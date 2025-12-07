"""
utils/html_generator.py
=======================
Génération dynamique de HTML pour l'affichage du chat avec Highlight.js
"""

import re
from typing import List, Dict
from .code_parser import CodeParser
from .css_generator import CSSGenerator
from core.logger import get_logger


class HTMLGenerator:
    """
    Générateur de HTML pour l'affichage des conversations.
    
    Fonctionnalités:
    - Rendu des messages user/assistant
    - Intégration Highlight.js pour coloration syntaxique
    - Boutons "Copier" sur les blocs de code
    - Ancres HTML pour scroll intelligent
    - CSS personnalisé selon préférences utilisateur
    - Support Markdown (titres, gras, italique, listes)
    """
    
    # Langages supportés par Highlight.js
    SUPPORTED_LANGUAGES = [
        'python', 'bash', 'perl', 'php', 'html', 'css',
        'powershell', 'java', 'json', 'javascript', 'sql',
        'cpp', 'c', 'csharp', 'ruby', 'go', 'rust'
    ]
    
    def __init__(self, css_generator: CSSGenerator = None):
        """
        Initialise le générateur HTML.
        
        Args:
            css_generator: Générateur de CSS personnalisé (optionnel)
        """
        self.logger = get_logger()
        self.code_parser = CodeParser()
        self.css_generator = css_generator or CSSGenerator()
    
    def generate_full_html(
        self,
        messages: List[Dict],
        custom_colors: Dict[str, str] = None
    ) -> str:
        """
        Génère le HTML complet pour une conversation.
        
        Args:
            messages: Liste de dicts {'role': str, 'content': str}
            custom_colors: Couleurs personnalisées (optionnel)
        
        Returns:
            HTML complet avec head et body
        """
        # Génération du CSS personnalisé
        custom_css = self.css_generator.generate_css(custom_colors) if custom_colors else ""
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat</title>
    
    <!-- Highlight.js CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    
    <!-- Langages supportés -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/perl.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/php.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/powershell.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/java.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
    
    <style>
        {self._get_base_css()}
        {custom_css}
    </style>
</head>
<body>
    <div class="chat-container">
        {self._generate_messages_html(messages)}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_messages_html(self, messages: List[Dict]) -> str:
        """
        Génère le HTML pour tous les messages.
        
        Args:
            messages: Liste de messages
        
        Returns:
            HTML des messages
        """
        html_parts = []
        
        # Trouver l'index du DERNIER message user
        last_user_idx = -1
        for idx in range(len(messages) - 1, -1, -1):
            if messages[idx]['role'] == 'user':
                last_user_idx = idx
                break
        
        self.logger.debug(f"[HTML_GEN] Dernier message user à l'index: {last_user_idx}")
        
        for idx, message in enumerate(messages):
            role = message['role']
            content = message['content']
            
            # ID d'ancre pour le dernier message user (pas le dernier message en général)
            anchor_id = ""
            if idx == last_user_idx and role == 'user':
                anchor_id = ' id="last-question"'
                self.logger.debug(f"[HTML_GEN] ✓ ANCRE #last-question ajoutée au message {idx} (user)")
            
            # Classe CSS selon le rôle
            message_class = f"message message-{role}"
            
            # Avatar/icône
            avatar = self._get_avatar(role)
            
            # Parse le contenu (détection code, markdown, etc.)
            parsed_content = self._parse_content(content)
            
            html_parts.append(f"""
                <div class="{message_class}"{anchor_id}>
                    <div class="message-avatar">{avatar}</div>
                    <div class="message-content">
                        {parsed_content}
                    </div>
                </div>
            """)
        
        self.logger.debug(f"[HTML_GEN] {len(messages)} message(s) générés au total")
        return "\n".join(html_parts)
    
    def _parse_content(self, content: str) -> str:
        """
        Parse le contenu pour détecter et formater le code et le markdown.
        
        Args:
            content: Contenu brut du message
        
        Returns:
            HTML formaté
        """
        # Détection des blocs de code
        parsed = self.code_parser.parse_content(content)
        
        html_parts = []
        
        for block in parsed:
            if block['type'] == 'text':
                # Texte normal - convertir markdown basique en HTML
                text = block['content']
                
                # Titres
                text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
                text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
                text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
                
                # Gras
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                
                # Italique
                text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
                
                # Code inline
                text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
                
                # Listes à puces
                text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
                text = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', text, flags=re.DOTALL)
                
                # Sauts de ligne
                text = text.replace('\n', '<br>')
                
                html_parts.append(f'<div class="text-block">{text}</div>')
            
            elif block['type'] == 'code':
                # Bloc de code avec syntaxe
                language = block['language']
                code = block['content']
                
                # Logging
                line_count = code.count('\n') + 1
                self.logger.debug(f"[PARSER] Bloc de code détecté: {language} ({line_count} lignes)")
                
                # Génération du bloc avec bouton copier
                html_parts.append(self._generate_code_block(code, language))
        
        return "\n".join(html_parts)
    
    def _generate_code_block(self, code: str, language: str) -> str:
        """
        Génère un bloc de code avec coloration et bouton copier.
        
        Args:
            code: Code source
            language: Langage de programmation
        
        Returns:
            HTML du bloc de code
        """
        # Échapper le HTML
        from html import escape
        escaped_code = escape(code)
        
        # Classe highlight.js
        lang_class = f"language-{language}" if language != 'plaintext' else ""
        
        return f"""
            <div class="code-block-wrapper">
                <div class="code-header">
                    <span class="code-language">{language}</span>
                    <button class="copy-button" onclick="copyCode(this)">📋 Copier</button>
                </div>
                <pre><code class="{lang_class}">{escaped_code}</code></pre>
            </div>
        """
    
    def _get_avatar(self, role: str) -> str:
        """Retourne l'avatar/icône selon le rôle."""
        avatars = {
            'user': '👤',
            'assistant': '🤖',
            'system': '⚙️'
        }
        return avatars.get(role, '❓')
    
    def _get_base_css(self) -> str:
        """Retourne le CSS de base pour le chat - THÈME SOMBRE."""
        return """
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background-color: #1e1e1e;
                color: #e0e0e0;
                line-height: 1.6;
            }
            
            .chat-container {
                max-width: 100%;
                padding: 20px;
            }
            
            .message {
                display: flex;
                flex-direction: column;
                margin-bottom: 20px;
                animation: fadeIn 0.3s ease-in;
                width: 100%;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message-avatar {
                font-size: 28px;
                margin-bottom: 8px;
                text-align: center;
            }
            
            .message-content {
                background: #252525;
                padding: 15px 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                border: 1px solid #3d3d3d;
                width: 100%;
            }
            
            .message-user .message-content {
                background: #1a3a1a;
                border: 1px solid #2d5f2d;
            }
            
            .message-assistant .message-content {
                background: #252525;
                border: 1px solid #3d3d3d;
            }
            
            .text-block {
                margin-bottom: 10px;
                color: #e0e0e0;
            }
            
            .text-block h1 {
                color: #4CAF50;
                font-size: 24px;
                margin: 20px 0 10px 0;
                border-bottom: 2px solid #3d3d3d;
                padding-bottom: 5px;
            }
            
            .text-block h2 {
                color: #4CAF50;
                font-size: 20px;
                margin: 18px 0 8px 0;
                border-bottom: 1px solid #3d3d3d;
                padding-bottom: 4px;
            }
            
            .text-block h3 {
                color: #66BB6A;
                font-size: 16px;
                margin: 15px 0 6px 0;
            }
            
            .text-block strong {
                color: #ffffff;
                font-weight: bold;
            }
            
            .text-block em {
                color: #b0b0b0;
                font-style: italic;
            }
            
            .text-block ul {
                margin: 10px 0;
                padding-left: 25px;
            }
            
            .text-block li {
                margin: 5px 0;
                color: #d0d0d0;
            }
            
            .inline-code {
                background-color: #2d2d2d;
                color: #4CAF50;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
            }
            
            .code-block-wrapper {
                margin: 15px 0;
                border-radius: 8px;
                overflow: hidden;
                background: #1e1e1e;
                border: 1px solid #3d3d3d;
            }
            
            .code-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: #2d2d2d;
                padding: 8px 15px;
                color: #b0b0b0;
                font-size: 12px;
                border-bottom: 1px solid #3d3d3d;
            }
            
            .code-language {
                font-weight: bold;
                text-transform: uppercase;
                color: #4CAF50;
            }
            
            .copy-button {
                background: #4caf50;
                color: white;
                border: none;
                padding: 5px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
                transition: background 0.2s;
            }
            
            .copy-button:hover {
                background: #45a049;
            }
            
            .copy-button.copied {
                background: #2196F3;
            }
            
            pre {
                margin: 0;
                overflow-x: auto;
                background: #1e1e1e;
            }
            
            code {
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.5;
            }
            
            html {
                scroll-behavior: smooth;
            }
            
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: #1e1e1e;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #4d4d4d;
                border-radius: 5px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #5d5d5d;
            }
        """
    
    def _get_javascript(self) -> str:
        """Retourne le JavaScript pour les fonctionnalités interactives."""
        return """
            // Initialisation Highlight.js
            document.addEventListener('DOMContentLoaded', function() {
                hljs.highlightAll();
            });
            
            // Fonction de copie du code - CORRIGÉE
            function copyCode(button) {
                try {
                    const wrapper = button.closest('.code-block-wrapper');
                    const codeElement = wrapper.querySelector('code');
                    const textToCopy = codeElement.textContent || codeElement.innerText;
                    
                    if (navigator.clipboard && navigator.clipboard.writeText) {
                        navigator.clipboard.writeText(textToCopy).then(function() {
                            const originalText = button.textContent;
                            button.textContent = '✓ Copié !';
                            button.classList.add('copied');
                            
                            setTimeout(function() {
                                button.textContent = originalText;
                                button.classList.remove('copied');
                            }, 2000);
                        }).catch(function(err) {
                            console.error('Erreur clipboard:', err);
                            fallbackCopy(textToCopy, button);
                        });
                    } else {
                        fallbackCopy(textToCopy, button);
                    }
                } catch (err) {
                    console.error('Erreur copie:', err);
                    button.textContent = '❌ Erreur';
                }
            }
            
            function fallbackCopy(text, button) {
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                document.body.appendChild(textArea);
                textArea.select();
                
                try {
                    const successful = document.execCommand('copy');
                    if (successful) {
                        const originalText = button.textContent;
                        button.textContent = '✓ Copié !';
                        button.classList.add('copied');
                        setTimeout(function() {
                            button.textContent = originalText;
                            button.classList.remove('copied');
                        }, 2000);
                    } else {
                        button.textContent = '❌ Erreur';
                    }
                } catch (err) {
                    button.textContent = '❌ Erreur';
                }
                
                document.body.removeChild(textArea);
            }
            
            window.addEventListener('load', function() {
                const lastQuestion = document.getElementById('last-question');
                if (lastQuestion) {
                    setTimeout(function() {
                        lastQuestion.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                }
            });
        """
    
    def update_html_with_new_message(
        self,
        current_html: str,
        new_message: Dict
    ) -> str:
        """
        Ajoute un nouveau message au HTML existant (pour streaming).
        
        Args:
            current_html: HTML actuel
            new_message: Nouveau message à ajouter
        
        Returns:
            HTML mis à jour
        """
        start_marker = '<div class="chat-container">'
        end_marker = '</div>\n    \n    <script>'
        
        start_idx = current_html.find(start_marker)
        end_idx = current_html.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            self.logger.debug("[HTML_GEN] Marqueurs non trouvés, génération complète")
            return current_html
        
        messages_html = current_html[start_idx + len(start_marker):end_idx]
        new_msg_html = self._generate_messages_html([new_message])
        updated_messages = messages_html + new_msg_html
        
        updated_html = (
            current_html[:start_idx + len(start_marker)] +
            updated_messages +
            current_html[end_idx:]
        )
        
        return updated_html

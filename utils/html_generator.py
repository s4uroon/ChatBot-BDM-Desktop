"""
utils/html_generator.py
=======================
Génération dynamique de HTML pour l'affichage du chat avec Highlight.js
"""

import re
import sys
import base64
import mimetypes
from typing import List, Dict
from pathlib import Path
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
        'python', 'bash', 'perl', 'php', 'xml',  # xml pour HTML/XML
        'powershell', 'java', 'json', 'javascript', 'sql',
        'cpp', 'c', 'csharp', 'ruby', 'go', 'rust'
    ]

    # Cache statique pour les fichiers Highlight.js (partagé entre instances)
    _hljs_cache = {
        'core_js': None,
        'languages_js': None,
        'theme_dark_css': None,
        'theme_light_css': None,
    }

    @staticmethod
    def _get_base_path() -> Path:
        """
        Retourne le chemin de base de l'application.
        Compatible avec PyInstaller (exécutable) et mode développement (script).
        """
        if getattr(sys, 'frozen', False):
            # Exécutable PyInstaller : fichiers extraits dans sys._MEIPASS
            return Path(sys._MEIPASS)
        else:
            # Script Python : chemin relatif depuis ce fichier
            return Path(__file__).parent.parent

    def __init__(self, css_generator: CSSGenerator = None, hljs_theme: str = 'dark'):
        """
        Initialise le générateur HTML.

        Args:
            css_generator: Générateur de CSS personnalisé (optionnel)
            hljs_theme: Thème Highlight.js ('light' ou 'dark')
        """
        self.logger = get_logger()
        self.code_parser = CodeParser()
        self.css_generator = css_generator or CSSGenerator()
        self.hljs_theme = hljs_theme
        self.assets_dir = self._get_base_path() / 'assets' / 'highlightjs'

        # Charger les fichiers en cache au premier accès
        self._ensure_cache_loaded()

    def _ensure_cache_loaded(self):
        """Charge les fichiers Highlight.js en cache s'ils ne le sont pas déjà."""
        if HTMLGenerator._hljs_cache['core_js'] is None:
            self.logger.debug("[HTML_GEN] Chargement du cache Highlight.js...")
            HTMLGenerator._hljs_cache['core_js'] = self._read_hljs_core()
            HTMLGenerator._hljs_cache['languages_js'] = self._read_hljs_languages()
            HTMLGenerator._hljs_cache['theme_dark_css'] = self._read_hljs_theme('dark')
            HTMLGenerator._hljs_cache['theme_light_css'] = self._read_hljs_theme('light')
            self.logger.debug("[HTML_GEN] Cache Highlight.js chargé")

    def _read_hljs_core(self) -> str:
        """Lit le fichier JavaScript core de Highlight.js depuis le disque."""
        try:
            js_file = self.assets_dir / 'highlight.min.js'
            if js_file.exists():
                return js_file.read_text(encoding='utf-8')
            else:
                self.logger.warning(f"[HTML_GEN] Fichier Highlight.js introuvable: {js_file}")
                return ""
        except Exception as e:
            self.logger.error(f"[HTML_GEN] Erreur lecture Highlight.js: {e}")
            return ""

    def _read_hljs_languages(self) -> str:
        """Lit tous les fichiers de langages depuis le disque."""
        languages_js = []
        languages_dir = self.assets_dir / 'languages'

        for lang in self.SUPPORTED_LANGUAGES:
            lang_file = languages_dir / f"{lang}.min.js"
            try:
                if lang_file.exists():
                    languages_js.append(lang_file.read_text(encoding='utf-8'))
                    self.logger.debug(f"[HTML_GEN] Langage chargé: {lang}")
                else:
                    self.logger.debug(f"[HTML_GEN] Langage non trouvé (ignoré): {lang}")
            except Exception as e:
                self.logger.error(f"[HTML_GEN] Erreur lecture langage {lang}: {e}")

        self.logger.debug(f"[HTML_GEN] Total langages chargés: {len(languages_js)}/{len(self.SUPPORTED_LANGUAGES)}")
        return "\n".join(languages_js)

    def _read_hljs_theme(self, theme: str) -> str:
        """Lit le CSS d'un thème Highlight.js depuis le disque."""
        try:
            theme_name = 'atom-one-light' if theme == 'light' else 'atom-one-dark'
            css_file = self.assets_dir / 'styles' / f"{theme_name}.min.css"

            if css_file.exists():
                return css_file.read_text(encoding='utf-8')
            else:
                self.logger.warning(f"[HTML_GEN] Thème CSS introuvable: {css_file}")
                return ""
        except Exception as e:
            self.logger.error(f"[HTML_GEN] Erreur lecture thème CSS: {e}")
            return ""

    def _get_hljs_core(self) -> str:
        """Retourne le JavaScript core depuis le cache."""
        return HTMLGenerator._hljs_cache['core_js'] or ""

    def _get_hljs_languages(self) -> str:
        """Retourne les langages depuis le cache."""
        return HTMLGenerator._hljs_cache['languages_js'] or ""

    def _get_hljs_theme_css(self) -> str:
        """Retourne le CSS du thème courant depuis le cache."""
        if self.hljs_theme == 'light':
            return HTMLGenerator._hljs_cache['theme_light_css'] or ""
        return HTMLGenerator._hljs_cache['theme_dark_css'] or ""

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

        # Récupérer les fichiers Highlight.js depuis le cache
        hljs_core_js = self._get_hljs_core()
        hljs_languages_js = self._get_hljs_languages()
        hljs_theme_css = self._get_hljs_theme_css()

        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat</title>

    <!-- Highlight.js (bundled locally) -->
    <style>
        {hljs_theme_css}
    </style>
    <script>
        {hljs_core_js}
    </script>

    <!-- Langages supportés (bundled locally) -->
    <script>
        {hljs_languages_js}
    </script>

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

                # Tableaux markdown (avant les autres transformations)
                text = self._parse_markdown_tables(text)

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

                # Listes à puces - grouper les éléments consécutifs
                def replace_list_block(match):
                    items = match.group(0)
                    # Convertir chaque ligne "- item" en "<li>item</li>"
                    list_items = re.sub(r'^- (.+)$', r'<li>\1</li>', items, flags=re.MULTILINE)
                    return f'<ul>{list_items}</ul>'

                # Trouver les blocs de listes consécutifs
                text = re.sub(r'(^- .+$(\n^- .+$)*)', replace_list_block, text, flags=re.MULTILINE)

                # Sauts de ligne (mais pas dans les listes ni les tableaux)
                text = re.sub(r'\n(?!</li>)(?!<li>)(?!</ul>)(?!<ul>)(?!</table>)(?!<t[hdr])(?!</t[hdr])', '<br>', text)

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

    def _parse_markdown_tables(self, text: str) -> str:
        """
        Détecte et convertit les tableaux markdown en HTML.

        Gère le format :
            | Header 1 | Header 2 |
            |----------|----------|
            | Cell 1   | Cell 2   |

        Supporte l'alignement :
            :--- (gauche), :---: (centre), ---: (droite)
        """
        lines = text.split('\n')
        result = []
        i = 0

        while i < len(lines):
            # Détecter le début d'un tableau : ligne avec pipes + ligne séparateur
            if (i + 1 < len(lines)
                    and '|' in lines[i]
                    and re.match(r'^\s*\|[\s:]*-+[\s:]*(\|[\s:]*-+[\s:]*)*\|?\s*$', lines[i + 1])):

                # Extraire les en-têtes
                header_cells = self._parse_table_row(lines[i])
                separator_cells = self._parse_table_row(lines[i + 1])

                # Déterminer l'alignement depuis la ligne séparateur
                alignments = []
                for sep in separator_cells:
                    sep = sep.strip()
                    if sep.startswith(':') and sep.endswith(':'):
                        alignments.append('center')
                    elif sep.endswith(':'):
                        alignments.append('right')
                    else:
                        alignments.append('left')

                # Construire le HTML du tableau
                table_html = '<table class="markdown-table">\n<thead>\n<tr>\n'
                for col_idx, cell in enumerate(header_cells):
                    align = alignments[col_idx] if col_idx < len(alignments) else 'left'
                    table_html += f'<th style="text-align:{align}">{cell.strip()}</th>\n'
                table_html += '</tr>\n</thead>\n<tbody>\n'

                # Avancer après le séparateur
                i += 2

                # Lire les lignes de données
                while i < len(lines) and '|' in lines[i]:
                    row_cells = self._parse_table_row(lines[i])
                    table_html += '<tr>\n'
                    for col_idx, cell in enumerate(row_cells):
                        align = alignments[col_idx] if col_idx < len(alignments) else 'left'
                        table_html += f'<td style="text-align:{align}">{cell.strip()}</td>\n'
                    # Compléter les cellules manquantes
                    for col_idx in range(len(row_cells), len(header_cells)):
                        table_html += '<td></td>\n'
                    table_html += '</tr>\n'
                    i += 1

                table_html += '</tbody>\n</table>'
                result.append(table_html)
            else:
                result.append(lines[i])
                i += 1

        return '\n'.join(result)

    @staticmethod
    def _parse_table_row(line: str) -> list:
        """Extrait les cellules d'une ligne de tableau markdown."""
        line = line.strip()
        # Retirer les pipes de début et fin
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|'):
            line = line[:-1]
        return line.split('|')
    
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
        """Retourne l'avatar/icône selon le rôle.

        Utilise des images si disponibles dans assets/avatars/,
        encodées en base64 pour compatibilité QWebEngineView.
        Sinon fallback vers emojis Unicode.
        """
        self.logger.debug(f"[HTML_GEN][AVATAR] Chargement avatar pour rôle: {role}")

        # Chemins des images d'avatar (compatible PyInstaller)
        base_path = self._get_base_path()
        avatar_dir = base_path / 'assets' / 'avatars'

        self.logger.debug(f"[HTML_GEN][AVATAR] Base path: {base_path}")
        self.logger.debug(f"[HTML_GEN][AVATAR] Avatar directory: {avatar_dir}")
        self.logger.debug(f"[HTML_GEN][AVATAR] Avatar directory exists: {avatar_dir.exists()}")

        if avatar_dir.exists():
            try:
                dir_contents = list(avatar_dir.iterdir())
                self.logger.debug(f"[HTML_GEN][AVATAR] Fichiers dans {avatar_dir}: {[f.name for f in dir_contents]}")
            except Exception as e:
                self.logger.debug(f"[HTML_GEN][AVATAR] Erreur listing directory: {e}")

        # Mapping rôle -> fichier image
        avatar_files = {
            'user': 'user.png',
            'assistant': 'assistant.png',
            'system': 'system.png'
        }

        # Emojis de fallback si image non trouvée
        emoji_fallback = {
            'user': '👤',
            'assistant': '🤖',
            'system': '⚙️'
        }

        # Vérifier si un fichier image existe pour ce rôle
        if role in avatar_files:
            avatar_filename = avatar_files[role]
            avatar_path = avatar_dir / avatar_filename

            self.logger.debug(f"[HTML_GEN][AVATAR] Recherche fichier: {avatar_filename}")
            self.logger.debug(f"[HTML_GEN][AVATAR] Chemin complet: {avatar_path}")
            self.logger.debug(f"[HTML_GEN][AVATAR] Fichier existe: {avatar_path.exists()}")

            if avatar_path.exists():
                self.logger.info(f"[HTML_GEN][AVATAR] ✓ Fichier trouvé: {avatar_path}")

                try:
                    # Vérifier les permissions
                    import os
                    is_readable = os.access(avatar_path, os.R_OK)
                    self.logger.debug(f"[HTML_GEN][AVATAR] Permissions lecture: {is_readable}")

                    # Vérifier la taille du fichier
                    file_size = avatar_path.stat().st_size
                    self.logger.debug(f"[HTML_GEN][AVATAR] Taille fichier: {file_size} octets")

                    if file_size == 0:
                        self.logger.warning(f"[HTML_GEN][AVATAR] ⚠ Fichier vide: {avatar_path}")
                        return emoji_fallback.get(role, '❓')

                    # Lire l'image et l'encoder en base64
                    self.logger.debug(f"[HTML_GEN][AVATAR] Lecture fichier...")
                    with open(avatar_path, 'rb') as img_file:
                        img_data = img_file.read()
                        self.logger.debug(f"[HTML_GEN][AVATAR] Données lues: {len(img_data)} octets")

                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        self.logger.debug(f"[HTML_GEN][AVATAR] Base64 encodé: {len(img_base64)} caractères")
                        self.logger.debug(f"[HTML_GEN][AVATAR] Base64 preview: {img_base64[:50]}...")

                    # Déterminer le type MIME de l'image
                    mime_type = mimetypes.guess_type(str(avatar_path))[0] or 'image/png'
                    self.logger.debug(f"[HTML_GEN][AVATAR] Type MIME détecté: {mime_type}")

                    # Retourner une balise <img> avec data URL (base64)
                    data_url = f'data:{mime_type};base64,{img_base64}'
                    html_tag = f'<img src="{data_url}" alt="{role}" class="avatar-img">'

                    self.logger.info(f"[HTML_GEN][AVATAR] ✓ Avatar {role} chargé avec succès (base64)")
                    self.logger.debug(f"[HTML_GEN][AVATAR] HTML tag length: {len(html_tag)} caractères")

                    return html_tag

                except PermissionError as e:
                    self.logger.error(f"[HTML_GEN][AVATAR] ✗ Erreur permissions pour {avatar_path}: {e}")
                except IOError as e:
                    self.logger.error(f"[HTML_GEN][AVATAR] ✗ Erreur I/O lecture {avatar_path}: {e}")
                except Exception as e:
                    self.logger.error(f"[HTML_GEN][AVATAR] ✗ Erreur chargement avatar {role}: {e}", exc_info=True)
            else:
                self.logger.info(f"[HTML_GEN][AVATAR] ✗ Fichier non trouvé: {avatar_path}, utilisation emoji fallback")
        else:
            self.logger.debug(f"[HTML_GEN][AVATAR] Rôle '{role}' non reconnu, utilisation emoji fallback")

        # Fallback vers emoji
        emoji = emoji_fallback.get(role, '❓')
        self.logger.debug(f"[HTML_GEN][AVATAR] Retour emoji: {emoji}")
        return emoji
    
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
                line-height: 1;
            }

            .message-avatar .avatar-img {
                width: 46px;
                height: 46px;
                object-fit: cover;
                display: inline-block;
                vertical-align: middle;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
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

            /* Indicateur de frappe */
            .typing-indicator {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 10px 0;
            }

            .typing-dot {
                width: 10px;
                height: 10px;
                background-color: #4CAF50;
                border-radius: 50%;
                animation: typing-bounce 1.4s infinite ease-in-out both;
            }

            .typing-dot:nth-child(1) {
                animation-delay: -0.32s;
            }

            .typing-dot:nth-child(2) {
                animation-delay: -0.16s;
            }

            @keyframes typing-bounce {
                0%, 80%, 100% {
                    transform: scale(0);
                    opacity: 0.5;
                }
                40% {
                    transform: scale(1);
                    opacity: 1;
                }
            }

            /* === TABLEAUX MARKDOWN === */
            .markdown-table {
                width: 100%;
                border-collapse: collapse;
                margin: 12px 0;
                font-size: 14px;
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #3d3d3d;
            }

            .markdown-table thead {
                background: #2d2d2d;
            }

            .markdown-table th {
                padding: 10px 14px;
                font-weight: bold;
                color: #4CAF50;
                border-bottom: 2px solid #4CAF50;
                border-right: 1px solid #3d3d3d;
                white-space: nowrap;
            }

            .markdown-table th:last-child {
                border-right: none;
            }

            .markdown-table td {
                padding: 8px 14px;
                border-bottom: 1px solid #333333;
                border-right: 1px solid #333333;
                color: #d0d0d0;
            }

            .markdown-table td:last-child {
                border-right: none;
            }

            .markdown-table tbody tr:nth-child(even) {
                background: #1e1e1e;
            }

            .markdown-table tbody tr:nth-child(odd) {
                background: #252525;
            }

            .markdown-table tbody tr:hover {
                background: #2a3a2a;
            }

            .markdown-table tbody tr:last-child td {
                border-bottom: none;
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

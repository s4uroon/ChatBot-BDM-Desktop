"""
ui/chat_widget.py
=================
Widget d'affichage du chat avec QWebEngineView
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QContextMenuEvent
from typing import List, Dict, Optional
from utils.html_generator import HTMLGenerator
from core.logger import get_logger


class CustomWebEngineView(QWebEngineView):
    """QWebEngineView avec menu contextuel personnalisé."""
    
    export_requested = pyqtSignal()
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """Crée un menu contextuel personnalisé."""
        menu = QMenu(self)
        
        # Action standard : Copier
        copy_action = menu.addAction("📋 Copy")
        copy_action.triggered.connect(lambda: self.page().triggerAction(self.page().WebAction.Copy))
        
        # Action standard : Sélectionner tout
        select_all_action = menu.addAction("✓ Select All")
        select_all_action.triggered.connect(lambda: self.page().triggerAction(self.page().WebAction.SelectAll))
        
        menu.addSeparator()
        
        # Action personnalisée : Export session
        export_action = menu.addAction("💾 Export Current Session")
        export_action.triggered.connect(self.export_requested.emit)
        
        menu.exec(event.globalPos())


class ChatWidget(QWidget):
    """
    Widget d'affichage du chat avec QWebEngineView.
    
    Fonctionnalités:
    - Affichage HTML des messages
    - Coloration syntaxique (Highlight.js)
    - Scroll intelligent
    - Boutons copier sur les blocs de code
    - Menu contextuel personnalisé
    """
    
    # Signal pour demander l'export de la session courante
    export_current_session = pyqtSignal()
    
    def __init__(self, parent=None, hljs_theme: str = 'dark'):
        super().__init__(parent)
        self.logger = get_logger()

        # Générateurs
        self.hljs_theme = hljs_theme
        self.html_generator = HTMLGenerator(hljs_theme=hljs_theme)
        self.custom_colors = None

        # Messages actuels
        self.current_messages: List[Dict] = []

        # Flag pour savoir si on doit scroller
        self.should_scroll_to_question = False

        # Limite d'affichage pour optimisation (peut être modifié via set_max_displayed_messages)
        self.max_displayed_messages = 100

        # Protection contre les race conditions de rendu
        self._render_version = 0
        self._pending_render = False

        self.setup_ui()
        self.load_empty_page()
    
    def setup_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # WebEngine View personnalisée avec menu contextuel
        self.web_view = CustomWebEngineView()
        self.web_view.export_requested.connect(self.export_current_session.emit)
        self.web_view.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #1e1e1e;
            }
        """)
        
        layout.addWidget(self.web_view)
    
    def load_empty_page(self):
        """Charge une page vide au démarrage - THÈME SOMBRE."""
        empty_html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #1a3a1a 0%, #2d2d2d 100%);
            color: #e0e0e0;
        }
        .welcome {
            text-align: center;
            animation: fadeIn 1s ease-in;
        }
        .welcome h1 {
            font-size: 48px;
            margin-bottom: 20px;
            color: #4CAF50;
            text-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
        }
        .welcome p {
            font-size: 18px;
            opacity: 0.9;
            color: #b0b0b0;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="welcome">
        <h1>🤖 ChatBot BDM Desktop</h1>
        <p>Commencez une nouvelle conversation ou sélectionnez une conversation existante</p>
    </div>
</body>
</html>
        """
        self.web_view.setHtml(empty_html)
        self.logger.debug("[CHAT_WIDGET] Page vide chargée")
    
    def append_message(self, role: str, content: str):
        """
        Ajoute un nouveau message à la conversation affichée.

        Args:
            role: 'user' ou 'assistant'
            content: Contenu du message
        """
        self.logger.debug(f"[CHAT_WIDGET] ===== append_message() APPELÉ =====")
        self.logger.debug(f"[CHAT_WIDGET] Role: {role}, Longueur contenu: {len(content)}")
        self.logger.debug(f"[CHAT_WIDGET] Messages actuels avant ajout: {len(self.current_messages)}")

        # Si c'est un message assistant et qu'il y a déjà un message "loading", le remplacer
        if role == 'assistant' and self.current_messages and self.current_messages[-1]['role'] == 'assistant':
            if '⏳' in self.current_messages[-1]['content']:
                self.logger.debug("[CHAT_WIDGET] → Remplacement du message loading")
                # Remplacer le message loading
                self.current_messages[-1] = {'role': role, 'content': content}
                self.should_scroll_to_question = True  # Activer le scroll vers la question
                self.logger.debug(f"[CHAT_WIDGET] → should_scroll_to_question mis à True")
                self._render_html()
                self.logger.debug(f"[CHAT_WIDGET] Message loading remplacé par réponse finale")
                return

        # Vérification anti-duplication : bloquer uniquement les duplications IMMÉDIATES (race conditions)
        # Ne pas bloquer les questions légitimes identiques posées à des moments différents
        if self.current_messages:
            last_msg = self.current_messages[-1]

            # Bloquer seulement si le dernier message a le même role ET le même contenu
            # (indique une race condition, pas une question légitime)
            if last_msg['role'] == role and last_msg['content'] == content:
                # Exception : ne pas bloquer les typing indicators (ils peuvent être multiples)
                if 'typing-indicator' in content:
                    self.logger.debug(f"[CHAT_WIDGET] Typing indicator multiple détecté (autorisé)")
                else:
                    self.logger.warning(f"[CHAT_WIDGET] ⚠️ DUPLICATION IMMÉDIATE DÉTECTÉE - Message ignoré (role: {role})")
                    return

        self.logger.debug("[CHAT_WIDGET] → Ajout d'un nouveau message")
        message = {'role': role, 'content': content}
        self.current_messages.append(message)

        # Si c'est un message user, ne PAS scroller automatiquement
        if role == 'user':
            self.logger.debug("[CHAT_WIDGET] → Message user, should_scroll_to_question = False")
            self.should_scroll_to_question = False

        self._render_html()
        self.logger.debug(f"[CHAT_WIDGET] Message ajouté, total: {len(self.current_messages)}")
    
    def update_last_message(self, content: str):
        """
        Met à jour le contenu du dernier message (pour le streaming).
        
        Args:
            content: Nouveau contenu
        """
        if self.current_messages:
            self.current_messages[-1]['content'] = content
            self._render_html()
    
    def load_conversation(self, messages: List[Dict]):
        """
        Charge une conversation complète.

        Args:
            messages: Liste de messages à afficher
        """
        self.current_messages = messages
        self.should_scroll_to_question = False  # Ne pas scroller lors du chargement
        self._render_version = 0  # Réinitialiser le compteur de version
        self._render_html()
        self.logger.debug(f"[CHAT_WIDGET] Conversation chargée: {len(messages)} messages")
    
    def clear_conversation(self):
        """Efface la conversation affichée."""
        self.current_messages = []
        self.should_scroll_to_question = False
        self.load_empty_page()
        self.logger.debug("[CHAT_WIDGET] Conversation effacée")

    def show_typing_indicator(self):
        """Affiche un indicateur de frappe animé."""
        self.logger.debug("[CHAT_WIDGET] Affichage de l'indicateur de frappe")
        typing_html = """
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """
        self.append_message('assistant', typing_html)

    def hide_typing_indicator(self):
        """Cache l'indicateur de frappe en retirant le dernier message s'il contient l'indicateur."""
        self.logger.debug("[CHAT_WIDGET] hide_typing_indicator() appelé")
        self.logger.debug(f"[CHAT_WIDGET] Nombre de messages actuels: {len(self.current_messages)}")

        if not self.current_messages:
            self.logger.warning("[CHAT_WIDGET] ⚠️ Aucun message dans la liste")
            return

        # Chercher l'indicateur de frappe dans les derniers messages (max 3)
        # Parcourir de la fin vers le début, mais limité aux 3 derniers
        removed = False
        for i in range(len(self.current_messages) - 1, max(-1, len(self.current_messages) - 4), -1):
            msg = self.current_messages[i]
            content = msg.get('content', '')

            # Vérifier si c'est un typing indicator
            if msg.get('role') == 'assistant' and 'typing-indicator' in content:
                self.logger.debug(f"[CHAT_WIDGET] Retrait de l'indicateur de frappe à l'index {i}")
                self.logger.debug(f"[CHAT_WIDGET] Contenu retiré: {content[:50]}...")
                self.current_messages.pop(i)
                removed = True
                break  # Retirer seulement le premier trouvé

        if removed:
            self.logger.debug(f"[CHAT_WIDGET] Indicateur de frappe retiré, messages restants: {len(self.current_messages)}")
            self._render_html()
        else:
            self.logger.warning("[CHAT_WIDGET] ⚠️ Aucun indicateur de frappe trouvé dans les 3 derniers messages")

    def set_max_displayed_messages(self, count: int):
        """
        Définit le nombre maximum de messages affichés pour optimiser les performances.

        Args:
            count: Nombre maximum de messages (défaut: 100)
        """
        self.max_displayed_messages = max(10, count)  # Minimum 10 messages
        self.logger.debug(f"[CHAT_WIDGET] Limite d'affichage: {self.max_displayed_messages} messages")
    
    def _render_html(self):
        """Génère et affiche le HTML de la conversation SANS scroller automatiquement."""
        # Incrémenter la version de rendu pour invalider les anciens callbacks
        self._render_version += 1
        current_version = self._render_version

        self.logger.debug(f"[CHAT_WIDGET] ===== _render_html() APPELÉ (version {current_version}) =====")
        self.logger.debug(f"[CHAT_WIDGET] Nombre de messages: {len(self.current_messages)}")
        self.logger.debug(f"[CHAT_WIDGET] should_scroll_to_question: {self.should_scroll_to_question}")

        # Optimisation: ne rendre que les N derniers messages si la conversation est longue
        messages_to_render = self.current_messages
        if len(self.current_messages) > self.max_displayed_messages:
            messages_to_render = self.current_messages[-self.max_displayed_messages:]
            self.logger.debug(
                f"[CHAT_WIDGET] Optimisation: affichage des {self.max_displayed_messages} derniers messages "
                f"sur {len(self.current_messages)} total"
            )

        html = self.html_generator.generate_full_html(
            messages_to_render,
            self.custom_colors
        )

        self.logger.debug(f"[CHAT_WIDGET] HTML généré, taille: {len(html)} caractères")

        # Si on a au moins un message
        if len(self.current_messages) > 0:
            # Si on doit scroller vers la question, on charge le HTML et on scrollera après
            if self.should_scroll_to_question:
                self.logger.debug("[CHAT_WIDGET] ✓ Mode SCROLL VERS QUESTION activé")
                self.web_view.setHtml(html)
                self.logger.debug("[CHAT_WIDGET] HTML chargé, programmation du scroll dans 300ms")
                # Scroller après le chargement avec un délai
                QTimer.singleShot(300, lambda: self._do_scroll_to_question())
                self.should_scroll_to_question = False
            else:
                # Sinon, sauvegarder et restaurer la position
                self.logger.debug("[CHAT_WIDGET] Mode PRÉSERVATION scroll activé")
                js_get_scroll = "window.pageYOffset || document.documentElement.scrollTop"

                def callback(scroll_pos):
                    # Vérifier que ce callback correspond toujours à la dernière version
                    if current_version != self._render_version:
                        self.logger.debug(f"[CHAT_WIDGET] ⚠️ Callback obsolète ignoré (v{current_version} vs v{self._render_version})")
                        return

                    self.logger.debug(f"[CHAT_WIDGET] Position scroll sauvegardée: {scroll_pos}")
                    self.web_view.setHtml(html)
                    self.logger.debug("[CHAT_WIDGET] HTML rechargé")
                    # Restaurer la position
                    if scroll_pos and scroll_pos > 0:
                        self.logger.debug(f"[CHAT_WIDGET] Restauration du scroll à {scroll_pos} dans 100ms")
                        QTimer.singleShot(100, lambda: self._restore_scroll(scroll_pos))
                    else:
                        self.logger.debug("[CHAT_WIDGET] Pas de restauration (position = 0 ou None)")

                self.web_view.page().runJavaScript(js_get_scroll, callback)
        else:
            # Pas de messages, juste charger
            self.logger.debug("[CHAT_WIDGET] Pas de messages, chargement HTML simple")
            self.web_view.setHtml(html)

        self.logger.debug(f"[CHAT_WIDGET] ===== _render_html() TERMINÉ (version {current_version}) =====")
    
    def _do_scroll_to_question(self):
        """Execute le scroll vers la dernière question."""
        self.logger.debug("[CHAT_WIDGET] ===== _do_scroll_to_question() APPELÉ =====")
        self.scroll_to_last_question()
    
    def _restore_scroll(self, position):
        """Restaure la position de scroll."""
        self.logger.debug(f"[CHAT_WIDGET] _restore_scroll() appelé avec position={position}")
        js_code = f"window.scrollTo(0, {position});"
        self.web_view.page().runJavaScript(js_code)
        self.logger.debug(f"[CHAT_WIDGET] Commande JavaScript de restauration envoyée")
    
    def scroll_to_last_question(self):
        """Scroll vers la dernière question (ancre #last-question) avec debug amélioré."""
        self.logger.debug("[CHAT_WIDGET] ===== TENTATIVE DE SCROLL =====")
        
        js_code = """
            (function() {
                console.log('=== DEBUT SCROLL JAVASCRIPT ===');
                const lastQuestion = document.getElementById('last-question');
                console.log('Element last-question trouvé:', lastQuestion);
                
                if (lastQuestion) {
                    console.log('Position de l\'élément:', lastQuestion.offsetTop);
                    console.log('Scrolling vers last-question...');
                    lastQuestion.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    console.log('scrollIntoView() appelé');
                    return 'SUCCESS: Element found and scrolled';
                } else {
                    console.log('ERREUR: Element last-question NOT FOUND');
                    console.log('Elements avec id dans le DOM:');
                    const allIds = Array.from(document.querySelectorAll('[id]')).map(el => el.id);
                    console.log('IDs trouvés:', allIds);
                    return 'ERROR: Element not found';
                }
            })();
        """
        
        def scroll_callback(result):
            self.logger.debug(f"[CHAT_WIDGET] Résultat JavaScript: {result}")
        
        self.web_view.page().runJavaScript(js_code, scroll_callback)
        self.logger.debug("[CHAT_WIDGET] Code JavaScript de scroll envoyé")
    
    def scroll_to_bottom(self):
        """Scroll vers le bas de la page."""
        js_code = "window.scrollTo(0, document.body.scrollHeight);"
        self.web_view.page().runJavaScript(js_code)
    
    def set_custom_colors(self, colors: Dict[str, str]):
        """
        Définit les couleurs personnalisées pour la coloration syntaxique.

        Args:
            colors: Dictionnaire de couleurs
        """
        self.custom_colors = colors
        if self.current_messages:
            self._render_html()

    def set_hljs_theme(self, theme: str):
        """
        Change le thème Highlight.js (light/dark).

        Args:
            theme: 'light' ou 'dark'
        """
        if theme not in ['light', 'dark']:
            self.logger.warning(f"[CHAT_WIDGET] Thème invalide: {theme}, utilisation de 'dark'")
            theme = 'dark'

        self.hljs_theme = theme
        self.html_generator = HTMLGenerator(hljs_theme=theme)
        self.logger.debug(f"[CHAT_WIDGET] Thème Highlight.js changé: {theme}")

        # Re-render si il y a des messages
        if self.current_messages:
            self._render_html()

    def export_to_html(self, filepath: str) -> bool:
        """
        Exporte la conversation en HTML.
        
        Args:
            filepath: Chemin du fichier de sortie
        
        Returns:
            True si succès
        """
        try:
            html = self.html_generator.generate_full_html(
                self.current_messages,
                self.custom_colors
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            self.logger.debug(f"[CHAT_WIDGET] Export HTML vers {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"[CHAT_WIDGET] Erreur export HTML", exc_info=True)
            return False

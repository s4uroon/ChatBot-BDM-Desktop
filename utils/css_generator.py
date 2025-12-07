"""
utils/css_generator.py
======================
Générateur de CSS personnalisé pour la coloration syntaxique
"""

from typing import Dict, Optional
from core.logger import get_logger


class CSSGenerator:
    """
    Générateur de CSS personnalisé pour Highlight.js.
    
    Permet de personnaliser les couleurs de la coloration syntaxique
    selon les préférences utilisateur.
    """
    
    # Mapping entre types de tokens et classes CSS Highlight.js
    TOKEN_CLASSES = {
        'comment': ['.hljs-comment', '.hljs-quote'],
        'keyword': ['.hljs-keyword', '.hljs-selector-tag', '.hljs-built_in'],
        'string': ['.hljs-string', '.hljs-title', '.hljs-section'],
        'number': ['.hljs-number', '.hljs-literal'],
        'function': ['.hljs-function', '.hljs-title.function_', '.hljs-params'],
    }
    
    # Couleurs par défaut (Atom One Dark theme)
    DEFAULT_COLORS = {
        'comment': '#6a9955',
        'keyword': '#569cd6',
        'string': '#ce9178',
        'number': '#b5cea8',
        'function': '#dcdcaa',
    }
    
    def __init__(self):
        self.logger = get_logger()
    
    def generate_css(self, custom_colors: Optional[Dict[str, str]] = None) -> str:
        """
        Génère le CSS personnalisé pour la coloration syntaxique.
        
        Args:
            custom_colors: Dict {'comment': '#xxx', 'keyword': '#xxx', ...}
        
        Returns:
            CSS string
        """
        # Fusionner les couleurs par défaut avec les personnalisées
        colors = self.DEFAULT_COLORS.copy()
        if custom_colors:
            colors.update(custom_colors)
        
        css_rules = []
        
        # Générer les règles CSS pour chaque type de token
        for token_type, color in colors.items():
            if token_type in self.TOKEN_CLASSES:
                classes = self.TOKEN_CLASSES[token_type]
                selector = ', '.join(classes)
                css_rules.append(f"{selector} {{ color: {color} !important; }}")
        
        css = "\n".join(css_rules)
        self.logger.debug(f"[CSS_GEN] CSS personnalisé généré avec {len(colors)} couleurs")
        
        return css
    
    def generate_preview_css(self, colors: Dict[str, str]) -> str:
        """
        Génère un CSS pour la prévisualisation dans les paramètres - THÈME SOMBRE.
        
        Args:
            colors: Dict de couleurs
        
        Returns:
            CSS pour preview
        """
        preview_css = f"""
            .preview-container {{
                background: #1e1e1e;
                padding: 20px;
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                line-height: 1.6;
                border: 1px solid #3d3d3d;
            }}
            
            .preview-comment {{ color: {colors.get('comment', '#6a9955')}; }}
            .preview-keyword {{ color: {colors.get('keyword', '#569cd6')}; font-weight: bold; }}
            .preview-string {{ color: {colors.get('string', '#ce9178')}; }}
            .preview-number {{ color: {colors.get('number', '#b5cea8')}; }}
            .preview-function {{ color: {colors.get('function', '#dcdcaa')}; }}
            .preview-text {{ color: #d4d4d4; }}
        """
        
        return preview_css
    
    def get_preview_html(self, colors: Dict[str, str]) -> str:
        """
        Génère un HTML de prévisualisation des couleurs.
        
        Args:
            colors: Dict de couleurs
        
        Returns:
            HTML pour preview
        """
        css = self.generate_preview_css(colors)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>{css}</style>
</head>
<body>
    <div class="preview-container">
        <div>
            <span class="preview-comment"># Ceci est un commentaire</span>
        </div>
        <div>
            <span class="preview-keyword">def</span>
            <span class="preview-function"> calculate_sum</span>
            <span class="preview-text">(a, b):</span>
        </div>
        <div>
            <span class="preview-text">    </span>
            <span class="preview-string">"Calcule la somme de deux nombres"</span>
        </div>
        <div>
            <span class="preview-text">    result = a + b + </span>
            <span class="preview-number">42</span>
        </div>
        <div>
            <span class="preview-text">    </span>
            <span class="preview-keyword">return</span>
            <span class="preview-text"> result</span>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def validate_color(self, color: str) -> bool:
        """
        Valide un code couleur hexadécimal.
        
        Args:
            color: Code couleur (ex: '#ff5733' ou 'ff5733')
        
        Returns:
            True si valide
        """
        if not color:
            return False
        
        # Ajouter # si manquant
        if not color.startswith('#'):
            color = '#' + color
        
        # Vérifier le format hex
        if len(color) != 7:
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def normalize_color(self, color: str) -> str:
        """
        Normalise un code couleur.
        
        Args:
            color: Code couleur
        
        Returns:
            Code couleur normalisé avec #
        """
        if not color:
            return '#000000'
        
        color = color.strip()
        
        if not color.startswith('#'):
            color = '#' + color
        
        return color.lower()
    
    def get_contrasting_color(self, hex_color: str) -> str:
        """
        Retourne une couleur contrastante (noir ou blanc) pour un fond.
        Utile pour les boutons ou labels.
        
        Args:
            hex_color: Couleur de fond en hex
        
        Returns:
            '#ffffff' ou '#000000'
        """
        # Retirer le #
        hex_color = hex_color.lstrip('#')
        
        # Convertir en RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Calculer la luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Retourner noir ou blanc selon la luminance
        return '#000000' if luminance > 0.5 else '#ffffff'
    
    def export_theme(self, colors: Dict[str, str], theme_name: str) -> Dict:
        """
        Exporte un thème de couleurs.
        
        Args:
            colors: Dict de couleurs
            theme_name: Nom du thème
        
        Returns:
            Dict du thème avec métadonnées
        """
        theme = {
            'name': theme_name,
            'version': '1.0',
            'colors': colors,
            'css': self.generate_css(colors)
        }
        
        self.logger.debug(f"[CSS_GEN] Thème '{theme_name}' exporté")
        return theme
    
    def import_theme(self, theme_dict: Dict) -> Dict[str, str]:
        """
        Importe un thème de couleurs.
        
        Args:
            theme_dict: Dict du thème
        
        Returns:
            Dict de couleurs
        """
        colors = theme_dict.get('colors', {})
        
        # Valider les couleurs
        validated_colors = {}
        for key, color in colors.items():
            if self.validate_color(color):
                validated_colors[key] = self.normalize_color(color)
            else:
                self.logger.debug(f"[CSS_GEN] Couleur invalide ignorée: {key}={color}")
        
        self.logger.debug(f"[CSS_GEN] Thème importé: {len(validated_colors)} couleurs")
        return validated_colors

"""
utils/code_parser.py
====================
Détection et parsing des blocs de code dans les messages
"""

import re
from typing import List, Dict
from core.logger import get_logger


class CodeParser:
    """
    Parser pour détecter les blocs de code dans le texte.
    
    Détecte les formats:
    - Blocs fencés Markdown: ```language\ncode\n```
    - Blocs inline: `code`
    """
    
    # Pattern pour blocs de code fencés (```language\ncode\n```)
    FENCE_PATTERN = re.compile(
        r'```(\w+)?\n(.*?)```',
        re.DOTALL
    )
    
    # Langages supportés (correspondance entre alias et noms standards)
    LANGUAGE_ALIASES = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'sh': 'bash',
        'shell': 'bash',
        'ps1': 'powershell',
        'rb': 'ruby',
        'rs': 'rust',
        'yml': 'yaml',
        'md': 'markdown',
    }
    
    def __init__(self):
        self.logger = get_logger()
    
    def parse_content(self, content: str) -> List[Dict]:
        """
        Parse le contenu et identifie les blocs de texte et de code.
        
        Args:
            content: Contenu brut du message
        
        Returns:
            Liste de dicts {'type': 'text'|'code', 'content': str, 'language': str}
        """
        blocks = []
        last_pos = 0
        
        # Recherche de tous les blocs de code
        for match in self.FENCE_PATTERN.finditer(content):
            start, end = match.span()
            
            # Texte avant le bloc de code
            if start > last_pos:
                text_content = content[last_pos:start].strip()
                if text_content:
                    blocks.append({
                        'type': 'text',
                        'content': text_content,
                        'language': None
                    })
            
            # Bloc de code
            language = match.group(1) or 'plaintext'
            code_content = match.group(2)
            
            # Normaliser le langage
            language = self._normalize_language(language)
            
            blocks.append({
                'type': 'code',
                'content': code_content,
                'language': language
            })
            
            last_pos = end
        
        # Texte restant après le dernier bloc
        if last_pos < len(content):
            text_content = content[last_pos:].strip()
            if text_content:
                blocks.append({
                    'type': 'text',
                    'content': text_content,
                    'language': None
                })
        
        # Si aucun bloc détecté, tout est du texte
        if not blocks:
            blocks.append({
                'type': 'text',
                'content': content,
                'language': None
            })
        
        self.logger.debug(f"[PARSER] {len(blocks)} bloc(s) détecté(s)")
        return blocks
    
    def _normalize_language(self, language: str) -> str:
        """
        Normalise le nom du langage.
        
        Args:
            language: Nom du langage (potentiellement alias)
        
        Returns:
            Nom normalisé
        """
        language = language.lower().strip()
        
        # Vérifier les alias
        if language in self.LANGUAGE_ALIASES:
            return self.LANGUAGE_ALIASES[language]
        
        return language
    
    def detect_language_from_content(self, code: str) -> str:
        """
        Tente de détecter le langage automatiquement depuis le contenu.
        (Heuristique simple basée sur des patterns)
        
        Args:
            code: Code source
        
        Returns:
            Langage détecté ou 'plaintext'
        """
        code = code.strip()
        
        # Python
        if any(keyword in code for keyword in ['def ', 'import ', 'class ', 'print(', 'if __name__']):
            return 'python'
        
        # JavaScript
        if any(keyword in code for keyword in ['function ', 'const ', 'let ', 'var ', '=>', 'console.log']):
            return 'javascript'
        
        # Bash
        if code.startswith('#!') or any(keyword in code for keyword in ['#!/bin/bash', 'echo ', 'export ']):
            return 'bash'
        
        # HTML
        if '<html' in code.lower() or '<!doctype' in code.lower():
            return 'html'
        
        # JSON
        if code.startswith('{') and code.endswith('}'):
            try:
                import json
                json.loads(code)
                return 'json'
            except:
                pass
        
        # SQL
        if any(keyword in code.upper() for keyword in ['SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE TABLE']):
            return 'sql'
        
        # Défaut
        return 'plaintext'
    
    def extract_code_blocks(self, content: str) -> List[Dict]:
        """
        Extrait uniquement les blocs de code (pas le texte).
        
        Args:
            content: Contenu du message
        
        Returns:
            Liste de blocs de code
        """
        blocks = self.parse_content(content)
        return [block for block in blocks if block['type'] == 'code']
    
    def count_code_blocks(self, content: str) -> int:
        """
        Compte le nombre de blocs de code dans le contenu.
        
        Args:
            content: Contenu du message
        
        Returns:
            Nombre de blocs de code
        """
        return len(self.extract_code_blocks(content))
    
    def get_languages_used(self, content: str) -> List[str]:
        """
        Retourne la liste des langages utilisés dans le contenu.
        
        Args:
            content: Contenu du message
        
        Returns:
            Liste de langages (unique)
        """
        code_blocks = self.extract_code_blocks(content)
        languages = [block['language'] for block in code_blocks]
        return list(set(languages))

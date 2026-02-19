"""
utils/logo_utils.py
===================
Utilitaire de chargement du logo de l'application (encodage base64)
"""

import os
import base64
from core.logger import get_logger

# Cache du logo en base64 pour éviter les lectures disque répétées
_logo_cache: str = ""


def get_logo_base64() -> str:
    """
    Retourne le logo de l'application encodé en base64 (data URI).
    Le résultat est mis en cache après le premier chargement.

    Returns:
        str: Data URI du logo ou chaîne vide si erreur
    """
    global _logo_cache
    if _logo_cache:
        return _logo_cache

    logger = get_logger()
    try:
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'assets', 'ChatBot_BDM_Desktop_256.png'
        )
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode('utf-8')
            _logo_cache = f"data:image/png;base64,{logo_data}"
            return _logo_cache
    except Exception as e:
        logger.warning(f"[LOGO] Impossible de charger le logo: {e}")
        return ""

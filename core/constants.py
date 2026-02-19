"""
core/constants.py
=================
Constantes globales de l'application
"""

# Informations de l'application
APP_NAME = "ChatBot BDM Desktop"
APP_VERSION = "2.1.0"
APP_ORGANIZATION = "ChatbotBDM"
APP_ID = f"ChatbotBDM.ChatBotBDMDesktop.{APP_VERSION}"
APP_CREATOR = "Gwendal CHAIGNEAU BOEZENNEC"

# Limites
MAX_INPUT_CHARS = 1000000
DEFAULT_MAX_DISPLAYED_MESSAGES = 100

# Timeouts (en secondes)
API_TIMEOUT = 60.0
API_CONNECT_TIMEOUT = 10.0
WORKER_WAIT_TIMEOUT_MS = 10000  # 10 secondes pour attendre la fin du worker

# Valeurs par défaut API
DEFAULT_API_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4"
DEFAULT_TEMPERATURE = 0.7

# Titre de conversation
AUTO_TITLE_MAX_LENGTH = 50
AUTO_TITLE_PROMPT = (
    "Generate a short title (maximum 8 words) in the same language as the user message "
    "that summarizes the following message. Reply ONLY with the title, nothing else:\n\n"
)

"""
core/api_client.py
==================
Client OpenAI avec désactivation SSL pour serveurs auto-signés
"""

import httpx
from openai import OpenAI
from typing import Optional, Iterator
from .logger import get_logger


class APIClient:
    """
    Client OpenAI configuré avec bypass SSL pour environnements entreprise.
    Support du streaming pour réponses progressives.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4",
        verify_ssl: bool = False
    ):
        """
        Initialise le client OpenAI avec configuration SSL personnalisée.
        
        Args:
            api_key: Clé API OpenAI
            base_url: URL de base de l'API (support serveurs locaux)
            model: Modèle à utiliser par défaut
            verify_ssl: Vérification SSL (False pour certificats auto-signés)
        """
        self.logger = get_logger()
        self.model = model
        self.base_url = base_url
        
        # Configuration du client HTTP avec bypass SSL
        # CRITIQUE: verify=False permet l'usage de certificats auto-signés
        http_client = httpx.Client(
            verify=verify_ssl,
            timeout=httpx.Timeout(60.0, connect=10.0)
        )
        
        # Initialisation du client OpenAI avec transport personnalisé
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )
        
        self.logger.debug(f"[API_CLIENT] Initialisé - URL: {base_url}, SSL verify: {verify_ssl}")
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test la connexion à l'API.
        
        Returns:
            (success: bool, message: str)
        """
        try:
            self.logger.debug("[API_CLIENT] Test de connexion...")
            
            # Test simple avec une requête minimale
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            self.logger.debug("[API_CLIENT] Test réussi")
            return True, "Connexion établie avec succès"
            
        except Exception as e:
            error_msg = f"Échec de connexion: {str(e)}"
            self.logger.error(f"[API_CLIENT] {error_msg}", exc_info=True)
            return False, error_msg
    
    def chat_completion_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """
        Requête streaming pour réponses progressives.
        
        Args:
            messages: Liste des messages du contexte
            temperature: Créativité du modèle (0-2)
            max_tokens: Limite de tokens (None = pas de limite)
        
        Yields:
            Fragments de texte au fur et à mesure
        """
        try:
            self.logger.debug(f"[API] Démarrage requête vers modèle '{self.model}' ({len(messages)} messages)")
            
            # Requête streaming
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            chunk_count = 0
            for chunk in stream:
                # Vérifier que le chunk a des choices et du contenu
                if not chunk.choices or len(chunk.choices) == 0:
                    continue
                
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    chunk_count += 1
                    
                    # Log des chunks en mode debug
                    if chunk_count % 10 == 0:  # Log tous les 10 chunks
                        self.logger.debug(f"[API] Chunk #{chunk_count} reçu")
                    
                    yield content
            
            self.logger.debug(f"[API_CLIENT] Stream terminé: {chunk_count} chunks")
            
        except Exception as e:
            self.logger.error(f"[API] Erreur durant le streaming", exc_info=True)
            yield f"\n\n[ERREUR] {str(e)}"
    
    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Requête standard (non-streaming) pour tests rapides.
        
        Args:
            messages: Liste des messages du contexte
            temperature: Créativité du modèle
            max_tokens: Limite de tokens
        
        Returns:
            Réponse complète ou None en cas d'erreur
        """
        try:
            self.logger.debug(f"[API] Démarrage requête vers modèle '{self.model}' ({len(messages)} messages)")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            self.logger.debug(f"[API_CLIENT] Réponse reçue: {len(content)} caractères")
            
            return content
            
        except Exception as e:
            self.logger.error(f"[API] Erreur durant la requête API", exc_info=True)
            return None
    
    def update_model(self, model: str) -> None:
        """Met à jour le modèle utilisé."""
        self.model = model
        self.logger.debug(f"[API_CLIENT] Modèle changé: {model}")
    
    def close(self) -> None:
        """Ferme proprement le client HTTP."""
        try:
            if hasattr(self.client, '_client'):
                self.client._client.close()
            self.logger.debug("[API_CLIENT] Client fermé")
        except Exception as e:
            self.logger.error(f"[API_CLIENT] Erreur lors de la fermeture: {e}")

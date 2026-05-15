"""
core/api_profile.py
===================
Schéma de données pour les profils de configuration API
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid


class Provider:
    OPENAI    = "openai"
    ANTHROPIC = "anthropic"
    LOCAL     = "local"

    ALL = [OPENAI, ANTHROPIC, LOCAL]

    LABELS = {
        OPENAI:    "OpenAI",
        ANTHROPIC: "Anthropic",
        LOCAL:     "Local (Ollama / LMStudio)",
    }

    DEFAULT_URLS = {
        OPENAI:    "https://api.openai.com/v1",
        ANTHROPIC: "https://api.anthropic.com/v1",
        LOCAL:     "http://localhost:11434/v1",
    }

    DEFAULT_MODELS = {
        OPENAI:    "gpt-4o",
        ANTHROPIC: "claude-sonnet-4-6",
        LOCAL:     "llama3",
    }


@dataclass
class APIProfile:
    name:        str
    provider:    str
    api_key:     str
    base_url:    str
    model:       str
    verify_ssl:  bool          = False
    temperature: float         = 0.7
    max_tokens:  Optional[int] = None
    profile_id:  str           = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "APIProfile":
        known = {k for k in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})

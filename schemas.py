import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator

class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


ENV_VAR_POR_PROVIDER = {
    Provider.OPENAI: "OPENAI_API_KEY",
    Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    Provider.GEMINI: "GEMINI_API_KEY",
    Provider.OPENROUTER: "OPENROUTER_API_KEY",
}


class ChatMessage(BaseModel):
    role: str = Field(description="'user', 'assistant' o 'system'")
    content: str

    @field_validator("role")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        roles_permitidos = {"user", "assistant", "system"}
        if v not in roles_permitidos:
            raise ValueError(f"role debe ser uno de {roles_permitidos}, recibido: '{v}'")
        return v


class LLMConfig(BaseModel):
    provider: Provider
    model: str
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    google_api_key: Optional[SecretStr] = None
    openrouter_api_key: Optional[SecretStr] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, gt=0)

    @model_validator(mode="after")
    def completar_api_key_desde_env(self) -> "LLMConfig":
        """Si no se pasó la api key del provider activo, la busca en las variables de entorno."""
        campo = self._campo_api_key(self.provider)
        if getattr(self, campo) is None:
            valor = os.getenv(ENV_VAR_POR_PROVIDER[self.provider])
            if valor:
                setattr(self, campo, SecretStr(valor))
        return self

    @staticmethod
    def _campo_api_key(provider: "Provider") -> str:
        return {
            Provider.OPENAI: "openai_api_key",
            Provider.ANTHROPIC: "anthropic_api_key",
            Provider.GEMINI: "google_api_key",
            Provider.OPENROUTER: "openrouter_api_key",
        }[provider]

    def get_api_key(self) -> str:
        """Devuelve la API key correspondiente al provider configurado."""
        api_key: Optional[SecretStr] = getattr(self, self._campo_api_key(self.provider))
        if api_key is None:
            raise ValueError(
                f"No se configuró una API key para el provider '{self.provider.value}' "
                f"(seteá {ENV_VAR_POR_PROVIDER[self.provider]} en el .env)"
            )
        return api_key.get_secret_value()


class ModelResponse(BaseModel):
    provider: Provider
    model: str
    content: str
    error: Optional[str] = None


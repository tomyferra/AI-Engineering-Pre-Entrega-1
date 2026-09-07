
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List
from schemas import ModelResponse, ChatMessage


class BaseLLMClient(ABC):
    """Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor real detrás."""

    @abstractmethod
    async def generate(self, message: ChatMessage) -> ModelResponse:
        """Genera una respuesta completa (modo normal, no streaming)."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """Genera una respuesta en streaming."""
        raise NotImplementedError("This method should be implemented by subclasses.")

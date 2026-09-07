from typing import AsyncGenerator, List

from clients.llm_client import BaseLLMClient
from clients.openai_client import OpenAIClient
from clients.anthropic_client import AnthropicClient
from clients.gemini_client import GeminiClient
from clients.openrouter_client import OpenRouterClient
from schemas import ChatMessage, LLMConfig, ModelResponse, Provider

MODELS_POR_PROVIDER = {
    Provider.OPENAI: "gpt-4o-mini",
    Provider.ANTHROPIC: "claude-3-5-haiku-20241022",
    Provider.GEMINI: "gemini-3.6-flash",
    Provider.OPENROUTER: "minimax/minimax-m3:free",
}

CLIENTS_POR_PROVIDER = {
    Provider.OPENAI: OpenAIClient,
    Provider.ANTHROPIC: AnthropicClient,
    Provider.GEMINI: GeminiClient,
    Provider.OPENROUTER: OpenRouterClient,
}


class AsyncLLMManager:
    """Punto de entrada único: instancia el cliente correcto según config.provider."""

    def __init__(self, config: LLMConfig):
        self.config = config
        client_cls = CLIENTS_POR_PROVIDER[config.provider]
        self._client: BaseLLMClient = client_cls(
            api_key=config.get_api_key(),
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        return await self._client.generate(messages)

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        async for chunk in self._client.generate_stream(messages):
            yield chunk

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncLLMManager":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.aclose()

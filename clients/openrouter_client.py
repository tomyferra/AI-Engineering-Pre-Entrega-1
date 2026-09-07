from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError
from typing import AsyncGenerator, List

from schemas import ModelResponse, ChatMessage, Provider
from clients.llm_client import BaseLLMClient


class OpenRouterClient(BaseLLMClient):
    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ):
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[m.model_dump() for m in messages],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            return ModelResponse(
                provider=Provider.OPENROUTER,
                model=self.model,
                content=response.choices[0].message.content or "",
            )

        except RateLimitError as e:
            return ModelResponse(
                provider=Provider.OPENROUTER,
                model=self.model,
                content="",
                error=f"Límite de cuota de OpenRouter excedido: {e}",
            )

        except APIConnectionError as e:
            return ModelResponse(
                provider=Provider.OPENROUTER,
                model=self.model,
                content="",
                error=f"Error de conexión con OpenRouter: {e}",
            )

        except APIError as e:
            return ModelResponse(
                provider=Provider.OPENROUTER,
                model=self.model,
                content="",
                error=f"Error de la API de OpenRouter: {e}",
            )

    async def generate_stream(
        self,
        messages: List[ChatMessage],
    ) -> AsyncGenerator[str, None]:
        try:
            async with await self._client.chat.completions.create(
                model=self.model,
                messages=[m.model_dump() for m in messages],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            ) as stream:
                async for chunk in stream:
                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta.content

                    if delta:
                        yield delta

        except (RateLimitError, APIConnectionError, APIError) as e:
            yield f"\n[⚠️ Error durante el streaming: {e}]"

    async def aclose(self) -> None:
        await self._client.close()
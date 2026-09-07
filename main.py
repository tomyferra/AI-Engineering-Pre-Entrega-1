import asyncio
import os

from dotenv import load_dotenv

from schemas import ChatMessage, LLMConfig, Provider
from clients.openai_client import OpenAIClient
from clients.antrhropic_client import AnthropicClient
from clients.gemini_client import GeminiClient
from clients.openrouter_client import OpenRouterClient

load_dotenv()

MODELS_POR_PROVIDER = {
    Provider.OPENAI: "gpt-4o-mini",
    Provider.ANTHROPIC: "claude-3-5-haiku-20241022",
    Provider.GEMINI: "gemini-3.6-flash",
    Provider.OPENROUTER: "openrouter/free",
}

CLIENTS_POR_PROVIDER = {
    Provider.OPENAI: OpenAIClient,
    Provider.ANTHROPIC: AnthropicClient,
    Provider.GEMINI: GeminiClient,
    Provider.OPENROUTER: OpenRouterClient,
}


async def main() -> None:
    provider = Provider(os.getenv("LLM_PROVIDER", "openrouter"))
    config = LLMConfig(provider=provider, model=MODELS_POR_PROVIDER[provider], temperature=0.2, max_tokens=1024)

    question_to_answer = "¿Cuál es la capital de Francia?"
    
    client_cls = CLIENTS_POR_PROVIDER[provider]
    client = client_cls(
        api_key=config.get_api_key(),
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
    print(f"--- Pregunta:  ({question_to_answer}) ---")
    print("------------------------------------------------------------")
    pregunta = [ChatMessage(role="user", content=question_to_answer)]

    print(f"--- Modo normal ({provider.value}), model: {config.model} ---")
    respuesta = await client.generate(pregunta)
    print(respuesta.error or respuesta.content)

    print(f"\n--- Modo streaming ({provider.value}), model: {config.model} ---")
    async for chunk in client.generate_stream(pregunta):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import sys

from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

from manager import AsyncLLMManager, MODELS_POR_PROVIDER
from schemas import ChatMessage, LLMConfig, Provider

load_dotenv()


async def main() -> None:
    provider = Provider(os.getenv("LLM_PROVIDER", "openrouter"))
    config = LLMConfig(provider=provider, model=MODELS_POR_PROVIDER[provider], temperature=0.2, max_tokens=1024)

    question_to_answer = "¿Cuál es la capital de Francia?"
    pregunta = [ChatMessage(role="user", content=question_to_answer)]

    print(f"--- Pregunta: ({question_to_answer}) ---")
    print("------------------------------------------------------------")

    async with AsyncLLMManager(config) as manager:
        print(f"--- Modo normal ({provider.value}), model: {config.model} ---")
        respuesta = await manager.generate(pregunta)
        print(respuesta.error or respuesta.content)

        print(f"\n--- Modo streaming ({provider.value}), model: {config.model} ---")
        async for chunk in manager.generate_stream(pregunta):
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())

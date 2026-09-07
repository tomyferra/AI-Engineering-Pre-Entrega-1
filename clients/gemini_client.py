from google import genai
from google.genai import types
from typing import AsyncGenerator, List
from clients.llm_client import BaseLLMClient
from schemas import ModelResponse, ChatMessage, Provider


class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self._client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _convertir_mensajes(self, messages: List[ChatMessage]):
        """Gemini separa el system prompt del resto, y llama 'model' al rol del asistente."""
        contents = []
        system_instruction = None
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                rol_gemini = "model" if m.role == "assistant" else "user"
                contents.append(types.Content(role=rol_gemini, parts=[types.Part(text=m.content)]))
        return contents, system_instruction

    def _crear_chat(self, messages: List[ChatMessage]):
        """Arma un chat de Gemini con el historial previo, dejando el último mensaje afuera."""
        contents, system_instruction = self._convertir_mensajes(messages)
        historial, ultimo_mensaje = contents[:-1], contents[-1]
        chat = self._client.aio.chats.create(
            model=self.model,
            history=historial,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                system_instruction=system_instruction,
            ),
        )
        return chat, ultimo_mensaje.parts

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        try:
            chat, ultimo_mensaje = self._crear_chat(messages)
            response = await chat.send_message(ultimo_mensaje)
            return ModelResponse(provider=Provider.GEMINI, model=self.model, content=response.text)
        except Exception as e:
            return ModelResponse(provider=Provider.GEMINI, model=self.model, content="",
                                  error=f"Error de la API de Gemini: {e}")

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        try:
            chat, ultimo_mensaje = self._crear_chat(messages)
            stream = await chat.send_message_stream(ultimo_mensaje)
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[⚠️ Error durante el streaming: {e}]"

    async def aclose(self) -> None:
        self._client.close()
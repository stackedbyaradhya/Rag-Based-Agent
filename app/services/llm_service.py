from typing import Any

import httpx

from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.api_key = settings.openrouter_api_key
        self.model = settings.llm_model

    async def answer(self, question: str, context: str) -> str:
        if not self.api_key:
            return "I cannot answer confidently without connected LLM credentials."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict enterprise knowledge assistant. "
                    "Answer only using provided context. Refuse if insufficient."
                ),
            },
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
        ]

        payload: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": 0.1}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
                return body["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as exc:
                details = _extract_error_details(exc.response)
                return (
                    "I could not generate an answer from the LLM provider right now. "
                    f"Provider error ({exc.response.status_code}): {details}"
                )
            except Exception:
                return "I could not generate an answer due to an unexpected LLM service error."


def _extract_error_details(response: httpx.Response) -> str:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        text = (response.text or "").strip()
        return text[:300] if text else "Unknown upstream error."

    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            message = err.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
        message = body.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    return str(body)[:300]

from typing import Any

import httpx

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.api_key = settings.openrouter_api_key
        self.model = settings.embedding_model

    async def embed(self, input_text: str) -> list[float]:
        if not self.api_key:
            # Deterministic local fallback for dev when API key is unavailable.
            return [float((ord(ch) % 17) / 17) for ch in (input_text[:768].ljust(768, " "))]

        payload: dict[str, Any] = {"model": self.model, "input": input_text}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/embeddings", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

from __future__ import annotations

import os
import httpx

from app.ai_tutor.schemas import TutorRequest
from app.ai_tutor.services.providers.base import AIProvider


class RemoteServerProvider(AIProvider):
    """
    Connects to the central cloud server (e.g. Render) to execute AI Tutor & Chat requests
    using the server-side Gemini API key. This avoids distributing the API key to client machines.
    """

    def __init__(self):
        self.server_url = os.getenv(
            "LICENSE_SERVER_URL",
            "https://lls-cbt-activator.onrender.com",
        ).rstrip("/")
        self.timeout = float(os.getenv("AI_SERVER_TIMEOUT", "25"))

    @property
    def name(self) -> str:
        return "cloud-ai"

    @property
    def available(self) -> bool:
        # Cloud server is available when connected to the internet
        return bool(self.server_url)

    async def ask_tutor(
        self,
        request: TutorRequest,
    ) -> dict:
        """Forward tutor explanation request to the cloud server."""
        payload = request.model_dump()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.server_url}/api/v1/tutor/ask",
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        return data

    async def chat(self, prompt: str) -> str:
        """Forward general knowledge chat prompt to the cloud server."""
        payload = {
            "message": prompt,
            "history": [],
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.server_url}/api/v1/tutor/chat",
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        return data.get("reply", "").strip()

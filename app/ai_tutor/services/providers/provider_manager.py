from __future__ import annotations

import logging

from app.ai_tutor.schemas import TutorRequest
from app.ai_tutor.services.providers.base import AIProvider
from app.ai_tutor.services.response_validator import (
    validate_tutor_result,
)


logger = logging.getLogger(__name__)


class AIProviderManager:
    def __init__(
        self,
        providers: list[AIProvider],
    ):
        self.providers = providers

    async def ask_tutor(
        self,
        request: TutorRequest,
    ) -> tuple[str, dict]:

        last_error: Exception | None = None

        for provider in self.providers:
            if not provider.available:
                logger.info(
                    "Skipping unavailable provider: %s",
                    provider.name,
                )
                print(
                    f"AI provider '{provider.name}' failed:",
                    repr(last_error) if last_error else "No error information available.",
                )

                continue

            try:
                logger.info(
                    "Trying AI provider: %s",
                    provider.name,
                )

                result = await provider.ask_tutor(request)

                validated = validate_tutor_result(result)

                logger.info(
                    "AI provider succeeded: %s",
                    provider.name,
                )

                return (
                    provider.name,
                    validated.model_dump(),
                )

            except Exception as exc:
                last_error = exc

                logger.warning(
                    "AI provider failed: %s - %s",
                    provider.name,
                    exc,
                )

                continue

        if last_error is not None:
            raise RuntimeError("All AI providers failed.") from last_error

        raise RuntimeError("No AI providers are available.")

    def health(self) -> dict:

        return {
            provider.name: {
                "available": provider.available,
            }
            for provider in self.providers
        }

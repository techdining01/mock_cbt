from __future__ import annotations

from app.ai_tutor.schemas import (
    TutorRequest,
    TutorResponse,
)

from app.ai_tutor.services.providers.gemini import (
    GeminiProvider,
)


class TutorService:
    def __init__(self) -> None:

        self.provider = GeminiProvider()

    async def explain(
        self,
        request: TutorRequest,
    ) -> TutorResponse:

        result = await self.provider.generate_tutor_response(request)

        return TutorResponse(
            success=True,
            answer="",
            greeting=result.get("greeting", ""),
            explanation=result.get("explanation", ""),
            steps=result.get("steps", []),
            hint=result.get("hint", ""),
            encouragement=result.get("encouragement", ""),
            follow_up_question=result.get("follow_up_question", ""),
        )

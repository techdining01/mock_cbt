from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.ai_tutor.schemas import (
    TutorRequest,
    TutorResponse,
)

from app.ai_tutor.services.providers.provider_manager import (
    AIProviderManager,
)

from app.ai_tutor.services.providers.gemini import (
    GeminiProvider,
)

from app.ai_tutor.services.providers.ollama import (
    OllamaProvider,
)


router = APIRouter(
    prefix="/api/v1/tutor",
    tags=["AI Tutor"],
)


provider_manager = AIProviderManager(
    providers=[
        GeminiProvider(),
        OllamaProvider(),
    ]
)


@router.get("/health")
async def tutor_health():

    return {
        "success": True,
        "service": "AI Tutor",
        "providers": provider_manager.health(),
    }


@router.post(
    "/ask",
    response_model=TutorResponse,
)
async def ask_tutor(
    request: TutorRequest,
):

    try:
        provider_name, result = await provider_manager.ask_tutor(request)

        greeting = result.get(
            "greeting",
            "",
        )

        explanation = result.get(
            "explanation",
            "",
        )

        steps = result.get(
            "steps",
            [],
        )

        hint = result.get(
            "hint",
            "",
        )

        encouragement = result.get(
            "encouragement",
            "",
        )

        follow_up = result.get(
            "follow_up_question",
            "",
        )

        parts: list[str] = []

        if greeting:
            parts.append(greeting)

        if explanation:
            parts.append(explanation)

        if steps:
            parts.append(
                "\n".join(f"{index + 1}. {step}" for index, step in enumerate(steps))
            )

        if hint:
            parts.append(f"Hint: {hint}")

        if encouragement:
            parts.append(encouragement)

        if follow_up:
            parts.append(f"Think about this: {follow_up}")

        answer = "\n\n".join(parts)

        return TutorResponse(
            success=True,
            answer=answer,
            provider=provider_name,
            greeting=greeting,
            explanation=explanation,
            steps=steps,
            hint=hint,
            encouragement=encouragement,
            follow_up_question=follow_up,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI Tutor is temporarily unavailable. All configured providers failed."
            ),
        ) from exc

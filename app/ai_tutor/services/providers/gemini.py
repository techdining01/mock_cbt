from __future__ import annotations

import json
import os

from google import genai

from app.ai_tutor.schemas import TutorRequest
from app.ai_tutor.services.providers.base import AIProvider
from dotenv import load_dotenv


load_dotenv(".env")


class GeminiProvider(AIProvider):
    def __init__(self):

        self.api_key = os.getenv("GEMINI_API_KEY")

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )

        self.client = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def available(self) -> bool:
        return self.client is not None

    async def ask_tutor(
        self,
        request: TutorRequest,
    ) -> dict:

        if not self.available:
            raise RuntimeError("Gemini provider is not configured.")

        options_text = "\n".join(
            f"{option.label}. {option.text}" for option in request.options
        )

        prompt = self._build_prompt(
            request=request,
            options_text=options_text,
        )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        raw = response.text.strip()

        return self._parse_response(raw)

    def _build_prompt(
        self,
        request: TutorRequest,
        options_text: str,
    ) -> str:

        return f"""
You are an excellent secondary-school teacher
helping a student understand a CBT examination question.

CRITICAL RULE:

The CORRECT ANSWER supplied by the CBT system is authoritative.

You MUST NOT change it, recalculate it, reinterpret it,
or choose another option.

Your job is to explain the supplied correct answer.

If the student's answer differs from the CORRECT ANSWER,
clearly explain why the student's answer is incorrect and
why the supplied correct answer is correct.

Never state the student's answer as the correct answer.

SUBJECT:
{request.subject}

QUESTION:
{request.question}

OPTIONS:
{options_text or "No options supplied"}

STUDENT'S ANSWER:
{request.student_answer or "No answer selected"}

CORRECT ANSWER:
{request.correct_answer or "Not supplied"}

STORED EXPLANATION:
{request.explanation or "No stored explanation available"}

Give a clear, friendly teaching explanation.

If the student selected the wrong answer:

- explain why their choice is wrong
- explain why the correct answer is correct
- do not embarrass the student

If the question requires reasoning,
explain the reasoning step by step.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "greeting": "...",
    "explanation": "...",
    "steps": [
        "...",
        "..."
    ],
    "hint": "...",
    "encouragement": "...",
    "follow_up_question": "..."
}}
"""

    @staticmethod
    def _parse_response(
        raw: str,
    ) -> dict:

        if raw.startswith("```json"):
            raw = raw[7:]

        elif raw.startswith("```"):
            raw = raw[3:]

        if raw.endswith("```"):
            raw = raw[:-3]

        raw = raw.strip()

        result = json.loads(raw)

        if not isinstance(result, dict):
            raise ValueError("Gemini returned an invalid response.")

        return result

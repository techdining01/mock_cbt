from __future__ import annotations

import json
import os

import httpx

from app.ai_tutor.schemas import TutorRequest
from app.ai_tutor.services.providers.base import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://127.0.0.1:11434",
        ).rstrip("/")

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:0.5b-instruct",
        )

        self.timeout = float(
            os.getenv(
                "OLLAMA_TIMEOUT",
                "90",
            )
        )

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def available(self) -> bool:
        # Ollama is a local service. Actual availability
        # is confirmed when ask_tutor() connects to it.
        return True

    async def ask_tutor(
        self,
        request: TutorRequest,
    ) -> dict:

        prompt = self._build_prompt(request)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
            },
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
        ) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )

            response.raise_for_status()

        data = response.json()

        raw = data.get("response", "").strip()

        if not raw:
            raise RuntimeError("Ollama returned an empty response.")

        return self._parse_response(raw)

    def _build_prompt(
        self,
        request: TutorRequest,
    ) -> str:

        options_text = "\n".join(
            f"{option.label}. {option.text}" for option in request.options
        )

        return f"""
You are a secondary-school CBT tutor.

Your job is to help the student understand the
examination question, not simply give an answer.

The supplied correct answer is authoritative.
DO NOT change it.

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

Instructions:

1. Explain the answer clearly.
2. If the student selected the wrong answer,
   explain why it is wrong.
3. Explain why the correct answer is correct.
4. If reasoning is required, explain it step by step.
5. Be friendly and encouraging.
6. Do not embarrass the student.
7. Do not invent facts.
8. Do not change the supplied correct answer.

Return ONLY valid JSON with exactly these fields:

{{
    "greeting": "short friendly greeting",
    "explanation": "clear explanation",
    "steps": ["step one", "step two"],
    "hint": "",
    "encouragement": "",
    "follow_up_question": ""
}}

Rules for optional fields:
- "steps": include ONLY if the question requires step-by-step reasoning (e.g. maths, calculations). Otherwise return an empty array [].
- "hint": include ONLY if there is a genuinely useful memory aid. Otherwise return "".
- "encouragement": include ONLY if the student answered incorrectly or did not answer. Otherwise return "".
- "follow_up_question": include ONLY if a meaningful follow-up exists. Otherwise return "".
"""

    @staticmethod
    def _parse_response(
        raw: str,
    ) -> dict:

        raw = raw.strip()

        if raw.startswith("```json"):
            raw = raw[7:]

        elif raw.startswith("```"):
            raw = raw[3:]

        if raw.endswith("```"):
            raw = raw[:-3]

        raw = raw.strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned invalid JSON.") from exc

        if not isinstance(result, dict):
            raise RuntimeError("Ollama returned an invalid object.")

        return result

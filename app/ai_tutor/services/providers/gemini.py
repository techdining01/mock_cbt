from __future__ import annotations

import asyncio
import json
import os
import re

from google import genai

from app.ai_tutor.schemas import ChatMessage, TutorRequest
from app.ai_tutor.services.providers.base import AIProvider


_GEMINI_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_\-]{15,}$")


def _looks_like_valid_gemini_key(key: str | None) -> bool:
    """Heuristic check: reject obviously invalid Gemini keys early.

    Google AI Studio / Gemini keys are typically base64url-ish and start
    with prefixes like ``AIza``, ``AQ``, or other known Google key formats,
    with a minimum length and a restricted character set.

    This is intentionally lenient — it only rejects values that are clearly
    not Google API keys (e.g. ``"test"``, empty strings, random unicode).
    """
    if not key:
        return False
    key = key.strip()
    if len(key) < 15:
        return False
    if not _GEMINI_KEY_PATTERN.match(key):
        return False
    return True


class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key: str | None = None
        self.client = None
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.timeout = float(os.getenv("GEMINI_TIMEOUT", "45"))
        self._model_failed = False
        self._last_key_seen: str | None = None
        self._ensure_client()

    def _ensure_client(self):
        """Dynamically initialize or refresh Gemini client if API key is present.

        The key source is the process environment. The router's bootstrap injects
        DB-backed settings into ``os.environ`` before the first call, so setting
        changes are picked up on the next ``ask_tutor``/``chat`` call.
        """
        key_raw = os.getenv("GEMINI_API_KEY")
        key = key_raw.strip() if isinstance(key_raw, str) else None

        if key == self._last_key_seen:
            return

        self._last_key_seen = key

        if not _looks_like_valid_gemini_key(key):
            self.api_key = None
            self.client = None
            return

        if self.client is None or key != self.api_key:
            self.api_key = key
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as err:
                print(f"[GeminiProvider] Client initialization error: {err}", flush=True)
                self.client = None

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def available(self) -> bool:
        self._ensure_client()
        return (
            self.client is not None
            and bool(self.api_key)
            and not self._model_failed
        )

    async def ask_tutor(
        self,
        request: TutorRequest,
    ) -> dict:
        self._ensure_client()
        if not self.available:
            raise RuntimeError(
                "Gemini provider is not configured. "
                "Add a valid GEMINI_API_KEY in settings or in .env."
            )

        options_text = "\n".join(
            f"{option.label}. {option.text}" for option in request.options
        )

        prompt = self._build_prompt(
            request=request,
            options_text=options_text,
        )

        try:
            response = await asyncio.wait_for(
                self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                ),
                timeout=self.timeout,
            )
        except Exception as exc:
            if self._is_auth_error(exc):
                # Bad key / quota / permission — mark client as unusable so
                # we immediately skip Gemini on subsequent retries.
                self.client = None
                print(
                    f"[GeminiProvider] Auth/quota failure — disabling provider for this run: {exc}",
                    flush=True,
                )
            elif self._is_model_error(exc):
                self._model_failed = True
                print(
                    f"[GeminiProvider] Model '{self.model}' not found — falling back to next provider.",
                    flush=True,
                )
            raise

        raw = (getattr(response, "text", None) or "").strip()
        if not raw:
            raise RuntimeError("Gemini returned an empty response.")
        return self._parse_response(raw)

    async def chat(
        self,
        message: str,
        history: list[ChatMessage] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        self._ensure_client()
        if not self.available:
            raise RuntimeError(
                "Gemini provider is not configured. "
                "Add a valid GEMINI_API_KEY in settings or in .env."
            )

        prompt = self._flatten_chat(message, history, system_prompt)

        try:
            response = await asyncio.wait_for(
                self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                ),
                timeout=self.timeout,
            )
        except Exception as exc:
            if self._is_auth_error(exc):
                self.client = None
                print(
                    f"[GeminiProvider] Auth/quota failure in chat — disabling provider: {exc}",
                    flush=True,
                )
            elif self._is_model_error(exc):
                self._model_failed = True
                print(
                    f"[GeminiProvider] Model '{self.model}' not found — falling back to next provider.",
                    flush=True,
                )
            raise
        reply = (getattr(response, "text", None) or "").strip()
        if not reply:
            raise RuntimeError("Gemini returned an empty chat response.")
        return reply

    @staticmethod
    def _is_model_error(exc: Exception) -> bool:
        msg = str(exc).lower()
        return any(
            k in msg
            for k in (
                "not found",
                "404",
                "invalid model",
                "model not found",
                "does not exist",
            )
        )

    @staticmethod
    def _is_auth_error(exc: Exception) -> bool:
        msg = str(exc).lower()
        return any(
            k in msg
            for k in (
                "api key not valid",
                "invalid api key",
                "api key invalid",
                "permission denied",
                "401",
                "403",
                "quota",
                "unauthorized",
                "authentication",
            )
        )

    @staticmethod
    def _flatten_chat(
        message: str,
        history: list[ChatMessage] | None,
        system_prompt: str | None = None,
    ) -> str:
        """Flatten structured (message, history, system_prompt) into a plain-text prompt."""
        lines: list[str] = []
        if system_prompt:
            lines.append(system_prompt.strip())
            lines.append("")
        for msg in (history or [])[-10:]:
            role = "Student" if msg.role == "user" else "AI"
            lines.append(f"{role}: {msg.content}")
        lines.append(f"Student: {message}")
        lines.append("AI:")
        return "\n".join(lines)

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

If the question requires reasoning, explain the reasoning step by step.

IMPORTANT: For the "steps" field:
- Only include actual, meaningful step-by-step reasoning if the question requires it (mathematics, calculations, logical reasoning, etc.)
- Each step should be a complete, clear explanation of one part of the solution
- If the question does NOT require step-by-step reasoning, return an empty array: []

CRITICAL: You MUST provide content for ALL fields. Do not leave any field empty:
- "greeting": Always provide a short, friendly greeting appropriate for the context
- "explanation": Always provide a clear, detailed explanation of the answer
- "steps": provide meaningful step-by-step reasoning in an array
- "hint": Always provide a helpful memory aid or tip related to the question
- "encouragement": Always provide encouraging words appropriate for the student's performance
- "follow_up_question": Always provide a thought-provoking follow-up question to deepen understanding

Return ONLY valid JSON.

Use exactly this structure:
{{
    "greeting": "short friendly greeting",
    "explanation": "clear explanation",
    "steps": [],
    "hint": "helpful memory aid or tip",
    "encouragement": "encouraging words",
    "follow_up_question": "thought-provoking follow-up question"
}}
"""

    @staticmethod
    def _parse_response(raw: str) -> dict:
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
            raise RuntimeError("Gemini returned invalid JSON.") from exc
        if not isinstance(result, dict):
            raise ValueError("Gemini returned an invalid response object.")
        return result


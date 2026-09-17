from __future__ import annotations

import json
import os
import socket
from typing import Any

import httpx

from app.ai_tutor.schemas import ChatMessage, TutorRequest
from app.ai_tutor.services.providers.base import AIProvider


def _split_host_port(base_url: str) -> tuple[str, int]:
    host = base_url.split("://")[-1].split("/")[0]
    parts = host.rsplit(":", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    scheme = base_url.split("://", 1)[0].lower() if "://" in base_url else "http"
    return host, 443 if scheme == "https" else 11434


class OllamaProvider(AIProvider):
    def __init__(self):
        self._base_url = ""
        self._model = ""
        self._timeout = 90.0
        self._last_url_seen: str | None = None
        self._last_model_seen: str | None = None
        self._last_timeout_seen: str | None = None
        self._refresh_from_env()
        # Models we consider always-installable via ``ollama pull`` if missing.
        self._known_light_models = {
            "qwen2.5:0.5b-instruct",
            "qwen2.5:1.5b-instruct",
            "llama3.2:1b",
            "llama3.2:3b",
            "gemma3:1b",
            "phi3:mini",
        }

    # ------------------------------------------------------------------
    # Env reloading (settings can change at runtime)
    # ------------------------------------------------------------------

    def _refresh_from_env(self) -> None:
        url_raw = os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
        url = url_raw.strip().rstrip("/") or "http://127.0.0.1:11434"
        model = (os.getenv("OLLAMA_MODEL") or "qwen2.5:0.5b-instruct").strip()
        timeout_raw = os.getenv("OLLAMA_TIMEOUT") or "90"
        if (
            url == self._last_url_seen
            and model == self._last_model_seen
            and timeout_raw == self._last_timeout_seen
        ):
            return
        self._base_url = url
        self._model = model
        self._last_url_seen = url
        self._last_model_seen = model
        self._last_timeout_seen = timeout_raw
        try:
            self._timeout = float(timeout_raw)
        except (TypeError, ValueError):
            self._timeout = 90.0

    @property
    def name(self) -> str:
        return "ollama"

    # ------------------------------------------------------------------
    # Health / availability
    # ------------------------------------------------------------------

    def _tcp_probe(self, timeout: float = 1.0) -> bool:
        try:
            addr, port = _split_host_port(self._base_url)
            with socket.create_connection((addr, port), timeout=timeout):
                return True
        except OSError:
            return False

    async def _api_probe(self) -> bool:
        """True iff the Ollama API responds on /api/tags."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self._base_url}/api/tags")
            return 200 <= response.status_code < 500
        except Exception:
            return False

    async def _ensure_model_available(self) -> bool:
        """Return True if the chosen model is listed by Ollama.

        Does NOT auto-pull because that can take minutes; callers surface
        a clear "please run ollama pull X" message instead.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/api/tags")
            if response.status_code != 200:
                return False
            data = response.json()
            models = data.get("models") or []
            names = {str(m.get("name", "")).strip() for m in models if isinstance(m, dict)}
            if self._model in names:
                return True
            # Match with/without explicit ``:latest`` tag
            for n in list(names):
                base = n.split(":")[0] if ":" in n else n
                lookup_base = (
                    self._model.split(":")[0] if ":" in self._model else self._model
                )
                if base == lookup_base:
                    return True
            return False
        except Exception:
            return False

    @property
    def available(self) -> bool:
        self._refresh_from_env()
        # Cheap TCP probe — avoids async overhead in the health-check path.
        return self._tcp_probe(timeout=1.0)

    # ------------------------------------------------------------------
    # Core ask_tutor — with JSON mode fallback and last-ditch parser
    # ------------------------------------------------------------------

    async def ask_tutor(
        self,
        request: TutorRequest,
    ) -> dict:
        self._refresh_from_env()

        if not self._tcp_probe(timeout=2.0):
            raise RuntimeError(
                "Ollama is not reachable. "
                "Please start Ollama locally or configure OLLAMA_BASE_URL."
            )

        if not await self._ensure_model_available():
            raise RuntimeError(
                f"Ollama model '{self._model}' is not installed. "
                f"Run:  ollama pull {self._model}"
            )

        system_prompt = (
            "You are a helpful CBT tutor. Always answer in plain, "
            "encouraging English. Never invent facts. Never change the "
            "supplied correct answer."
        )
        user_prompt = self._build_prompt(request)

        # Strategy: prefer Ollama /api/chat with JSON response_format if
        # available; fall back to /api/generate with "format":"json".
        response_text = await self._try_chat_endpoint(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
            json_mode=True,
        )
        if response_text is None:
            response_text = await self._generate_json(user_prompt, temperature=0.2)

        if not response_text:
            raise RuntimeError("Ollama returned an empty response.")

        try:
            result = self._parse_response(response_text)
        except RuntimeError:
            # Last resort: coerce by re-asking for valid JSON only
            fix_prompt = (
                "Return ONLY valid JSON with keys: greeting, explanation, "
                "steps, hint, encouragement, follow_up_question.\n"
                "Input:\n" + response_text
            )
            retry = await self._generate_json(fix_prompt, temperature=0.0)
            if not retry:
                raise
            result = self._parse_response(retry)

        return result

    # ------------------------------------------------------------------
    # Chat endpoint (general knowledge)
    # ------------------------------------------------------------------

    async def chat(
        self,
        message: str,
        history: list[ChatMessage] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        self._refresh_from_env()

        if not self._tcp_probe(timeout=2.0):
            raise RuntimeError(
                "Ollama is not reachable. "
                "Please start Ollama locally or configure OLLAMA_BASE_URL."
            )
        if not await self._ensure_model_available():
            raise RuntimeError(
                f"Ollama model '{self._model}' is not installed. "
                f"Run:  ollama pull {self._model}"
            )

        # 1. Prefer /api/chat (preserves roles natively)
        try:
            messages: list[dict[str, Any]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt.strip()})
            for msg in (history or [])[-10:]:
                role = "user" if msg.role == "user" else "assistant"
                messages.append({"role": role, "content": msg.content})
            messages.append({"role": "user", "content": message})

            payload = {
                "model": self._model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.7},
            }
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
            data = response.json()
            message_obj = data.get("message") or {}
            reply = (message_obj.get("content") or "").strip()
            if reply:
                return reply
        except httpx.HTTPStatusError as exc:
            # /api/chat may not exist on very old Ollama versions — fall through.
            if exc.response.status_code >= 500 or exc.response.status_code == 404:
                pass
            else:
                raise
        except Exception:
            # Fall back to flattened /api/generate
            pass

        # 2. Fallback: /api/generate with flattened prompt
        flattened = self._flatten_chat(message, history, system_prompt)
        payload = {
            "model": self._model,
            "prompt": flattened,
            "stream": False,
            "options": {"temperature": 0.7},
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
        return (response.json().get("response") or "").strip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _try_chat_endpoint(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool,
    ) -> str | None:
        """Use Ollama /api/chat. Returns None on 404/old-server style errors."""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            payload: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            }
            if json_mode:
                try:
                    import httpx as _httpx

                    schema = {
                        "type": "object",
                        "properties": {
                            "greeting": {"type": "string"},
                            "explanation": {"type": "string"},
                            "steps": {"type": "array", "items": {"type": "string"}},
                            "hint": {"type": "string"},
                            "encouragement": {"type": "string"},
                            "follow_up_question": {"type": "string"},
                        },
                        "required": [
                            "greeting",
                            "explanation",
                            "steps",
                            "hint",
                            "encouragement",
                            "follow_up_question",
                        ],
                    }
                    payload["format"] = schema
                except Exception:
                    payload["format"] = "json"
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
            data = response.json()
            message_obj = data.get("message") or {}
            content = (message_obj.get("content") or "").strip()
            return content or None
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (404, 400):
                return None
            raise
        except Exception:
            return None

    async def _generate_json(self, prompt: str, temperature: float) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
        return (response.json().get("response") or "").strip()

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

IMPORTANT: For the "steps" field:
- Only include actual, meaningful step-by-step reasoning if the question requires it (mathematics, calculations, logical reasoning, etc.)
- Each step should be a complete, clear explanation of one part of the solution
- Example of good steps: ["First, identify the formula needed", "Substitute the given values into the formula", "Calculate the result step by step", "Verify the answer makes sense"]
- If the question does NOT require step-by-step reasoning, return an empty array: []
- NEVER use placeholder text like "step one", "step two" - either give real steps or return []

CRITICAL: You MUST provide content for ALL fields. Do not leave any field empty:
- "greeting": Always provide a short, friendly greeting appropriate for the context
- "explanation": Always provide a clear, detailed explanation of the answer
- "steps": provide meaningful step-by-step reasoning in an array
- "hint": Provide a helpful memory aid or tip related to the question
- "encouragement": Always provide encouraging words appropriate for the student's performance
- "follow_up_question": Always provide a thought-provoking follow-up question to deepen understanding

Return ONLY valid JSON with exactly these fields:

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

        # Slurp the first JSON object if the model added trailing text
        if not (raw.startswith("{") and raw.endswith("}")):
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                raw = raw[start : end + 1]

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned invalid JSON.") from exc

        if not isinstance(result, dict):
            raise RuntimeError("Ollama returned an invalid object.")

        # Apply defaults defensively so response_validator never sees empty fields
        defaults: dict[str, Any] = {
            "greeting": "Hi there!",
            "explanation": "",
            "steps": [],
            "hint": "",
            "encouragement": "Keep practicing — you've got this!",
            "follow_up_question": "Can you think of another way to approach this problem?",
        }
        for key, fallback in defaults.items():
            value = result.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                result[key] = fallback
            if key == "steps":
                if not isinstance(value, list):
                    result[key] = []
                else:
                    cleaned = [
                        str(s).strip()
                        for s in value
                        if isinstance(s, str) and s.strip()
                    ]
                    result[key] = cleaned

        return result


from __future__ import annotations

import os
import shutil
from io import BytesIO
from pathlib import Path

import pytesseract
from PIL import Image


class OCRService:
    @staticmethod
    def resolve_tesseract_path() -> str | None:
        resolved = shutil.which("tesseract")
        if resolved:
            return resolved

        candidates = []

        for env_var in (
            "ProgramFiles",
            "ProgramFiles(x86)",
        ):
            base_dir = os.environ.get(env_var)
            if base_dir:
                candidates.append(Path(base_dir) / "Tesseract-OCR" / "tesseract.exe")
                candidates.append(Path(base_dir) / "tesseract.exe")

        candidates.extend(
            [
                Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
                Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
            ]
        )

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        return None

    def __init__(
        self,
        tesseract_cmd: str | None = None,
    ):
        configured = tesseract_cmd or self.resolve_tesseract_path()
        if configured:
            pytesseract.pytesseract.tesseract_cmd = configured

    @staticmethod
    def is_available() -> bool:
        return OCRService.resolve_tesseract_path() is not None

    # ========================================================
    # FILE
    # ========================================================

    def extract_text(
        self,
        image_path: str | Path,
    ) -> str:

        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR is not installed or not on PATH. "
                "Install Tesseract OCR to extract text from scanned pages."
            )

        try:
            text = pytesseract.image_to_string(
                str(image_path),
                config="--psm 6",
            )
        except Exception as exc:
            raise RuntimeError(f"OCR failed: {exc}") from exc

        return text.strip()

    # ========================================================
    # BYTES
    # ========================================================

    def extract_bytes(
        self,
        image_bytes: bytes,
    ) -> str:

        image = Image.open(BytesIO(image_bytes))

        text = pytesseract.image_to_string(
            image,
            config="--psm 6",
        )

        return text.strip()

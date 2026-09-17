from __future__ import annotations

from pathlib import Path
import uuid

import pymupdf


class PDFProcessor:
    """
    Handles PDF loading, page rendering and diagram cropping.

    """

    def __init__(self):
        self.document = None
        self.source_path: Path | None = None

    # ========================================================
    # OPEN
    # ========================================================

    def open(self, path: str | Path):

        self.close()

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        self.document = pymupdf.open(str(path))
        self.source_path = path

        return {
            "name": path.name,
            "path": str(path),
            "pages": len(self.document),
        }

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        if self.document is not None:
            self.document.close()

        self.document = None
        self.source_path = None

    # ========================================================
    # PAGE COUNT
    # ========================================================

    @property
    def page_count(self):

        if self.document is None:
            return 0

        return len(self.document)

    # ========================================================
    # RENDER PAGE
    # ========================================================

    def render_page(
        self,
        page_number: int,
        scale: float = 1.5,
    ) -> bytes:

        self._ensure_open()

        page_index = page_number - 1

        if page_index < 0 or page_index >= len(self.document):
            raise IndexError(
                "Page number out of range."
            )

        page = self.document.load_page(page_index)

        matrix = pymupdf.Matrix(
            scale,
            scale,
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        return pixmap.tobytes("png")

    # ========================================================
    # RENDER THUMBNAIL
    # ========================================================

    def render_thumbnail(
        self,
        page_number: int,
    ) -> bytes:

        return self.render_page(
            page_number,
            scale=0.35,
        )

    # ========================================================
    # CROP PAGE
    # ========================================================

    def crop_page(
        self,
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        scale: float = 1.5,
    ) -> bytes:

        self._ensure_open()

        page_index = page_number - 1

        if page_index < 0 or page_index >= len(self.document):
            raise IndexError(
                "Page number out of range."
            )

        if width <= 0 or height <= 0:
            raise ValueError(
                "Crop dimensions must be greater than zero."
            )

        page = self.document.load_page(page_index)

        # Coordinates received from JavaScript are
        # relative to the rendered image.
        #
        # Convert them back to PDF coordinates.

        rect = pymupdf.Rect(
            x / scale,
            y / scale,
            (x + width) / scale,
            (y + height) / scale,
        )

        page_rect = page.rect

        rect = rect & page_rect

        if rect.is_empty:
            raise ValueError(
                "Selected crop is outside the page."
            )

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(
                scale,
                scale,
            ),
            clip=rect,
            alpha=False,
        )

        return pixmap.tobytes("png")

    # ========================================================
    # SAVE CROP
    # ========================================================

    def save_crop(
        self,
        image_bytes: bytes,
        question_id: int,
        image_position: int,
        image_type: str = "diagram",
        source_page: int | None = None,
    ) -> str:

        base_dir = Path(__file__).resolve().parents[2]

        image_dir = (
            base_dir
            / "data"
            / "question_images"
            / str(question_id)
        )

        image_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            f"{image_type}_{image_position}_"
            f"{uuid.uuid4().hex[:8]}.png"
        )

        image_path = image_dir / filename

        image_path.write_bytes(image_bytes)

        return str(
            image_path.relative_to(base_dir)
        ).replace("\\", "/")

    # ========================================================
    # INTERNAL
    # ========================================================

    def _ensure_open(self):

        if self.document is None:
            raise RuntimeError(
                "No PDF document is currently open."
            )
from __future__ import annotations

from pathlib import Path
import uuid

import pymupdf


class QuestionImportReviewService:
    def __init__(self):

        self.base_dir = Path(__file__).resolve().parent.parent

        self.storage_dir = self.base_dir / "storage" / "question_imports"

        self.source_dir = self.storage_dir / "source"

        self.pages_dir = self.storage_dir / "pages"

        self.source_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.pages_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ========================================================
    # PREPARE DOCUMENT
    # ========================================================

    def prepare_document(
        self,
        source_path: str,
    ) -> dict:

        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(f"Source file does not exist: {source}")

        extension = source.suffix.lower()

        if extension not in {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }:
            raise ValueError(
                "Unsupported file type. Supported types: PDF, PNG, JPG, JPEG, WEBP."
            )

        import_id = uuid.uuid4().hex

        import_dir = self.pages_dir / import_id

        import_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        if extension == ".pdf":
            return self._prepare_pdf(
                source,
                import_id,
                import_dir,
            )

        return self._prepare_image(
            source,
            import_id,
            import_dir,
        )

    # ========================================================
    # PDF
    # ========================================================

    def _prepare_pdf(
        self,
        source: Path,
        import_id: str,
        import_dir: Path,
    ) -> dict:

        document = pymupdf.open(
            str(source),
        )

        try:
            page_count = len(document)

            pages = []

            for index in range(page_count):
                page = document.load_page(
                    index,
                )

                matrix = pymupdf.Matrix(
                    2,
                    2,
                )

                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                page_number = index + 1

                output_path = import_dir / f"page_{page_number:04d}.png"

                pixmap.save(
                    str(output_path),
                )

                pages.append(
                    {
                        "page": page_number,
                        "image_path": str(output_path),
                        "image_url": output_path.as_uri(),
                    }
                )

            return {
                "success": True,
                "import_id": import_id,
                "source_type": "pdf",
                "source_path": str(source),
                "source_name": source.name,
                "page_count": page_count,
                "pages": pages,
            }

        finally:
            document.close()

    # ========================================================
    # IMAGE
    # ========================================================

    def _prepare_image(
        self,
        source: Path,
        import_id: str,
        import_dir: Path,
    ) -> dict:

        output_path = import_dir / f"page_0001{source.suffix.lower()}"

        output_path.write_bytes(
            source.read_bytes(),
        )

        return {
            "success": True,
            "import_id": import_id,
            "source_type": "image",
            "source_path": str(source),
            "source_name": source.name,
            "page_count": 1,
            "pages": [
                {
                    "page": 1,
                    "image_path": str(output_path),
                    "image_url": output_path.as_uri(),
                }
            ],
        }

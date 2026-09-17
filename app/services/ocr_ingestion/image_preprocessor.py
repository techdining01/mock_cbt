from __future__ import annotations

from pathlib import Path

import cv2


class ImagePreprocessor:
    def preprocess(
        self,
        image_path: str | Path,
        output_path: str | Path,
    ) -> str:

        image_path = str(image_path)
        output_path = Path(output_path)

        image = cv2.imread(
            image_path,
        )

        if image is None:
            raise ValueError(f"Unable to read image: {image_path}")

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        # Light denoising.
        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0,
        )

        # Thresholding.
        processed = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cv2.imwrite(
            str(output_path),
            processed,
        )

        return str(output_path)

from __future__ import annotations

import re


class QuestionParser:
    QUESTION_PATTERN = re.compile(
        r"(?mi)^\s*(?:q\.?|question|no\.?|num\.?)?\s*(\d{1,3})\s*[\.\)\]:\-–—]?\s*"
    )

    QUESTION_PATTERN_FALLBACK = re.compile(
        r"(?mi)(?:^|\n)\s*(?:q\.?|question|no\.?|num\.?)?\s*(\d{1,3})\s*[\.\)\]:\-–—]?\s+"
    )

    OPTION_PATTERN = re.compile(
        r"(?mi)(?:^|\n)\s*[\(\[]?\s*([A-E])\s*[\)\].:\-–—]?\s*"
    )

    OPTION_PATTERN_FALLBACK = re.compile(
        r"(?i)(?:^|\s)([A-E])\s*[\)\].:\-–—]\s*"
    )

    OPTION_PATTERN_INLINE = re.compile(
        r"(?i)\s[\(\[]?\s*([A-E])\s*[\)\].:\-–—]?\s+"
    )

    def parse(
        self,
        text: str,
    ) -> list[dict]:

        normalized_text = self._normalize_text(
            text
        )

        matches = list(
            self.QUESTION_PATTERN.finditer(
                normalized_text
            )
        )

        if len(matches) < 1:
            matches = list(
                self.QUESTION_PATTERN_FALLBACK.finditer(
                    normalized_text
                )
            )

        questions = []

        for index, match in enumerate(matches):
            question_number = int(match.group(1))

            start = match.end()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(normalized_text)

            block = normalized_text[
                start:end
            ].strip()

            question_text, options = (
                self._extract_question_parts(
                    block
                )
            )

            if not question_text and not options:
                continue

            questions.append(
                {
                    "question_number": question_number,
                    "text": question_text,
                    "options": options,
                    "images": [],
                }
            )

        return questions

    def _normalize_text(
        self,
        text: str,
    ) -> str:

        normalized = (
            text.replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("\u00a0", " ")
            .replace("\u2013", "-")
            .replace("\u2014", "-")
            .replace("\u2022", "-")
        )

        normalized = re.sub(
            r"(?<=[\dA-E])[\.\)\]:\-](?=[A-Za-z])",
            r"\g<0> ",
            normalized,
        )

        normalized = re.sub(
            r"(?mi)^\s*([A-E])\s{2,}",
            r"\1. ",
            normalized,
        )

        normalized = re.sub(
            r"(?mi)^\s*(\d{1,3})\s{2,}",
            r"\1. ",
            normalized,
        )

        normalized = re.sub(
            r"[ \t]+",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\n{3,}",
            "\n\n",
            normalized,
        )

        return normalized.strip()

    def _extract_question_parts(
        self,
        block: str,
    ) -> tuple[str, dict[str, str]]:

        option_matches = list(
            self.OPTION_PATTERN.finditer(block)
        )

        if len(option_matches) < 2:
            option_matches = list(
                self.OPTION_PATTERN_FALLBACK.finditer(block)
            )

        if len(option_matches) < 2:
            option_matches = list(
                self.OPTION_PATTERN_INLINE.finditer(block)
            )

        if not option_matches:
            return block.strip(), {}

        question_text = block[
            : option_matches[0].start()
        ].strip()

        options: dict[str, str] = {}

        for index, option_match in enumerate(option_matches):
            label = option_match.group(1).upper()

            start = option_match.end()

            if index + 1 < len(option_matches):
                end = option_matches[index + 1].start()
            else:
                end = len(block)

            option_text = block[start:end].strip(" \n\t-:")

            if option_text:
                options[label] = option_text

        return question_text, options

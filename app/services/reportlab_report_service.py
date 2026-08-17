from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


WIDTH, HEIGHT = A4


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = (
        text.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("&", "&amp;")
    )
    return text


class ReportlabReportService:
    """Generate polished PDF reports for exam results and student history using ReportLab."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def __init__(self, logo_path: str | Path | None = None):
        self.logo_path: Path | None = Path(logo_path) if logo_path else None

        styles = getSampleStyleSheet()

        self.styles = {
            "title": ParagraphStyle(
                "Title",
                parent=styles["Title"],
                fontSize=20,
                leading=24,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#1e3a8a"),
                spaceAfter=6,
            ),
            "subtitle": ParagraphStyle(
                "Subtitle",
                parent=styles["Normal"],
                fontSize=12,
                leading=15,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#334155"),
                spaceAfter=4,
            ),
            "h2": ParagraphStyle(
                "H2",
                parent=styles["Heading2"],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#0f172a"),
                spaceBefore=10,
                spaceAfter=6,
            ),
            "h3": ParagraphStyle(
                "H3",
                parent=styles["Heading3"],
                fontSize=12,
                leading=15,
                textColor=colors.HexColor("#1e293b"),
                spaceBefore=8,
                spaceAfter=4,
            ),
            "body": ParagraphStyle(
                "Body",
                parent=styles["BodyText"],
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#1f2937"),
            ),
            "body_bold": ParagraphStyle(
                "BodyBold",
                parent=styles["BodyText"],
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#111827"),
                fontName="Helvetica-Bold",
            ),
            "small": ParagraphStyle(
                "Small",
                parent=styles["Normal"],
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#475569"),
                alignment=TA_RIGHT,
            ),
            "question": ParagraphStyle(
                "Question",
                parent=styles["BodyText"],
                fontSize=10.5,
                leading=14,
                textColor=colors.HexColor("#0f172a"),
                fontName="Helvetica-Bold",
                spaceBefore=6,
            ),
            "option": ParagraphStyle(
                "Option",
                parent=styles["BodyText"],
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#1e293b"),
                leftIndent=14,
            ),
            "correct": ParagraphStyle(
                "Correct",
                parent=styles["BodyText"],
                fontSize=9.5,
                leading=12,
                textColor=colors.HexColor("#065f46"),
                fontName="Helvetica-Bold",
            ),
            "wrong": ParagraphStyle(
                "Wrong",
                parent=styles["BodyText"],
                fontSize=9.5,
                leading=12,
                textColor=colors.HexColor("#991b1b"),
                fontName="Helvetica-Bold",
            ),
            "explanation": ParagraphStyle(
                "Explanation",
                parent=styles["BodyText"],
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor("#1e3a8a"),
                leftIndent=8,
                rightIndent=8,
            ),
        }

    # ------------------------------------------------------------------
    def _add_header_footer(self, canvas, doc):
        """Draw watermark-style header / footer on every page."""
        canvas.saveState()

        # Header line
        canvas.setStrokeColor(colors.HexColor("#1e3a8a"))
        canvas.setLineWidth(1.5)
        canvas.line(2 * cm, HEIGHT - 1.8 * cm, WIDTH - 2 * cm, HEIGHT - 1.8 * cm)

        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(colors.HexColor("#1e3a8a"))
        canvas.drawString(2 * cm, HEIGHT - 1.6 * cm, "MOCK CBT EXAMINATION REPORT")

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawRightString(
            WIDTH - 2 * cm,
            HEIGHT - 1.6 * cm,
            "Generated: " + datetime.now().strftime("%d/%m/%Y %H:%M"),
        )

        # Footer
        canvas.setStrokeColor(colors.HexColor("#94a3b8"))
        canvas.setLineWidth(0.75)
        canvas.line(2 * cm, 1.6 * cm, WIDTH - 2 * cm, 1.6 * cm)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(2 * cm, 1.2 * cm, "Confidential - For Educational Use Only")
        canvas.drawRightString(
            WIDTH - 2 * cm,
            1.2 * cm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    def _build_logo(self, max_height_cm: float = 1.2) -> Image | None:
        if self.logo_path is None or not self.logo_path.exists():
            return None
        try:
            img = Image(str(self.logo_path))
            aspect = img.drawWidth / max(1, img.drawHeight)
            h = max_height_cm * cm
            w = h * aspect
            img.drawWidth = w
            img.drawHeight = h
            return img
        except Exception:
            return None

    def _summary_cards_table(self, data: list[list]) -> Table:
        tbl = Table(data, colWidths=[3.6 * cm] * len(data[0]), hAlign="CENTER")
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
                    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
                    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (-1, 1), 16),
                    ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0f172a")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#93c5fd")),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return tbl

    # ==================================================================
    # SINGLE EXAM RESULT
    # ==================================================================
    def generate_exam_result_pdf(
        self,
        output_path: str | Path,
        result: dict,
    ) -> Path:
        """Generate a detailed PDF for a single completed examination result.

        `result` must follow the shape returned by ExamService.get_result():
          - student_name, year, total, correct, wrong, unanswered, percentage
          - subjects[]: [{subject_id, subject_name, total, correct, wrong, percentage}]
          - review[]: [{subject_name, number, text, options[], correct_option_id,
                        selected_option_id, is_answered, is_correct, explanation}]
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.4 * cm,
            bottomMargin=2.2 * cm,
            title="Exam Result",
            author="Mock CBT System",
        )

        story: list = []

        # ----- Header -----
        logo = self._build_logo()
        header_row = [[logo or "", Paragraph(_clean_text(result.get("student_name") or "Student"), self.styles["title"])]]
        header_tbl = Table(header_row, colWidths=[2.2 * cm, 13 * cm], hAlign="CENTER")
        header_tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ]
            )
        )
        story.append(header_tbl)

        subtitle = (
            f"Examination Year: <b>{_clean_text(result.get('year', '-'))}</b>"
            "&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Date Printed: <b>{datetime.now().strftime('%d %B %Y')}</b>"
        )
        story.append(Paragraph(subtitle, self.styles["subtitle"]))
        story.append(Spacer(1, 0.15 * cm))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor("#93c5fd"),
                spaceAfter=0.2 * cm,
            )
        )

        # ----- Summary cards -----
        pct = _clean_text(result.get("percentage", 0))
        summary = self._summary_cards_table(
            [
                ["Total", "Correct", "Wrong", "Unanswered", "Percentage"],
                [
                    _clean_text(result.get("total", 0)),
                    _clean_text(result.get("correct", 0)),
                    _clean_text(result.get("wrong", 0)),
                    _clean_text(result.get("unanswered", 0)),
                    f"{pct}%",
                ],
            ]
        )
        story.append(summary)
        story.append(Spacer(1, 0.6 * cm))

        # ----- Subject performance -----
        story.append(Paragraph("Subject Performance", self.styles["h2"]))
        subjects = result.get("subjects", []) or []
        if subjects:
            subj_header = ["Subject", "Total", "Correct", "Wrong", "Percentage"]
            subj_data = [subj_header]
            for s in subjects:
                pct_s = f"{_clean_text(s.get('percentage', 0))}%"
                subj_data.append(
                    [
                        Paragraph(_clean_text(s.get("subject_name", "")), self.styles["body"]),
                        _clean_text(s.get("total", 0)),
                        _clean_text(s.get("correct", 0)),
                        _clean_text(s.get("wrong", 0)),
                        pct_s,
                    ]
                )
            subj_tbl = Table(
                subj_data,
                colWidths=[7 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.6 * cm],
                hAlign="LEFT",
            )
            subj_tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
                        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
                        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(subj_tbl)
        else:
            story.append(Paragraph("No subject breakdown available.", self.styles["body"]))

        story.append(PageBreak())

        # ----- Question review section -----
        story.append(Paragraph("Answer Review", self.styles["h2"]))
        story.append(
            Paragraph(
                "Each question below lists the options given, marks the correct answer, "
                "and indicates your answer.",
                self.styles["body"],
            )
        )
        story.append(Spacer(1, 0.3 * cm))

        review = result.get("review", []) or []
        if not review:
            story.append(Paragraph("No review data available.", self.styles["body"]))
        else:
            for i, q in enumerate(review, start=1):
                status_label = "Correct" if q.get("is_correct") else (
                    "Unanswered" if not q.get("is_answered") else "Wrong"
                )
                status_color = {
                    "Correct": colors.HexColor("#065f46"),
                    "Unanswered": colors.HexColor("#92400e"),
                    "Wrong": colors.HexColor("#991b1b"),
                }[status_label]

                q_label = (
                    f"<b>{_clean_text(q.get('subject_name', ''))} · Q{_clean_text(q.get('number', i))}"
                    f"</b>&nbsp;&nbsp;"
                    f"<font color='#{status_color.hexval()[2:]}'>[{status_label}]</font>"
                )
                story.append(Paragraph(q_label, self.styles["h3"]))

                q_text = _clean_text(q.get("text", ""))
                story.append(Paragraph(q_text, self.styles["question"]))

                options = q.get("options", []) or []
                correct_id = q.get("correct_option_id")
                selected_id = q.get("selected_option_id")

                for opt in options:
                    label = _clean_text(opt.get("label", "")).upper()
                    text = _clean_text(opt.get("text", ""))
                    opt_id = opt.get("id")
                    markers = []
                    if correct_id is not None and opt_id is not None and int(opt_id) == int(correct_id):
                        markers.append('<font color="#065f46"><b>[Correct]</b></font>')
                    if (
                        selected_id is not None
                        and opt_id is not None
                        and int(opt_id) == int(selected_id)
                        and not (
                            correct_id is not None
                            and opt_id is not None
                            and int(opt_id) == int(correct_id)
                        )
                    ):
                        markers.append('<font color="#991b1b"><b>[Your Answer]</b></font>')
                    elif (
                        selected_id is not None
                        and correct_id is not None
                        and opt_id is not None
                        and int(opt_id) == int(selected_id)
                        and int(opt_id) == int(correct_id)
                    ):
                        markers.append('<font color="#065f46"><b>[Your Answer · Correct]</b></font>')

                    bullet = f"<b>{label}.</b> {text} {' '.join(markers)}"
                    story.append(Paragraph(bullet, self.styles["option"]))

                # Answer summary row
                story.append(Spacer(1, 0.15 * cm))
                student_ans = _clean_text("Not answered")
                correct_ans = _clean_text("Not provided")
                for opt in options:
                    opt_id = opt.get("id")
                    label = _clean_text(opt.get("label", "")).upper()
                    txt = _clean_text(opt.get("text", ""))
                    if correct_id is not None and opt_id is not None and int(opt_id) == int(correct_id):
                        correct_ans = f"{label}. {txt}"
                    if selected_id is not None and opt_id is not None and int(opt_id) == int(selected_id):
                        student_ans = f"{label}. {txt}"

                summary_rows = [
                    [
                        Paragraph("<b>Your Answer</b>", self.styles["body"]),
                        Paragraph(student_ans, self.styles["body"]),
                    ],
                    [
                        Paragraph("<b>Correct Answer</b>", self.styles["body"]),
                        Paragraph(correct_ans, self.styles["body"]),
                    ],
                ]
                summary_tbl = Table(summary_rows, colWidths=[3.2 * cm, 13 * cm], hAlign="LEFT")
                summary_tbl.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                story.append(summary_tbl)

                # Explanation
                expl = q.get("explanation") or ""
                if str(expl).strip():
                    story.append(Spacer(1, 0.15 * cm))
                    story.append(Paragraph("<b>Explanation:</b>", self.styles["explanation"]))
                    story.append(
                        Paragraph(_clean_text(expl), self.styles["explanation"])
                    )

                story.append(Spacer(1, 0.4 * cm))
                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=0.3,
                        color=colors.HexColor("#e2e8f0"),
                        spaceAfter=0.2 * cm,
                    )
                )

        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        return output_path

    # ==================================================================
    # STUDENT HISTORY
    # ==================================================================
    def generate_student_history_pdf(
        self,
        output_path: str | Path,
        student_name: str,
        history: Iterable[dict],
    ) -> Path:
        """Generate a PDF report of a student's exam history.

        `history` is a list of dicts each containing:
            id, year, completed_at, total, correct, percentage,
            subjects[]: [{name, total, correct, percentage}]
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.4 * cm,
            bottomMargin=2.2 * cm,
            title="Student History Report",
            author="Mock CBT System",
        )

        story: list = []
        history_list = list(history)

        # ---- Header ----
        logo = self._build_logo()
        header_row = [[logo or "", Paragraph(_clean_text(student_name), self.styles["title"])]]
        header_tbl = Table(header_row, colWidths=[2.2 * cm, 13 * cm], hAlign="CENTER")
        header_tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ]
            )
        )
        story.append(header_tbl)
        story.append(Paragraph("Student Examination History Report", self.styles["subtitle"]))
        story.append(Spacer(1, 0.15 * cm))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor("#93c5fd"),
                spaceAfter=0.4 * cm,
            )
        )

        # ---- Aggregate summary ----
        total_sessions = len(history_list)
        if total_sessions:
            avg_pct = sum(
                float(h.get("percentage") or 0) for h in history_list
            ) / total_sessions
            total_questions = sum(int(h.get("total") or 0) for h in history_list)
            total_correct = sum(int(h.get("correct") or 0) for h in history_list)
        else:
            avg_pct = 0.0
            total_questions = 0
            total_correct = 0

        summary = self._summary_cards_table(
            [
                ["Sessions", "Questions Attempted", "Correct", "Average %"],
                [
                    str(total_sessions),
                    str(total_questions),
                    str(total_correct),
                    f"{avg_pct:.2f}%",
                ],
            ]
        )
        story.append(summary)
        story.append(Spacer(1, 0.6 * cm))

        # ---- History table ----
        story.append(Paragraph("Session Breakdown", self.styles["h2"]))
        if not history_list:
            story.append(Paragraph("No examination history found for this student.", self.styles["body"]))
        else:
            hist_header = [
                "Date",
                "Year",
                "Subjects",
                "Score",
                "%",
            ]
            hist_data = [hist_header]
            for h in history_list:
                subjects_bullets = "<br/>".join(
                    f"· {_clean_text(s.get('name', ''))}: "
                    f"<b>{_clean_text(s.get('correct', 0))}/{_clean_text(s.get('total', 0))}</b> "
                    f"({_clean_text(s.get('percentage', 0))}%)"
                    for s in (h.get("subjects", []) or [])
                ) or "-"
                pct_val = float(h.get("percentage") or 0)
                pct_cell = f"{pct_val:.2f}%"

                score_cell = (
                    f"<b>{_clean_text(h.get('correct', 0))}</b>/"
                    f"{_clean_text(h.get('total', 0))}"
                )

                hist_data.append(
                    [
                        Paragraph(_clean_text(h.get("completed_at", "-")), self.styles["body"]),
                        _clean_text(h.get("year", "-")),
                        Paragraph(subjects_bullets, self.styles["body"]),
                        Paragraph(score_cell, self.styles["body"]),
                        pct_cell,
                    ]
                )

            hist_tbl = Table(
                hist_data,
                repeatRows=1,
                colWidths=[3.2 * cm, 1.6 * cm, 7.6 * cm, 2.4 * cm, 2 * cm],
                hAlign="LEFT",
            )
            hist_tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ALIGN", (1, 0), (1, -1), "CENTER"),
                        ("ALIGN", (3, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(hist_tbl)

        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        return output_path

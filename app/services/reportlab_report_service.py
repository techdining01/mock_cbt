from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class ReportlabReportService:
    """
    Generates professional, high-fidelity PDF examination result transcripts
    using ReportLab.
    """

    def __init__(self, logo_path: Path | str | None = None):
        self.logo_path = self._resolve_logo_path(logo_path)

    def _resolve_logo_path(self, logo_input: Path | str | None = None) -> Path | None:
        """Resolves school logo image path from multiple possible relative or absolute locations."""
        base_dir = Path(__file__).resolve().parents[2]

        # 1. If explicit path/string provided
        if logo_input:
            if isinstance(logo_input, str) and logo_input.startswith("data:image"):
                try:
                    import base64
                    import tempfile
                    header, encoded = logo_input.split(",", 1)
                    ext = ".png" if "png" in header else ".jpg"
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                    tmp.write(base64.b64decode(encoded))
                    tmp.close()
                    return Path(tmp.name)
                except Exception:
                    pass

            cleaned_str = str(logo_input).split("?")[0].strip()
            if cleaned_str:
                candidates = [
                    Path(cleaned_str),
                    base_dir / cleaned_str,
                    base_dir / "app" / "web" / cleaned_str,
                    base_dir / "app" / "web" / "images" / Path(cleaned_str).name,
                ]
                for c in candidates:
                    if c.exists() and c.is_file():
                        return c

        # 2. Check self.logo_path if set
        if hasattr(self, "logo_path") and self.logo_path and Path(self.logo_path).exists():
            return Path(self.logo_path)

        # 3. Fallback candidates in app/web/images
        fallback_candidates = [
            base_dir / "app" / "web" / "images" / "school_logo_custom.png",
            base_dir / "app" / "web" / "images" / "school_logo_custom.jpg",
            base_dir / "app" / "web" / "images" / "school_logo.png",
            base_dir / "app" / "web" / "images" / "school_logo.ico",
        ]
        for fb in fallback_candidates:
            if fb.exists() and fb.is_file():
                return fb

        return None

    def _get_grade_and_remark(self, percentage: float) -> tuple[str, str, colors.Color]:
        """Returns grade letter, descriptive remark, and badge color."""
        pct = float(percentage or 0)
        if pct >= 75.0:
            return "A", "DISTINCTION / EXCELLENT", colors.HexColor("#15803d")
        elif pct >= 65.0:
            return "B", "VERY GOOD / CREDIT", colors.HexColor("#1d4ed8")
        elif pct >= 50.0:
            return "C", "CREDIT / GOOD", colors.HexColor("#0284c7")
        elif pct >= 40.0:
            return "D", "PASS", colors.HexColor("#d97706")
        else:
            return "F", "NEEDS IMPROVEMENT", colors.HexColor("#b91c1c")

    def generate(
        self,
        result: Dict[str, Any],
        output_path: str | Path | None = None,
        school_name: str | None = None,
        school_address: str | None = None,
        school_logo_path: str | Path | None = None,
    ) -> str:
        """
        Builds the PDF result sheet and saves it to output_path.
        Returns the absolute string path to the generated PDF.

        Args:
            result: Exam result data dictionary
            output_path: Path to save the PDF (optional)
            school_name: School/institution name (optional)
            school_address: School address (optional)
            school_logo_path: Path to school logo image (optional)
        """
        student_name = str(result.get("student_name") or result.get("student_full_name") or "Candidate").strip()
        safe_student_name = "".join(c if c.isalnum() else "_" for c in student_name)[:30]
        year = result.get("year", datetime.now().year)

        # Use provided settings or defaults
        school_name = school_name or "LLS Computer-Based Testing (CBT) Software"
        school_address = school_address or ""
        school_logo_path = self._resolve_logo_path(school_logo_path)

        if not output_path:
            # Default to user's Downloads or Documents directory
            downloads_dir = Path(os.environ.get("USERPROFILE", ".")) / "Downloads"
            if not downloads_dir.exists():
                downloads_dir = Path(os.environ.get("USERPROFILE", ".")) / "Documents"
            if not downloads_dir.exists():
                downloads_dir = Path(__file__).resolve().parents[2] / "data"
                downloads_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = downloads_dir / f"CBT_Result_{safe_student_name}_{year}_{timestamp}.pdf"
        else:
            output_file = Path(output_path)

        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom paragraph styles
        primary_color = colors.HexColor("#1e3a8a")   # Deep navy blue
        accent_color = colors.HexColor("#2563eb")    # Royal blue
        dark_text = colors.HexColor("#0f172a")       # Slate 900
        muted_text = colors.HexColor("#475569")      # Slate 600

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=primary_color,
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=accent_color,
        )

        institution_meta = ParagraphStyle(
            "InstMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=muted_text,
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=primary_color,
            spaceAfter=6,
        )

        cell_style = ParagraphStyle(
            "CellNormal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=dark_text,
        )

        cell_bold = ParagraphStyle(
            "CellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=dark_text,
        )

        cell_center = ParagraphStyle(
            "CellCenter",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=dark_text,
        )

        cell_header = ParagraphStyle(
            "CellHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.white,
        )

        cell_header_left = ParagraphStyle(
            "CellHeaderLeft",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            textColor=colors.white,
        )

        story = []
        raw_body = str(result.get("exam_body") or "JAMB").upper().strip()
        if raw_body in ["SCHOOL", "PROPRIETARY"]:
            body_display = "School Internal Examination"
            exam_title_badge = "SCHOOL INTERNAL EXAMINATION"
        else:
            body_display = f"{raw_body} Mock"
            exam_title_badge = f"{raw_body} MOCK"

        # ========================================================
        # 1. HEADER SECTION (Logo + Title)
        # ========================================================
        header_table_data = []
        if school_logo_path and school_logo_path.exists():
            try:
                logo_img = Image(str(school_logo_path), width=58, height=58)
                header_text = [
                    Paragraph(school_name.upper(), title_style),
                    Spacer(1, 2),
                    Paragraph(f"OFFICIAL {exam_title_badge} EXAMINATION TRANSCRIPT", subtitle_style),
                    Spacer(1, 2),
                    Paragraph(f"Assessment Body: {body_display} · Academic Assessment Year: {year}", institution_meta),
                ]
                if school_address:
                    header_text.append(Spacer(1, 1))
                    header_text.append(Paragraph(school_address, institution_meta))
                header_table_data.append([logo_img, header_text])
                header_table = Table(header_table_data, colWidths=[68, 454])
                header_table.setStyle(
                    TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ])
                )
                story.append(header_table)
            except Exception:
                story.append(Paragraph(school_name.upper(), title_style))
                story.append(Spacer(1, 2))
                story.append(Paragraph(f"OFFICIAL {exam_title_badge} EXAMINATION TRANSCRIPT", subtitle_style))
                if school_address:
                    story.append(Spacer(1, 2))
                    story.append(Paragraph(school_address, institution_meta))
        else:
            story.append(Paragraph(school_name.upper(), title_style))
            story.append(Spacer(1, 2))
            story.append(Paragraph(f"OFFICIAL {exam_title_badge} EXAMINATION TRANSCRIPT", subtitle_style))
            story.append(Spacer(1, 2))
            story.append(Paragraph(f"Assessment Body: {body_display} · Academic Assessment Year: {year}", institution_meta))
            if school_address:
                story.append(Spacer(1, 1))
                story.append(Paragraph(school_address, institution_meta))

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=12))

        # ========================================================
        # 2. CANDIDATE PROFILE & META DATA
        # ========================================================
        total_questions = result.get("total", 0)
        correct_count = result.get("correct", 0)
        wrong_count = result.get("wrong", 0)
        unanswered_count = result.get("unanswered", 0)
        pct_value = float(result.get("percentage", 0.0))
        grade_letter, remark_text, badge_color = self._get_grade_and_remark(pct_value)

        current_date_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
        exam_session_id = f"CBT-{result.get('exam_id', '0000'):05d}" if isinstance(result.get("exam_id"), int) else f"CBT-{result.get('exam_id', '0000')}"

        meta_data = [
            [
                Paragraph("<b>Candidate Name:</b>", cell_style),
                Paragraph(f"<font color='#1e3a8a'><b>{student_name}</b></font>", cell_bold),
                Paragraph("<b>Session ID:</b>", cell_style),
                Paragraph(exam_session_id, cell_bold),
            ],
            [
                Paragraph("<b>Assessment Type:</b>", cell_style),
                Paragraph(f"<font color='#2563eb'><b>{body_display} Exam</b></font>", cell_bold),
                Paragraph("<b>Exam Year:</b>", cell_style),
                Paragraph(str(year), cell_bold),
            ],
        ]

        meta_table = Table(meta_data, colWidths=[110, 160, 110, 142])
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # ========================================================
        # 3. SCORE SUMMARY CARDS
        # ========================================================
        summary_cards_data = [
            [
                Paragraph("<b>TOTAL QUESTIONS</b>", ParagraphStyle("CardHead", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=muted_text)),
                Paragraph("<b>CORRECT</b>", ParagraphStyle("CardHead", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#166534"))),
                Paragraph("<b>WRONG</b>", ParagraphStyle("CardHead", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#991b1b"))),
                Paragraph("<b>UNANSWERED</b>", ParagraphStyle("CardHead", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#92400e"))),
                Paragraph("<b>SCORE PERCENT</b>", ParagraphStyle("CardHead", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=primary_color)),
            ],
            [
                Paragraph(f"<font size='14'><b>{total_questions}</b></font>", ParagraphStyle("Val", parent=styles["Normal"], alignment=TA_CENTER, textColor=dark_text)),
                Paragraph(f"<font size='14'><b>{correct_count}</b></font>", ParagraphStyle("Val", parent=styles["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#15803d"))),
                Paragraph(f"<font size='14'><b>{wrong_count}</b></font>", ParagraphStyle("Val", parent=styles["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#b91c1c"))),
                Paragraph(f"<font size='14'><b>{unanswered_count}</b></font>", ParagraphStyle("Val", parent=styles["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#d97706"))),
                Paragraph(f"<font size='14'><b>{pct_value:.1f}%</b></font>", ParagraphStyle("Val", parent=styles["Normal"], alignment=TA_CENTER, textColor=primary_color)),
            ],
        ]

        summary_table = Table(summary_cards_data, colWidths=[104, 104, 104, 104, 106])
        summary_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, 1), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (1, 0), (1, 1), colors.HexColor("#f0fdf4")),
                ("BACKGROUND", (2, 0), (2, 1), colors.HexColor("#fef2f2")),
                ("BACKGROUND", (3, 0), (3, 1), colors.HexColor("#fffbeb")),
                ("BACKGROUND", (4, 0), (4, 1), colors.HexColor("#eff6ff")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
            ])
        )
        story.append(summary_table)
        story.append(Spacer(1, 10))

        # Grade banner
        grade_banner_data = [[
            Paragraph(f"<b>FINAL GRADE:</b> <font color='{badge_color.hexval()}'><b>Grade {grade_letter} ({remark_text})</b></font>", ParagraphStyle("GradeBanner", parent=styles["Normal"], fontName="Helvetica", fontSize=10, alignment=TA_CENTER, textColor=dark_text))
        ]]
        grade_table = Table(grade_banner_data, colWidths=[522])
        grade_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(grade_table)
        story.append(Spacer(1, 16))

        # ========================================================
        # 4. SUBJECT BREAKDOWN TABLE
        # ========================================================
        story.append(Paragraph("Subject-by-Subject Performance", section_heading))

        subject_rows = result.get("subjects") or []
        table_rows = [
            [
                Paragraph("<b>Subject Name</b>", cell_header_left),
                Paragraph("<b>Total</b>", cell_header),
                Paragraph("<b>Correct</b>", cell_header),
                Paragraph("<b>Wrong</b>", cell_header),
                Paragraph("<b>Unanswered</b>", cell_header),
                Paragraph("<b>Percentage</b>", cell_header),
                Paragraph("<b>Grade</b>", cell_header),
            ]
        ]

        for s in subject_rows:
            s_name = s.get("subject_name", "Subject")
            s_total = s.get("total", 0)
            s_correct = s.get("correct", 0)
            s_wrong = s.get("wrong", 0)
            s_unanswered = s.get("unanswered", 0)
            s_pct = float(s.get("percentage", 0.0))
            s_grade, _, _ = self._get_grade_and_remark(s_pct)

            table_rows.append([
                Paragraph(s_name, cell_bold),
                Paragraph(str(s_total), cell_center),
                Paragraph(f"<font color='#15803d'><b>{s_correct}</b></font>", cell_center),
                Paragraph(f"<font color='#b91c1c'>{s_wrong}</font>", cell_center),
                Paragraph(f"<font color='#d97706'>{s_unanswered}</font>", cell_center),
                Paragraph(f"<b>{s_pct:.1f}%</b>", cell_center),
                Paragraph(f"<b>{s_grade}</b>", cell_center),
            ])

        # Add total/cumulative row
        table_rows.append([
            Paragraph("<b>OVERALL CUMULATIVE</b>", cell_bold),
            Paragraph(f"<b>{total_questions}</b>", cell_center),
            Paragraph(f"<font color='#15803d'><b>{correct_count}</b></font>", cell_center),
            Paragraph(f"<font color='#b91c1c'><b>{wrong_count}</b></font>", cell_center),
            Paragraph(f"<font color='#d97706'><b>{unanswered_count}</b></font>", cell_center),
            Paragraph(f"<b>{pct_value:.1f}%</b>", cell_center),
            Paragraph(f"<b>{grade_letter}</b>", cell_center),
        ])

        subj_table = Table(table_rows, colWidths=[162, 60, 60, 60, 60, 60, 60])
        table_styles = [
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
        ]

        # Alternating row background for body
        for i in range(1, len(table_rows) - 1):
            if i % 2 == 0:
                table_styles.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafc")))

        subj_table.setStyle(TableStyle(table_styles))
        story.append(subj_table)
        # ========================================================
        # 5. LEGAL DISCLAIMER & PRACTICE NOTICE
        # ========================================================
        disclaimer_text = (
            f"<b>LEGAL NOTICE & DISCLAIMER:</b> This document is an unofficial simulated mock practice transcript "
            f"generated by {school_name} for candidate preparatory and academic diagnostic assessment purposes only. "
            f"It is not an official result certificate issued by JAMB, WAEC, NECO, NABTEB, or any statutory examination councils."
        )
        disclaimer_box = Table(
            [[Paragraph(f"<font size='7' color='#475569'>{disclaimer_text}</font>", cell_style)]],
            colWidths=[522],
        )
        disclaimer_box.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(disclaimer_box)
        story.append(Spacer(1, 12))

        # ========================================================
        # 6. AUTHENTICATION & SIGNOFF FOOTER
        # ========================================================
        footer_data = [
            [
                Paragraph("<b>Candidate Signature:</b> ___________________", cell_style),
                Paragraph("<b>Examiner / Administrator:</b> ___________________", cell_style),
            ],
            [
                Spacer(1, 10),
                Spacer(1, 10),
            ],
            [
                Paragraph("<font size='7' color='#64748b'>Certified Mock CBT Examination Transcript · Any alteration invalidates this document.</font>", ParagraphStyle("Fine", parent=styles["Normal"], alignment=TA_LEFT)),
                Paragraph(f"<font size='7' color='#64748b'>Generated: {current_date_str}</font>", ParagraphStyle("FineR", parent=styles["Normal"], alignment=TA_RIGHT)),
            ]
        ]

        footer_table = Table(footer_data, colWidths=[300, 222])
        footer_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ])
        )

        story.append(KeepTogether([
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10),
            footer_table,
        ]))

        # Build document
        doc.build(story)
        return str(output_file.resolve())

    def generate_exam_result_pdf(
        self,
        output_path: str | Path,
        result: dict,
        school_name: str | None = None,
        school_address: str | None = None,
        school_logo_path: str | Path | None = None,
    ) -> Path:
        """Alias for generate() to maintain compatibility with existing code."""
        return Path(self.generate(
            result,
            output_path=output_path,
            school_name=school_name,
            school_address=school_address,
            school_logo_path=school_logo_path,
        ))

    def generate_student_history(
        self,
        student_name: str,
        sessions: list[dict],
        user_info: dict | None = None,
        output_path: str | Path | None = None,
        school_name: str | None = None,
        school_address: str | None = None,
        school_logo_path: str | Path | None = None,
    ) -> str:
        """
        Builds a comprehensive multi-exam historical transcript for a student.

        Args:
            student_name: Student's name
            sessions: List of exam session dictionaries
            user_info: Additional user information (optional)
            output_path: Path to save the PDF (optional)
            school_name: School/institution name (optional)
            school_address: School address (optional)
            school_logo_path: Path to school logo image (optional)
        """
        student_display = str(student_name or "Student").strip()
        safe_name = "".join(c if c.isalnum() else "_" for c in student_display)[:30]

        # Use provided settings or defaults
        school_name = school_name or "Mock CBT Examination"
        school_address = school_address or ""
        school_logo_path = self._resolve_logo_path(school_logo_path)

        if not output_path:
            downloads_dir = Path(os.environ.get("USERPROFILE", ".")) / "Downloads"
            if not downloads_dir.exists():
                downloads_dir = Path(os.environ.get("USERPROFILE", ".")) / "Documents"
            if not downloads_dir.exists():
                downloads_dir = Path(__file__).resolve().parents[2] / "data"
                downloads_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = downloads_dir / f"CBT_History_{safe_name}_{timestamp}.pdf"
        else:
            output_file = Path(output_path)

        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#1e3a8a")
        accent_color = colors.HexColor("#2563eb")
        dark_text = colors.HexColor("#0f172a")
        muted_text = colors.HexColor("#475569")

        title_style = ParagraphStyle("HistTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=17, leading=21, alignment=TA_CENTER, textColor=primary_color)
        subtitle_style = ParagraphStyle("HistSub", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, leading=15, alignment=TA_CENTER, textColor=accent_color)
        meta_style = ParagraphStyle("HistMeta", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, alignment=TA_CENTER, textColor=muted_text)
        cell_style = ParagraphStyle("HistCell", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, textColor=dark_text)
        cell_bold = ParagraphStyle("HistBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=dark_text)
        cell_center = ParagraphStyle("HistCenter", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=dark_text)
        cell_head = ParagraphStyle("HistHead", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.white)
        cell_head_left = ParagraphStyle("HistHeadL", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, alignment=TA_LEFT, textColor=colors.white)

        story = []

        # 1. Header
        if school_logo_path and school_logo_path.exists():
            try:
                logo_img = Image(str(school_logo_path), width=54, height=54)
                header_text = [
                    Paragraph(school_name.upper(), title_style),
                    Spacer(1, 2),
                    Paragraph("STUDENT COMPREHENSIVE EXAMINATION HISTORY", subtitle_style),
                    Spacer(1, 2),
                    Paragraph("Cumulative Academic Performance Record", meta_style),
                ]
                if school_address:
                    header_text.append(Spacer(1, 1))
                    header_text.append(Paragraph(school_address, meta_style))
                h_table = Table([[logo_img, header_text]], colWidths=[64, 458])
                h_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
                story.append(h_table)
            except Exception:
                story.append(Paragraph(school_name.upper(), title_style))
                story.append(Spacer(1, 2))
                story.append(Paragraph("STUDENT COMPREHENSIVE EXAMINATION HISTORY", subtitle_style))
                if school_address:
                    story.append(Spacer(1, 2))
                    story.append(Paragraph(school_address, meta_style))
        else:
            story.append(Paragraph(school_name.upper(), title_style))
            story.append(Spacer(1, 2))
            story.append(Paragraph("STUDENT COMPREHENSIVE EXAMINATION HISTORY", subtitle_style))
            story.append(Spacer(1, 2))
            story.append(Paragraph("Cumulative Academic Performance Record", meta_style))
            if school_address:
                story.append(Spacer(1, 1))
                story.append(Paragraph(school_address, meta_style))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=10))

        # 2. Student Info Card
        total_exams = len(sessions)
        avg_pct = (sum(float(s.get("percentage", 0)) for s in sessions) / total_exams) if total_exams else 0.0
        best_pct = max((float(s.get("percentage", 0)) for s in sessions), default=0.0)
        overall_grade, overall_remark, grade_color = self._get_grade_and_remark(avg_pct)

        student_class = (user_info.get("student_class") if user_info else "") or "N/A"
        adm_year = str((user_info.get("admission_year") if user_info else "") or "N/A")

        prof_data = [
            [
                Paragraph("<b>Candidate Name:</b>", cell_style),
                Paragraph(f"<font color='#1e3a8a'><b>{student_display}</b></font>", cell_bold),
                Paragraph("<b>Class:</b>", cell_style),
                Paragraph(student_class, cell_bold),
            ],
            [
                Paragraph("<b>Total Exams Taken:</b>", cell_style),
                Paragraph(str(total_exams), cell_bold),
                Paragraph("<b>Admission Year:</b>", cell_style),
                Paragraph(adm_year, cell_style),
            ],
            [
                Paragraph("<b>Average Score:</b>", cell_style),
                Paragraph(f"<b>{avg_pct:.1f}%</b>", cell_bold),
                Paragraph("<b>Best Score:</b>", cell_style),
                Paragraph(f"<font color='#15803d'><b>{best_pct:.1f}%</b></font>", cell_bold),
            ],
        ]

        prof_table = Table(prof_data, colWidths=[115, 155, 110, 142])
        prof_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(prof_table)
        story.append(Spacer(1, 14))

        # 3. History Table
        story.append(Paragraph("<b>Examination History Breakdown</b>", ParagraphStyle("HistSec", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, textColor=primary_color, spaceAfter=6)))

        table_rows = [
            [
                Paragraph("<b>Date / Time</b>", cell_head_left),
                Paragraph("<b>Year</b>", cell_head),
                Paragraph("<b>Subjects</b>", cell_head_left),
                Paragraph("<b>Questions</b>", cell_head),
                Paragraph("<b>Correct</b>", cell_head),
                Paragraph("<b>Wrong</b>", cell_head),
                Paragraph("<b>Score %</b>", cell_head),
                Paragraph("<b>Grade</b>", cell_head),
            ]
        ]

        for s in sessions:
            date_str = s.get("date_formatted") or s.get("completed_at") or s.get("started_at") or "N/A"
            if len(date_str) > 16:
                date_str = date_str[:16]
            y = str(s.get("year", ""))
            subjects_list = s.get("subjects", [])
            if subjects_str := s.get("subjects_str"):
                subjs = subjects_str
            elif subjects_list:
                # Handle both string and dict subjects
                subjs = ", ".join(
                    subj if isinstance(subj, str) else subj.get("subject_name", subj.get("name", str(subj)))
                    for subj in subjects_list
                )
            else:
                subjs = "Exam"
            tot = s.get("total", 0)
            cor = s.get("correct", 0)
            wro = s.get("wrong", 0)
            pct = float(s.get("percentage", 0.0))
            g, _, _ = self._get_grade_and_remark(pct)

            table_rows.append([
                Paragraph(date_str, cell_style),
                Paragraph(y, cell_center),
                Paragraph(subjs, cell_style),
                Paragraph(str(tot), cell_center),
                Paragraph(f"<font color='#15803d'><b>{cor}</b></font>", cell_center),
                Paragraph(f"<font color='#b91c1c'>{wro}</font>", cell_center),
                Paragraph(f"<b>{pct:.1f}%</b>", cell_center),
                Paragraph(f"<b>{g}</b>", cell_center),
            ])

        hist_table = Table(table_rows, colWidths=[90, 36, 170, 52, 45, 45, 48, 36])
        t_styles = [
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]

        for i in range(1, len(table_rows)):
            if i % 2 == 0:
                t_styles.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafc")))

        hist_table.setStyle(TableStyle(t_styles))
        story.append(hist_table)
        story.append(Spacer(1, 20))

        # 4. Signoff Footer
        gen_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")
        footer_data = [
            [
                Paragraph("<b>School Administrator:</b> ___________________", cell_style),
                Paragraph("<b>Official Stamp:</b> [ SEAL ]", ParagraphStyle("Stamp", parent=styles["Normal"], alignment=TA_RIGHT, fontName="Helvetica-Bold", textColor=muted_text)),
            ],
            [
                Spacer(1, 8),
                Spacer(1, 8),
            ],
            [
                Paragraph(f"<font size='7' color='#64748b'>Certified official transcript from Mock CBT System · Generated {gen_time}</font>", ParagraphStyle("HistFine", parent=styles["Normal"])),
                Paragraph("", cell_style),
            ]
        ]

        f_table = Table(footer_data, colWidths=[320, 202])
        f_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))

        story.append(KeepTogether([
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10),
            f_table,
        ]))

        doc.build(story)
        return str(output_file.resolve())

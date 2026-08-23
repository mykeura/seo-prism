"""
SEO Report PDF Generator Module

Generates professional executive PDF reports with SEO analysis results.
Every detected issue is included (zero truncation) with automatic
pagination, so no manual tweaks are ever needed regardless of how many
issues the scan found. Supports bilingual reports (Spanish/English) with
a sober corporate design and a prism-spectrum brand accent.

This is the default report format of the CLI; the PowerPoint generator in
report_generator.py remains available as an editable option.
"""

from datetime import datetime
from xml.sax.saxutils import escape
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    LongTable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .report_translations import get_translation, get_impact_template


class SEOReportPDFGenerator:
    """Generates executive SEO reports in PDF format with zero truncation."""

    # Sober professional palette: dark grays + one blue accent.
    # Severity colors are only used inside the severity cells.
    THEME = {
        'primary': colors.HexColor('#1F2937'),     # Dark gray (titles/header)
        'secondary': colors.HexColor('#4B5563'),   # Mid gray
        'text': colors.HexColor('#111827'),        # Body text
        'text_light': colors.HexColor('#6B7280'),  # Captions
        'line': colors.HexColor('#E5E7EB'),        # Table grid
        'row_alt': colors.HexColor('#F3F4F6'),     # Alternating rows (visible zebra)
        'card_bg': colors.HexColor('#F3F4F6'),     # Metric cards
        'accent': colors.HexColor('#2563EB'),      # Blue accent
        'high': colors.HexColor('#B91C1C'),        # Subtle red
        'medium': colors.HexColor('#B45309'),      # Subtle amber
        'low': colors.HexColor('#1D4ED8'),         # Subtle blue
        'high_bg': colors.HexColor('#FEF2F2'),     # Light red tint
        'grade_a': colors.HexColor('#15803D'),
        'grade_b': colors.HexColor('#2563EB'),
        'grade_c': colors.HexColor('#B45309'),
        'grade_d': colors.HexColor('#C2410C'),
        'grade_f': colors.HexColor('#B91C1C'),
    }

    # Prism-spectrum brand band (muted, professional rainbow).
    PRISM_COLORS = (
        colors.HexColor('#DC2626'),
        colors.HexColor('#EA580C'),
        colors.HexColor('#CA8A04'),
        colors.HexColor('#16A34A'),
        colors.HexColor('#2563EB'),
        colors.HexColor('#4F46E5'),
        colors.HexColor('#7C3AED'),
    )

    PAGE_W, PAGE_H = A4
    MARGIN = 1.6 * cm
    CONTENT_W = A4[0] - 2 * MARGIN  # usable width

    SEVERITY_WEIGHT = {'high': 3, 'medium': 2, 'low': 1}

    def __init__(self, custom_theme: dict = None):
        """
        Initialize the PDF report generator.

        Args:
            custom_theme: Optional dictionary of custom colors to override defaults
        """
        self.theme = {k: (v if not isinstance(v, tuple) else colors.HexColor('#%02X%02X%02X' % v))
                      for k, v in self.THEME.copy().items()}
        if custom_theme:
            self.theme.update(custom_theme)

        self._lang = 'en'
        self._scan_url = ''
        self._report_title = ''
        self._build_styles()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def generate_report(self, results: dict, output_path: str, lang: str = 'en') -> str:
        """
        Generate a professional executive SEO report in PDF format.

        Every issue in results['issues'] is rendered: one section per
        category with a paginating table (header repeated on each page).

        Args:
            results: Scan results dictionary with scan info, issues, pages,
                     seo_grade and resource_analysis
            output_path: Path where the PDF file will be saved
            lang: Language code ('es' or 'en')

        Returns:
            Path to the generated PDF file
        """
        self._lang = lang if lang in ('es', 'en') else 'en'
        scan = results.get('scan', {})
        self._scan_url = scan.get('url', '') or ''
        self._report_title = get_translation(self._lang, 'report_title')

        output_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(output_dir, exist_ok=True)

        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            title=f"SEO Prism — {self._report_title} — {self._scan_url}",
            author='SEO Prism',
            subject=self._report_title,
        )

        cover_frame = Frame(
            self.MARGIN, 1.3 * cm, self.CONTENT_W,
            self.PAGE_H - 2.4 * cm - 1.3 * cm, id='cover',
        )
        body_frame = Frame(
            self.MARGIN, 1.35 * cm, self.CONTENT_W,
            self.PAGE_H - 52 - 1.35 * cm, id='body',
        )
        doc.addPageTemplates([
            PageTemplate(id='Cover', frames=[cover_frame], onPage=self._draw_cover_page),
            PageTemplate(id='Body', frames=[body_frame], onPage=self._draw_body_page),
        ])

        story = [NextPageTemplate('Body')]
        story.extend(self._cover_flowables(results, self._lang))
        story.append(PageBreak())
        story.extend(self._executive_summary_flowables(results, self._lang))
        story.append(PageBreak())
        story.extend(self._catalog_flowables(results, self._lang))
        story.append(PageBreak())
        story.extend(self._recommendations_flowables(results, self._lang))
        story.extend(self._notes_flowables(self._lang))

        doc.build(story)
        return output_path

    # ------------------------------------------------------------------ #
    # Styles
    # ------------------------------------------------------------------ #

    def _build_styles(self):
        """Create the paragraph styles used across the report."""
        t = self.theme
        self.styles = {
            'brand': ParagraphStyle(
                'brand', fontName='Helvetica-Bold', fontSize=38, leading=42,
                alignment=TA_CENTER, textColor=t['primary']),
            'tagline': ParagraphStyle(
                'tagline', fontName='Helvetica', fontSize=11, leading=14,
                alignment=TA_CENTER, textColor=t['text_light']),
            'cover_title': ParagraphStyle(
                'cover_title', fontName='Helvetica-Bold', fontSize=22, leading=27,
                alignment=TA_CENTER, textColor=t['secondary']),
            'cover_sub': ParagraphStyle(
                'cover_sub', fontName='Helvetica', fontSize=13, leading=17,
                alignment=TA_CENTER, textColor=t['text_light']),
            'cover_info': ParagraphStyle(
                'cover_info', fontName='Helvetica', fontSize=11, leading=16,
                alignment=TA_CENTER, textColor=t['text']),
            'grade_letter': ParagraphStyle(
                'grade_letter', fontName='Helvetica-Bold', fontSize=44, leading=48,
                alignment=TA_CENTER, textColor=colors.white),
            'grade_info': ParagraphStyle(
                'grade_info', fontName='Helvetica', fontSize=10, leading=15,
                alignment=TA_LEFT, textColor=t['text']),
            'h1': ParagraphStyle(
                'h1', fontName='Helvetica-Bold', fontSize=15, leading=19,
                textColor=t['primary'], spaceBefore=2, spaceAfter=3, keepWithNext=1),
            # NOTE: keepWithNext is intentionally NOT set on h2/body_small:
            # reportlab moves the whole keep-with-next group (heading + impact
            # note + the huge LongTable) to a fresh page and then splits the
            # table with the leftover height, leaving a near-empty page and a
            # 2-row first chunk.
            'h2': ParagraphStyle(
                'h2', fontName='Helvetica-Bold', fontSize=11.5, leading=15,
                textColor=t['primary'], spaceBefore=14, spaceAfter=4),
            'body': ParagraphStyle(
                'body', fontName='Helvetica', fontSize=9.5, leading=13.5,
                textColor=t['text'], spaceAfter=6),
            'body_small': ParagraphStyle(
                'body_small', fontName='Helvetica', fontSize=8.5, leading=12,
                textColor=t['text_light'], spaceAfter=6),
            'note_italic': ParagraphStyle(
                'note_italic', fontName='Helvetica-Oblique', fontSize=8.5,
                leading=12, textColor=t['text_light'], spaceAfter=6),
            'metric_value': ParagraphStyle(
                'metric_value', fontName='Helvetica-Bold', fontSize=16, leading=19,
                alignment=TA_CENTER, textColor=t['primary']),
            'metric_label': ParagraphStyle(
                'metric_label', fontName='Helvetica', fontSize=7.5, leading=10,
                alignment=TA_CENTER, textColor=t['text_light']),
            # Table cells: URLs wrap anywhere (CJK) so they never overflow.
            'cell_url': ParagraphStyle(
                'cell_url', fontName='Helvetica', fontSize=7.5, leading=9.5,
                wordWrap='CJK', textColor=t['secondary']),
            'cell': ParagraphStyle(
                'cell', fontName='Helvetica', fontSize=7.5, leading=9.5,
                splitLongWords=1, textColor=t['text']),
            'cell_sev': ParagraphStyle(
                'cell_sev', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5,
                alignment=TA_CENTER, textColor=t['text']),
            'critical': ParagraphStyle(
                'critical', fontName='Helvetica', fontSize=9, leading=13,
                textColor=t['text']),
        }

    # ------------------------------------------------------------------ #
    # Page decorations (header / footer / prism band)
    # ------------------------------------------------------------------ #

    def _draw_spectrum(self, canvas, y, height):
        """Draw the prism-spectrum band as a row of rainbow rects."""
        n = len(self.PRISM_COLORS)
        w = self.PAGE_W / n
        for i, color in enumerate(self.PRISM_COLORS):
            canvas.setFillColor(color)
            canvas.rect(i * w, y, w + 0.5, height, stroke=0, fill=1)

    def _draw_cover_page(self, canvas, doc):
        """Cover page decorations: thick spectrum bands, no page number."""
        canvas.saveState()
        self._draw_spectrum(canvas, self.PAGE_H - 0.9 * cm, 0.9 * cm)
        self._draw_spectrum(canvas, 0, 0.35 * cm)
        canvas.restoreState()

    def _draw_body_page(self, canvas, doc):
        """Body page decorations: thin spectrum strip, header and footer."""
        canvas.saveState()
        self._draw_spectrum(canvas, self.PAGE_H - 6, 6)

        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(self.theme['primary'])
        canvas.drawString(self.MARGIN, self.PAGE_H - 26,
                          f"SEO Prism — {self._report_title}")
        if self._scan_url:
            canvas.setFont('Helvetica', 7.5)
            canvas.setFillColor(self.theme['text_light'])
            canvas.drawRightString(self.PAGE_W - self.MARGIN, self.PAGE_H - 26,
                                   self._shorten(self._scan_url, 72))
        canvas.setStrokeColor(self.theme['line'])
        canvas.setLineWidth(0.6)
        canvas.line(self.MARGIN, self.PAGE_H - 32,
                    self.PAGE_W - self.MARGIN, self.PAGE_H - 32)

        canvas.line(self.MARGIN, 1.1 * cm, self.PAGE_W - self.MARGIN, 1.1 * cm)
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(self.theme['text_light'])
        canvas.drawString(self.MARGIN, 0.75 * cm, 'SEO Prism')
        page_label = get_translation(self._lang, 'page')
        canvas.drawRightString(self.PAGE_W - self.MARGIN, 0.75 * cm,
                               f"{page_label} {canvas.getPageNumber()}")
        canvas.restoreState()

    @staticmethod
    def _shorten(text: str, max_len: int) -> str:
        """Middle-truncate long URLs for the page header, dropping any
        character the built-in Helvetica fonts cannot render."""
        text = SEOReportPDFGenerator._pdf_text(text)
        if len(text) <= max_len:
            return text
        half = max_len // 2 - 2
        return text[:half] + '...' + text[-half:]

    # ------------------------------------------------------------------ #
    # Data helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _pdf_text(value) -> str:
        """Sanitize and XML-escape text for Paragraph markup.

        The built-in Helvetica fonts use WinAnsi encoding and cannot render
        emoji or other exotic characters (they would appear as black
        squares), so any non-encodable character is dropped before escaping.
        """
        if value is None:
            return ''
        kept = []
        for ch in str(value):
            try:
                ch.encode('cp1252')
                kept.append(ch)
            except UnicodeEncodeError:
                continue
        return escape(''.join(kept))

    @staticmethod
    def _severity_counts(issues: list, breakdown: dict) -> dict:
        """Return {'high': n, 'medium': n, 'low': n}, preferring the grade
        breakdown and falling back to counting the issue list."""
        if breakdown:
            return {sev: breakdown.get(sev, 0) for sev in ('high', 'medium', 'low')}
        counts = {'high': 0, 'medium': 0, 'low': 0}
        for issue in issues:
            sev = issue.get('severity')
            if sev in counts:
                counts[sev] += 1
        return counts

    @classmethod
    def _grouped_categories(cls, issues: list) -> list:
        """Group issues by issue_type, ordered by severity weight (desc),
        then count (desc), then name — so the worst categories come first."""
        groups = {}
        for issue in issues:
            groups.setdefault(issue.get('issue_type', 'unknown'), []).append(issue)

        def weight(cat_issues):
            return sum(cls.SEVERITY_WEIGHT.get(i.get('severity'), 0) for i in cat_issues)

        return sorted(groups.items(), key=lambda kv: (-weight(kv[1]), -len(kv[1]), kv[0]))

    def _grade_color(self, grade: str):
        """Map a grade letter to its theme color."""
        mapping = {
            'A': self.theme['grade_a'],
            'B': self.theme['grade_b'],
            'C': self.theme['grade_c'],
            'D': self.theme['grade_d'],
            'F': self.theme['grade_f'],
        }
        return mapping.get(grade, self.theme['secondary'])

    def _severity_label(self, severity: str) -> str:
        """Translate a severity value ('high'/'medium'/'low')."""
        mapping = {
            'high': get_translation(self._lang, 'severity_high'),
            'medium': get_translation(self._lang, 'severity_medium'),
            'low': get_translation(self._lang, 'severity_low'),
        }
        return mapping.get(severity, severity)

    def _severity_color(self, severity: str):
        """Subtle color used only in severity cells."""
        return {
            'high': self.theme['high'],
            'medium': self.theme['medium'],
            'low': self.theme['low'],
        }.get(severity, self.theme['text_light'])

    # ------------------------------------------------------------------ #
    # Sections
    # ------------------------------------------------------------------ #

    def _cover_flowables(self, results: dict, lang: str) -> list:
        """Cover page: branding, URL, date, page count and grade box."""
        scan = results.get('scan', {})
        grade_data = results.get('seo_grade', {}) or {}
        grade = grade_data.get('grade', 'N/A')
        score = grade_data.get('score', 0)
        issues = results.get('issues', [])
        counts = self._severity_counts(issues, grade_data.get('breakdown', {}))

        flow = [
            Spacer(1, 2.6 * cm),
            Paragraph('SEO Prism', self.styles['brand']),
            Paragraph(get_translation(lang, 'tool_tagline'), self.styles['tagline']),
            Spacer(1, 1.1 * cm),
            Paragraph(get_translation(lang, 'report_title'), self.styles['cover_title']),
            Paragraph(get_translation(lang, 'executive_report'), self.styles['cover_sub']),
            Spacer(1, 1.4 * cm),
            Paragraph(
                f"<b>{self._pdf_text(get_translation(lang, 'analyzed_url'))}:</b> {self._pdf_text(scan.get('url', 'N/A') or 'N/A')}",
                self.styles['cover_info']),
            Paragraph(
                f"<b>{self._pdf_text(get_translation(lang, 'analysis_date'))}:</b> "
                f"{self._pdf_text(scan.get('timestamp') or datetime.now().strftime('%Y-%m-%d'))}",
                self.styles['cover_info']),
            Paragraph(
                f"<b>{self._pdf_text(get_translation(lang, 'total_pages'))}:</b> {scan.get('total_pages', 0)}",
                self.styles['cover_info']),
            Spacer(1, 1.6 * cm),
        ]

        # SEO Grade highlight box: colored letter + score + severity totals.
        high_hex = self.theme['high'].hexval()[2:]
        medium_hex = self.theme['medium'].hexval()[2:]
        low_hex = self.theme['low'].hexval()[2:]
        grade_info = Paragraph(
            f"<b>{self._pdf_text(get_translation(lang, 'seo_grade'))}</b><br/>"
            f"<b>{self._pdf_text(get_translation(lang, 'score'))}: {score}%</b><br/>"
            f"<font color='#{high_hex}'><b>{self._pdf_text(get_translation(lang, 'high_priority'))}: {counts['high']}</b></font><br/>"
            f"<font color='#{medium_hex}'><b>{self._pdf_text(get_translation(lang, 'medium_priority'))}: {counts['medium']}</b></font><br/>"
            f"<font color='#{low_hex}'><b>{self._pdf_text(get_translation(lang, 'low_priority'))}: {counts['low']}</b></font>",
            self.styles['grade_info'])
        grade_box = Table(
            [[Paragraph(str(grade), self.styles['grade_letter']), grade_info]],
            colWidths=[3.4 * cm, 7.0 * cm], hAlign='CENTER')
        grade_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self._grade_color(grade)),
            ('BACKGROUND', (1, 0), (1, 0), self.theme['card_bg']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.75, self.theme['line']),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (1, 0), (1, 0), 14),
            ('RIGHTPADDING', (1, 0), (1, 0), 14),
        ]))
        flow.append(grade_box)
        return flow

    def _executive_summary_flowables(self, results: dict, lang: str) -> list:
        """Executive summary: key metrics, top high-priority issues and the
        complete category distribution (no category limit)."""
        scan = results.get('scan', {})
        issues = results.get('issues', [])
        grade_data = results.get('seo_grade', {}) or {}
        counts = self._severity_counts(issues, grade_data.get('breakdown', {}))

        flow = [
            Paragraph(get_translation(lang, 'executive_summary'), self.styles['h1']),
            HRFlowable(width='100%', thickness=1, color=self.theme['accent'],
                       spaceBefore=0, spaceAfter=10),
            Paragraph(get_translation(lang, 'grade_explanation'), self.styles['note_italic']),
            Spacer(1, 0.2 * cm),
        ]

        # Key metric cards
        def card(value, label, color):
            value_style = ParagraphStyle(
                f'mv_{label}', parent=self.styles['metric_value'], textColor=color)
            return [Paragraph(str(value), value_style),
                    Paragraph(self._pdf_text(label), self.styles['metric_label'])]

        t = self.theme
        metrics = Table([
            card(scan.get('total_pages', 0), get_translation(lang, 'total_pages'), t['primary']) +
            card(scan.get('total_issues', len(issues)), get_translation(lang, 'total_issues'), t['primary']) +
            card(counts['high'], get_translation(lang, 'high_priority'), t['high']) +
            card(counts['medium'], get_translation(lang, 'medium_priority'), t['medium']) +
            card(counts['low'], get_translation(lang, 'low_priority'), t['low']),
        ], colWidths=[self.CONTENT_W / 5.0] * 5)
        metrics.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.theme['card_bg']),
            ('BOX', (0, 0), (-1, -1), 0.75, self.theme['line']),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, self.theme['line']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        flow.append(metrics)

        # Top high-priority issues as highlighted paragraphs
        high_issues = [i for i in issues if i.get('severity') == 'high'][:5]
        if high_issues:
            flow.append(Paragraph(get_translation(lang, 'top_priority_issues'),
                                  self.styles['h2']))
            rows = []
            for issue in high_issues:
                line = (f"<b>{self._pdf_text(issue.get('issue_type', 'unknown'))}</b> · "
                        f"{self._pdf_text(issue.get('url') or 'N/A')}")
                if issue.get('description'):
                    line += f"<br/>{self._pdf_text(issue['description'])}"
                rows.append([Paragraph(line, self.styles['critical'])])
            highlight = LongTable(rows, colWidths=[self.CONTENT_W])
            highlight.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.theme['high_bg']),
                ('LINEBEFORE', (0, 0), (0, -1), 2, self.theme['high']),
                ('LINEBELOW', (0, 0), (-1, -2), 1, colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            flow.append(highlight)

        # Complete distribution by category (every category, no limit)
        categories = self._grouped_categories(issues)
        if categories:
            flow.append(Paragraph(get_translation(lang, 'distribution'),
                                  self.styles['h2']))
            data = [[get_translation(lang, 'category'), get_translation(lang, 'count')]]
            for issue_type, cat_issues in categories:
                data.append([issue_type, str(len(cat_issues))])
            distribution = LongTable(data, colWidths=[self.CONTENT_W - 2.8 * cm, 2.8 * cm],
                                     repeatRows=1)
            distribution.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.theme['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.theme['row_alt']]),
                ('GRID', (0, 0), (-1, -1), 0.4, self.theme['line']),
                ('TOPPADDING', (0, 0), (-1, -1), 3.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            flow.append(distribution)

        return flow

    def _catalog_flowables(self, results: dict, lang: str) -> list:
        """Complete failure catalog: one section per category, each with a
        paginating LongTable listing EVERY issue of that category."""
        issues = results.get('issues', [])
        flow = [
            Paragraph(get_translation(lang, 'issue_catalog'), self.styles['h1']),
            HRFlowable(width='100%', thickness=1, color=self.theme['accent'],
                       spaceBefore=0, spaceAfter=10),
            Paragraph(get_translation(lang, 'catalog_note'), self.styles['note_italic']),
        ]

        categories = self._grouped_categories(issues)
        if not categories:
            flow.append(Paragraph(get_translation(lang, 'no_issues_found'),
                                  self.styles['body']))
            return flow

        issues_label = get_translation(lang, 'issues_label')
        for issue_type, cat_issues in categories:
            flow.append(Paragraph(
                f"{self._pdf_text(issue_type)} ({len(cat_issues)} {issues_label})",
                self.styles['h2']))

            impact = get_impact_template(lang, issue_type).get('impact', '')
            if impact:
                flow.append(Paragraph(self._pdf_text(impact), self.styles['body_small']))

            flow.append(self._issue_table(cat_issues, lang))

        return flow

    def _issue_table(self, issues: list, lang: str) -> LongTable:
        """LongTable with every issue of one category. Long URLs wrap
        (wordWrap='CJK'), and repeatRows=1 repeats the header on every
        page the table spills onto."""
        data = [[
            get_translation(lang, 'url'),
            get_translation(lang, 'source_page'),
            get_translation(lang, 'description'),
            get_translation(lang, 'severity'),
        ]]
        for issue in issues:
            severity = issue.get('severity', '')
            sev_hex = self._severity_color(severity).hexval()[2:]
            data.append([
                Paragraph(self._pdf_text(issue.get('url') or 'N/A'), self.styles['cell_url']),
                Paragraph(self._pdf_text(issue.get('source_page') or '—'), self.styles['cell_url']),
                Paragraph(self._pdf_text(issue.get('description') or '—'), self.styles['cell']),
                Paragraph(
                    f"<font color='#{sev_hex}'>{self._pdf_text(self._severity_label(severity))}</font>",
                    self.styles['cell_sev']),
            ])

        table = LongTable(data, colWidths=[5.0 * cm, 5.0 * cm, 6.0 * cm, 1.8 * cm],
                          repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.theme['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.theme['row_alt']]),
            ('GRID', (0, 0), (-1, -1), 0.4, self.theme['line']),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return table

    def _recommendations_flowables(self, results: dict, lang: str) -> list:
        """Recommendations / next steps per category, reusing the shared
        impact templates from report_translations."""
        issues = results.get('issues', [])
        flow = [
            Paragraph(get_translation(lang, 'recommendations'), self.styles['h1']),
            HRFlowable(width='100%', thickness=1, color=self.theme['accent'],
                       spaceBefore=0, spaceAfter=10),
        ]

        categories = self._grouped_categories(issues)
        if not categories:
            flow.append(Paragraph(get_translation(lang, 'no_issues_found'),
                                  self.styles['body']))
        else:
            issues_label = get_translation(lang, 'issues_label')
            for issue_type, cat_issues in categories:
                template = get_impact_template(lang, issue_type)
                flow.append(Paragraph(
                    f"{self._pdf_text(issue_type)} ({len(cat_issues)} {issues_label})",
                    self.styles['h2']))
                impact_label = self._pdf_text(get_translation(lang, 'impact_on_google'))
                flow.append(Paragraph(
                    f"<b>{impact_label}:</b> {self._pdf_text(template.get('impact', ''))}",
                    self.styles['body']))
                note = template.get('priority_note', '')
                if note:
                    note_html = '<br/>'.join(
                        self._pdf_text(part).strip()
                        for part in note.split('\n') if part.strip())
                    flow.append(Paragraph(note_html, self.styles['note_italic']))

        flow.append(Spacer(1, 0.4 * cm))
        flow.append(HRFlowable(width='100%', thickness=0.6,
                               color=self.theme['line'], spaceAfter=8))
        flow.append(Paragraph(get_translation(lang, 'call_to_action'),
                              self.styles['note_italic']))
        return flow

    def _notes_flowables(self, lang: str) -> list:
        """Editable notes section (placeholder for the consultant)."""
        return [
            Paragraph(get_translation(lang, 'notes'), self.styles['h1']),
            HRFlowable(width='100%', thickness=1, color=self.theme['accent'],
                       spaceBefore=0, spaceAfter=10),
            Paragraph(get_translation(lang, 'placeholder_notes'),
                      self.styles['note_italic']),
        ]

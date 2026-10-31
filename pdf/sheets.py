"""Sheets of equal items with a Code 128 barcode: copy labels and member cards.

Phase 4 small decisions 3, 4 and 5; ADR-0014, ADR-0035. Lengths are in
millimetres. Items fill a page row by row, left to right; a full page
continues on a new one.

Text uses the Vera TrueType font that ships with reportlab: the PDF base
fonts (WinAnsi) have no ş, ğ, ı or İ (plan §11, G08).
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from reportlab.graphics.barcode.code128 import Code128
from reportlab.lib.colors import Color, black
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

__all__ = [
    "CARD_LAYOUT",
    "LABEL_LAYOUT",
    "SheetItem",
    "SheetLayout",
    "fit_text",
    "item_position",
    "render_sheet",
]

FONT = "Vera"
pdfmetrics.registerFont(TTFont(FONT, "Vera.ttf"))  # found on reportlab's font path

BAR_HEIGHT_MM = 15
MODULE_MM = 0.33
HEADER_MAX_CHARS = 80  # ADR-0035
HEADER_SIZE = 8  # points
CAPTION_SIZE = 9
FOOTER_SIZE = 7
PADDING_MM = 2  # left and right text margin inside an item
LINE_GAP_MM = 1.2
ELLIPSIS = "…"
CUT_LINE_GREY = Color(0.7, 0.7, 0.7)
CUT_LINE_WIDTH = 0.25  # points


@dataclass(frozen=True, kw_only=True)
class SheetLayout:
    page_w: float = 210
    page_h: float = 297
    cols: int
    rows: int
    item_w: float
    item_h: float
    margin_top: float
    margin_left: float
    gap_x: float = 0
    gap_y: float = 0
    cut_lines: bool

    def __post_init__(self) -> None:
        if self.cols < 1 or self.rows < 1:
            raise ValueError("a layout needs at least one row and one column")
        width = self.margin_left + self.cols * self.item_w + (self.cols - 1) * self.gap_x
        height = self.margin_top + self.rows * self.item_h + (self.rows - 1) * self.gap_y
        if width > self.page_w + 1e-9 or height > self.page_h + 1e-9:
            raise ValueError("the items do not fit on the page")

    @property
    def per_page(self) -> int:
        return self.cols * self.rows


# 70 x 37 mm, 3 x 8 on A4, 0.5 mm top margin (phase 4 small decision 3).
LABEL_LAYOUT = SheetLayout(
    cols=3, rows=8, item_w=70, item_h=37, margin_top=0.5, margin_left=0, cut_lines=False
)
# ID-1 cards, 2 x 5 on A4, centred: (210 - 2 * 85.6) / 2 and (297 - 5 * 54) / 2
# (phase 4 small decision 4).
CARD_LAYOUT = SheetLayout(
    cols=2, rows=5, item_w=85.6, item_h=54, margin_top=13.5, margin_left=19.4, cut_lines=True
)


@dataclass(frozen=True)
class SheetItem:
    header: str
    barcode_value: str
    caption: str
    footer: str


def item_position(index: int, layout: SheetLayout) -> tuple[int, float, float]:
    """(page, left edge, top edge) of item ``index``, edges in mm from the
    page's top-left corner."""
    page, slot = divmod(index, layout.per_page)
    row, col = divmod(slot, layout.cols)
    x = layout.margin_left + col * (layout.item_w + layout.gap_x)
    y = layout.margin_top + row * (layout.item_h + layout.gap_y)
    return page, x, y


def fit_text(text: str, size: float, max_width: float, max_chars: int | None = None) -> str:
    """``text`` cut with "…" when longer than ``max_chars`` or wider than
    ``max_width`` points at ``size``; the font size is never reduced
    (ADR-0035). O(L²) for length L, L ≤ 80 in practice."""

    def width(value: str) -> float:
        return pdfmetrics.stringWidth(value, FONT, size)

    if (max_chars is None or len(text) <= max_chars) and width(text) <= max_width:
        return text
    cut = text[: len(text) if max_chars is None else max_chars - 1]
    while cut and width(cut + ELLIPSIS) > max_width:
        cut = cut[:-1]
    return cut.rstrip() + ELLIPSIS


def _draw_item(pdf: canvas.Canvas, item: SheetItem, layout: SheetLayout, x: float, top: float) -> None:
    """Draw one item; ``x`` and ``top`` are in points from the bottom-left."""
    item_w, item_h = layout.item_w * mm, layout.item_h * mm
    text_width = item_w - 2 * PADDING_MM * mm
    gap = LINE_GAP_MM * mm
    barcode = Code128(
        item.barcode_value, barWidth=MODULE_MM * mm, barHeight=BAR_HEIGHT_MM * mm, humanReadable=False
    )
    lines = [(item.header, HEADER_SIZE, HEADER_MAX_CHARS), None, (item.caption, CAPTION_SIZE, None)]
    if item.footer:
        lines.append((item.footer, FOOTER_SIZE, None))
    block = sum(gap + (line[1] if line else barcode.height) for line in lines) - gap
    cursor = top - (item_h - block) / 2  # the block is centred vertically
    centre = x + item_w / 2
    for line in lines:
        if line is None:
            barcode.drawOn(pdf, centre - barcode.width / 2, cursor - barcode.height)
            cursor -= barcode.height + gap
            continue
        text, size, max_chars = line
        pdf.setFont(FONT, size)
        cursor -= size
        pdf.drawCentredString(centre, cursor + 0.2 * size, fit_text(text, size, text_width, max_chars))
        cursor -= gap
    if layout.cut_lines:
        pdf.setStrokeColor(CUT_LINE_GREY)
        pdf.setLineWidth(CUT_LINE_WIDTH)
        pdf.rect(x, top - item_h, item_w, item_h, stroke=1, fill=0)
        pdf.setStrokeColor(black)


def render_sheet(items: list[SheetItem], layout: SheetLayout) -> bytes:
    """A PDF of ``items`` placed by ``layout``; O(n) for n items."""
    if not items:
        raise ValueError("render_sheet needs at least one item")
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(layout.page_w * mm, layout.page_h * mm), invariant=True)
    page_h = layout.page_h * mm
    current_page = 0
    for index, item in enumerate(items):
        page, x, y = item_position(index, layout)
        if page != current_page:
            pdf.showPage()
            current_page = page
        _draw_item(pdf, item, layout, x * mm, page_h - y * mm)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()

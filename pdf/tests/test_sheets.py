"""Unit tests for the PDF sheet helper (G08).

TC-69, TC-70; plus the layout presets, item placement and text fitting.
Decoding tests are marked ``slow`` (ADR-0030).
"""

from __future__ import annotations

import dataclasses

import pytest

from pdf.sheets import (
    CARD_LAYOUT,
    LABEL_LAYOUT,
    SheetItem,
    SheetLayout,
    fit_text,
    item_position,
    render_sheet,
)
from tests.support.barcode import pdf_page_count, pdf_text, read_pdf_barcodes


def _items(count: int, prefix: str = "") -> list[SheetItem]:
    return [
        SheetItem(header="Kütüphane", barcode_value=f"{i:08d}", caption=f"{i:08d}", footer=f"{prefix}{i}")
        for i in range(1, count + 1)
    ]


# --- Layout presets (phase 4 small decisions 3 and 4) -------------------------


def test_label_layout_preset() -> None:
    assert dataclasses.astuple(LABEL_LAYOUT) == (210, 297, 3, 8, 70, 37, 0.5, 0, 0, 0, False)


def test_card_layout_preset_centres_cards_on_a4() -> None:
    assert (CARD_LAYOUT.cols, CARD_LAYOUT.rows) == (2, 5)
    assert (CARD_LAYOUT.item_w, CARD_LAYOUT.item_h) == (85.6, 54)
    assert CARD_LAYOUT.cut_lines
    assert CARD_LAYOUT.margin_left == pytest.approx((210 - 2 * 85.6) / 2)
    assert CARD_LAYOUT.margin_top == pytest.approx((297 - 5 * 54) / 2)


def test_layouts_are_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        LABEL_LAYOUT.cols = 4  # type: ignore[misc]


def test_layout_that_does_not_fit_the_page_is_refused() -> None:
    with pytest.raises(ValueError):
        SheetLayout(cols=4, rows=8, item_w=70, item_h=37, margin_top=0, margin_left=0, cut_lines=False)
    with pytest.raises(ValueError):
        SheetLayout(cols=1, rows=0, item_w=70, item_h=37, margin_top=0, margin_left=0, cut_lines=False)


def test_items_fill_rows_left_to_right_then_pages() -> None:
    assert item_position(0, LABEL_LAYOUT) == (0, 0, 0.5)
    assert item_position(1, LABEL_LAYOUT) == (0, 70, 0.5)
    assert item_position(3, LABEL_LAYOUT) == (0, 0, 37.5)
    assert item_position(23, LABEL_LAYOUT) == (0, 140, 0.5 + 7 * 37)
    assert item_position(24, LABEL_LAYOUT) == (1, 0, 0.5)
    page, x, y = item_position(3, CARD_LAYOUT)
    assert (page, x, y) == (0, pytest.approx(19.4 + 85.6), pytest.approx(13.5 + 54))


def test_gaps_shift_items() -> None:
    layout = dataclasses.replace(LABEL_LAYOUT, cols=2, rows=4, gap_x=5, gap_y=2)
    assert item_position(1, layout) == (0, 75, 0.5)
    assert item_position(2, layout) == (0, 0, 39.5)


# --- Text fitting (ADR-0035) --------------------------------------------------


def test_short_text_is_kept() -> None:
    assert fit_text("Kütüphane", 8, 180, max_chars=80) == "Kütüphane"


def test_more_than_80_characters_are_cut_with_an_ellipsis() -> None:
    fitted = fit_text("i" * 81, 8, 10_000, max_chars=80)
    assert fitted == "i" * 79 + "…"
    assert fit_text("i" * 80, 8, 10_000, max_chars=80) == "i" * 80


def test_text_wider_than_the_item_is_cut_with_an_ellipsis() -> None:
    fitted = fit_text("W" * 80, 8, 180, max_chars=80)
    assert fitted.endswith("…")
    assert 1 < len(fitted) < 80
    assert fit_text("", 8, 180) == ""


# --- render_sheet ---------------------------------------------------------------


@pytest.mark.parametrize(("count", "pages"), [(24, 1), (25, 2)])
def test_tc69_label_layout_page_count(count: int, pages: int) -> None:
    assert pdf_page_count(render_sheet(_items(count), LABEL_LAYOUT)) == pages


def test_render_sheet_needs_items() -> None:
    with pytest.raises(ValueError):
        render_sheet([], LABEL_LAYOUT)


def test_render_sheet_writes_turkish_text() -> None:
    item = SheetItem(header="İstanbul Şehir Kütüphanesi", barcode_value="42", caption="Üye No: 42", footer="Iğdır")
    text = pdf_text(render_sheet([item], CARD_LAYOUT))
    for expected in ("İstanbul Şehir Kütüphanesi", "Üye No: 42", "Iğdır"):
        assert expected in text


def test_long_header_is_shortened_in_the_pdf() -> None:
    item = SheetItem(header="W" * 80, barcode_value="00000001", caption="00000001", footer="")
    text = pdf_text(render_sheet([item], LABEL_LAYOUT))
    assert "…" in text
    assert "W" * 80 not in text


def test_render_sheet_is_deterministic() -> None:
    assert render_sheet(_items(3), CARD_LAYOUT) == render_sheet(_items(3), CARD_LAYOUT)


@pytest.mark.slow
def test_tc70_decoded_values_follow_page_rows_and_columns() -> None:
    layout = SheetLayout(cols=2, rows=1, item_w=85.6, item_h=54, margin_top=20, margin_left=19.4, cut_lines=True)
    items = [
        SheetItem(header="K", barcode_value=value, caption=value, footer="")
        for value in ("00000003", "00000001", "00000002")
    ]
    decoded = read_pdf_barcodes(render_sheet(items, layout))
    assert [(b.page, b.value) for b in decoded] == [(0, "00000003"), (0, "00000001"), (1, "00000002")]
    assert {b.format for b in decoded} == {"Code128"}


@pytest.mark.slow
def test_tc70_rows_top_to_bottom_on_one_page() -> None:
    layout = SheetLayout(cols=2, rows=2, item_w=85.6, item_h=54, margin_top=20, margin_left=19.4, cut_lines=False)
    values = ["00000020", "00000010", "00000040"]
    items = [SheetItem(header="K", barcode_value=v, caption=v, footer="") for v in values]
    decoded = read_pdf_barcodes(render_sheet(items, layout))
    assert [(b.page, b.value) for b in decoded] == [(0, v) for v in values]

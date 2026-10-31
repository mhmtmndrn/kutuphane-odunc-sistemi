"""PDF test helpers: barcode decoding (ADR-0030) and text extraction.

``decode_pdf_barcodes`` renders every page with pypdfium2 and decodes the
barcodes with zxing-cpp. Values come in page order, then top to bottom and
left to right within a page. Development dependencies only.
"""

from __future__ import annotations

from dataclasses import dataclass

import pypdfium2 as pdfium
import zxingcpp

# Barcodes whose centres differ by less than this many millimetres
# vertically are one row (the bars are 15 mm high).
_ROW_TOLERANCE_MM = 7.5


@dataclass(frozen=True)
class DecodedBarcode:
    page: int
    value: str
    format: str


def read_pdf_barcodes(pdf: bytes, dpi: int = 300) -> list[DecodedBarcode]:
    tolerance = _ROW_TOLERANCE_MM / 25.4 * dpi
    found: list[DecodedBarcode] = []
    document = pdfium.PdfDocument(pdf)
    try:
        for page_no, page in enumerate(document):
            image = page.render(scale=dpi / 72).to_pil()
            located = []
            for result in zxingcpp.read_barcodes(image):
                pos = result.position
                xs = [pos.top_left.x, pos.top_right.x, pos.bottom_left.x, pos.bottom_right.x]
                ys = [pos.top_left.y, pos.top_right.y, pos.bottom_left.y, pos.bottom_right.y]
                located.append((sum(ys) / 4, sum(xs) / 4, result))
            located.sort(key=lambda item: item[0])
            rows: list[list[tuple[float, float, object]]] = []
            for item in located:
                if rows and item[0] - rows[-1][0][0] < tolerance:
                    rows[-1].append(item)
                else:
                    rows.append([item])
            for row in rows:
                for _, _, result in sorted(row, key=lambda item: item[1]):
                    found.append(DecodedBarcode(page_no, result.text, result.format.name))
    finally:
        document.close()
    return found


def decode_pdf_barcodes(pdf: bytes, dpi: int = 300) -> list[str]:
    return [barcode.value for barcode in read_pdf_barcodes(pdf, dpi)]


def pdf_page_count(pdf: bytes) -> int:
    document = pdfium.PdfDocument(pdf)
    try:
        return len(document)
    finally:
        document.close()


def pdf_text(pdf: bytes) -> str:
    """The text of every page, pages joined by a newline."""
    document = pdfium.PdfDocument(pdf)
    try:
        return "\n".join(page.get_textpage().get_text_range() for page in document)
    finally:
        document.close()

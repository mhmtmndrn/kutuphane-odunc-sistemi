"""One-time fetch of the demo books from Open Library (ADR-0033, ADR-0056).

Usage::

    python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300

Standard library only. The search API is called page by page with at least
one second between requests and a ``User-Agent`` naming the project. The
records that pass ``filter_records`` (ADR-0033, five rules in order) are
written with a ``_meta`` block; ``load_seed_data`` reads this file and never
goes to the network.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable
from datetime import date
from pathlib import Path

if __package__ in (None, ""):  # run as a file: make ``catalog`` importable
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalog.domain import IsbnOk, parse_isbn  # noqa: E402 - pure, no Django

SEARCH_URL = "https://openlibrary.org/search.json"
QUERY = "language:tur isbn:978605*"
FIELDS = "key,title,author_name,first_publish_year,isbn"
PAGE_SIZE = 100
MIN_INTERVAL_SECONDS = 1.0
TIMEOUT_SECONDS = 30
USER_AGENT = (
    "kutuphane-odunc-sistemi/1.0 "
    "(one-time demo data fetch; https://github.com/mhmtmndrn/kutuphane-odunc-sistemi)"
)
FILTER_VERSION = 1
SOURCE = "Open Library (https://openlibrary.org), arama API'si"
LICENSE = (
    "Open Library kataloğu verisi CC0 (kamu malı) olarak sunulur; yalnız bibliyografik "
    "alanlar (başlık, yazar, yıl, ISBN) ve OL kimliği alındı, kapak alınmadı."
)
GARBLED = ("¿", "Ã", "Å", "�")
TURKISH_LETTERS = frozenset("çğıİöşüÇĞÖŞÜ")

# Indirection so that tests replace the opener without touching urllib.
_urlopen = urllib.request.urlopen


def _isbn13(candidates: Iterable[str]) -> str | None:
    """The first candidate that is a valid ISBN-13 (rule 4)."""
    for raw in candidates:
        value = "".join(ch for ch in str(raw) if ch != "-" and not ch.isspace())
        if len(value) != 13:
            continue
        parsed = parse_isbn(value)
        if isinstance(parsed, IsbnOk):
            return parsed.isbn13
    return None


def filter_records(raw: Iterable[dict]) -> list[dict]:
    """Apply the five rules of ADR-0033 in order to Open Library search docs.

    1. blank title or author; 2. "¿", "Ã", "Å" or "�" in either;
    3. no Turkish letter in title and author; 4. no valid ISBN-13;
    5. a repeated ISBN (the first record is kept). O(n).
    """
    records: list[dict] = []
    seen: set[str] = set()
    for doc in raw:
        title = (doc.get("title") or "").strip()
        author = ", ".join(
            name.strip() for name in doc.get("author_name") or [] if name and name.strip()
        )
        if not title or not author:
            continue
        text = title + author
        if any(mark in text for mark in GARBLED):
            continue
        if not TURKISH_LETTERS.intersection(text):
            continue
        isbn = _isbn13(doc.get("isbn") or [])
        if isbn is None or isbn in seen:
            continue
        seen.add(isbn)
        year = doc.get("first_publish_year")
        records.append(
            {
                "ol_id": str(doc.get("key", "")).rsplit("/", 1)[-1],
                "title": title,
                "author": author,
                "year": year if isinstance(year, int) else None,
                "isbn13": isbn,
            }
        )
    return records


def _request(page: int) -> urllib.request.Request:
    query = urllib.parse.urlencode(
        {"q": QUERY, "fields": FIELDS, "limit": PAGE_SIZE, "page": page}
    )
    return urllib.request.Request(
        f"{SEARCH_URL}?{query}", headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )


def fetch_books(
    limit: int,
    *,
    urlopen: Callable = None,
    sleep: Callable[[float], None] = time.sleep,
) -> list[dict]:
    """Fetch pages until ``limit`` records pass the filter or a page is empty."""
    urlopen = urlopen or _urlopen
    raw: list[dict] = []
    records: list[dict] = []
    page = 0
    while len(records) < limit:
        page += 1
        if page > 1:
            sleep(MIN_INTERVAL_SECONDS)
        with urlopen(_request(page), timeout=TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
        docs = body.get("docs") or []
        if not docs:
            break
        raw.extend(docs)
        records = filter_records(raw)
    return records[:limit]


def write_output(path: Path, records: list[dict], fetched_on: date) -> None:
    data = {
        "_meta": {
            "source": SOURCE,
            "query": QUERY,
            "fetched_on": fetched_on.isoformat(),
            "license": LICENSE,
            "filter_version": FILTER_VERSION,
            "count": len(records),
        },
        "books": records,
    }
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"pozitif bir tam sayı olmalı: {value}") from None
    if number <= 0:
        raise argparse.ArgumentTypeError(f"pozitif bir tam sayı olmalı: {value}")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Demo kitaplarını Open Library'den bir kez çeker ve JSON dosyasına yazar."
    )
    parser.add_argument("--out", required=True, type=Path, help="Yazılacak JSON dosyası")
    parser.add_argument(
        "--limit", type=_positive_int, default=300, help="En çok kayıt sayısı; varsayılan 300"
    )
    args = parser.parse_args(argv)
    try:
        records = fetch_books(args.limit, urlopen=_urlopen, sleep=time.sleep)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        print(f"Open Library'ye erişilemedi: {reason}", file=sys.stderr)
        return 1
    write_output(args.out, records, date.today())
    print(f"{len(records)} kayıt yazıldı: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

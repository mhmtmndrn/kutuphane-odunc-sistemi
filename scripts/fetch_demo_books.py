"""One-time fetch of the demo books from Open Library (ADR-0033, ADR-0056, ADR-0059).

Usage::

    python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300

Standard library only. The search API is called page by page with at least
one second between requests and a ``User-Agent`` naming the project. The
Turkish editions that pass ``filter_records`` (ADR-0033's five rules, applied
to the edition per ADR-0059) are written with a ``_meta`` block; ``load_seed_data`` reads this file and never
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
FIELDS = (
    "key,author_name,first_publish_year,"
    "editions,editions.key,editions.title,editions.isbn,editions.language"
)
PAGE_SIZE = 100
MIN_INTERVAL_SECONDS = 1.0
TIMEOUT_SECONDS = 30
RETRY_WAITS_SECONDS = (2.0, 4.0, 8.0)  # per page, after a 5xx or a timeout
USER_AGENT = (
    "kutuphane-odunc-sistemi/1.0 "
    "(one-time demo data fetch; https://github.com/mhmtmndrn/kutuphane-odunc-sistemi)"
)
FILTER_VERSION = 2
SOURCE = "Open Library (https://openlibrary.org), arama API'si"
LICENSE = (
    "Open Library kataloğu verisi CC0 (kamu malı) olarak sunulur; yalnız bibliyografik "
    "alanlar (başlık, yazar, yıl, ISBN) ve OL kimliği alındı, kapak alınmadı."
)
GARBLED = ("¿", "Ã", "Å", "�")
TURKISH_LETTERS = frozenset("çğıİöşüÇĞÖŞÜ")
TURKISH_LANGUAGE = "tur"

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


def _turkish_edition(doc: dict) -> dict | None:
    """The first edition of a search doc whose language is Turkish (ADR-0059).

    The search returns works; the work title is usually the original one, while
    ``editions.docs`` holds the editions that matched the query.
    """
    for entry in (doc.get("editions") or {}).get("docs") or []:
        if TURKISH_LANGUAGE in (entry.get("language") or []):
            return entry
    return None


def filter_records(raw: Iterable[dict]) -> list[dict]:
    """Apply the five rules of ADR-0033 in order to the Turkish edition of each doc.

    A doc without a Turkish edition is dropped (ADR-0059); title, ISBN and
    ``ol_id`` come from the edition, author and year from the work.
    1. blank title or author; 2. "¿", "Ã", "Å" or "�" in either;
    3. no Turkish letter in title and author; 4. no valid ISBN-13;
    5. a repeated ISBN (the first record is kept). O(n + e) for e editions.
    """
    records: list[dict] = []
    seen: set[str] = set()
    for doc in raw:
        found = _turkish_edition(doc)
        if found is None:
            continue
        title = (found.get("title") or "").strip()
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
        isbn = _isbn13(found.get("isbn") or [])
        if isbn is None or isbn in seen:
            continue
        seen.add(isbn)
        year = doc.get("first_publish_year")
        records.append(
            {
                "ol_id": str(found.get("key", "")).rsplit("/", 1)[-1],
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


def _retryable(exc: Exception) -> bool:
    """A 5xx answer or a timeout; a 4xx or another network error is final."""
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code >= 500
    if isinstance(exc, urllib.error.URLError):
        return isinstance(exc.reason, TimeoutError)
    return isinstance(exc, TimeoutError)


def _get_page(page: int, urlopen: Callable, sleep: Callable[[float], None]) -> dict:
    """One search page; retried with growing waits while the error is retryable."""
    for wait in (*RETRY_WAITS_SECONDS, None):
        try:
            with urlopen(_request(page), timeout=TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            if wait is None or not _retryable(exc):
                raise
            sleep(wait)
    raise AssertionError("unreachable")  # pragma: no cover


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
        body = _get_page(page, urlopen, sleep)
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

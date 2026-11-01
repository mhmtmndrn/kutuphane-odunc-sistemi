"""Tests of the one-time Open Library fetch (plan G17, ADR-0033, ADR-0056).

No network: the HTTP opener and the wait are replaced (test plan §5).
"""

from __future__ import annotations

import io
import json
import urllib.parse
from datetime import date

import pytest

from scripts import fetch_demo_books as fetch


def isbn13(n: int) -> str:
    first12 = f"978605{n:06d}"
    total = sum(int(ch) * (3 if i % 2 else 1) for i, ch in enumerate(first12))
    return first12 + str((10 - total % 10) % 10)


def edition(n: int, title: str = "Çalıkuşu", isbn: list[str] | None = None,
            language: list[str] | None = None) -> dict:
    """An edition entry of a search document's ``editions.docs`` (ADR-0059)."""
    return {
        "key": f"/books/OL{n}M",
        "title": title,
        "isbn": [isbn13(n)] if isbn is None else isbn,
        "language": ["tur"] if language is None else language,
    }


def doc(n: int, title: str = "Çalıkuşu", author: str = "Reşat Nuri Güntekin",
        isbn: list[str] | None = None, work_title: str = "The Wren",
        editions: list[dict] | None = None, **extra) -> dict:
    """An Open Library search document (a work) with its matching Turkish edition.

    ``title`` and ``isbn`` belong to the edition; the work title is the original one.
    """
    base = {
        "key": f"/works/OL{n}W",
        "title": work_title,
        "author_name": [author],
        "first_publish_year": 1922,
        "editions": {
            "numFound": 1,
            "docs": [edition(n, title, isbn)] if editions is None else editions,
        },
    }
    base.update(extra)
    return base


def test_tc214_blank_and_garbled_records_dropped():
    raw = [
        doc(1, title=""),
        doc(2, author=""),
        doc(3, author_name=[]),
        doc(4, title="Kitap ¿ adı"),
        doc(5, author="YazarÃ Çelik"),
        doc(6, title="Åşk"),
        doc(7, author="Ali � Öz"),
        doc(8),
    ]
    records = fetch.filter_records(raw)
    assert [r["ol_id"] for r in records] == ["OL8M"]


def test_tc215_no_turkish_letter_and_invalid_isbn_dropped():
    bad_check = isbn13(3)[:-1] + str((int(isbn13(3)[-1]) + 1) % 10)
    raw = [
        doc(1, title="Madonna", author="Sabahattin Ali"),  # no Turkish letter
        doc(2, title="Kürk Mantolu Madonna", author="Sabahattin Ali"),  # "ü"
        doc(3, isbn=[bad_check]),
        doc(4, isbn=["6053609322"]),  # ISBN-10 form: not an ISBN-13
        doc(5, isbn=[]),
        doc(6, isbn=["123", isbn13(6)]),  # the first valid ISBN-13 is taken
    ]
    records = fetch.filter_records(raw)
    assert [r["ol_id"] for r in records] == ["OL2M", "OL6M"]
    assert records[1]["isbn13"] == isbn13(6)


def test_tc216_duplicate_isbn_and_first_300_with_meta(tmp_path):
    raw = [doc(1), doc(2, isbn=[isbn13(1)], title="İkinci kayıt")]
    records = fetch.filter_records(raw)
    assert [r["ol_id"] for r in records] == ["OL1M"]
    assert records[0] == {
        "ol_id": "OL1M",
        "title": "Çalıkuşu",
        "author": "Reşat Nuri Güntekin",
        "year": 1922,
        "isbn13": isbn13(1),
    }

    pages = [[doc(n) for n in range(1, 101)], [doc(n) for n in range(101, 201)],
             [doc(n) for n in range(201, 302)]]
    opener = FakeOpener(pages)
    books = fetch.fetch_books(300, urlopen=opener, sleep=lambda s: None)
    assert len(books) == 300
    out = tmp_path / "books.json"
    fetch.write_output(out, books, date(2026, 11, 1))
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data["books"]) == 300
    assert data["books"][0]["ol_id"] == "OL1M"
    meta = data["_meta"]
    assert meta["source"].startswith("Open Library")
    assert meta["query"] == "language:tur isbn:978605*"
    assert meta["fetched_on"] == "2026-11-01"
    assert "CC0" in meta["license"]
    assert meta["filter_version"] == fetch.FILTER_VERSION
    assert meta["count"] == 300


class FakeOpener:
    """Stands in for ``urllib.request.urlopen``; serves one page per call."""

    def __init__(self, pages: list[list[dict]]) -> None:
        self.pages = pages
        self.requests = []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        index = len(self.requests) - 1
        docs = self.pages[index] if index < len(self.pages) else []
        total = sum(len(page) for page in self.pages)
        return io.BytesIO(json.dumps({"numFound": total, "docs": docs}).encode("utf-8"))


def test_tc340_paging_wait_user_agent_and_limit(tmp_path):
    pages = [[doc(1), doc(2)], [doc(3)], []]
    waits: list[float] = []
    opener = FakeOpener(pages)
    books = fetch.fetch_books(300, urlopen=opener, sleep=waits.append)
    assert [b["ol_id"] for b in books] == ["OL1M", "OL2M", "OL3M"]
    assert len(opener.requests) == 3  # stops at the empty page
    assert len(waits) == 2 and all(w >= 1.0 for w in waits)  # between requests only
    for number, request in enumerate(opener.requests, start=1):
        assert request.get_header("User-agent").startswith("kutuphane-odunc-sistemi")
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.full_url).query)
        assert query["q"] == ["language:tur isbn:978605*"]
        assert query["page"] == [str(number)]

    limited = FakeOpener(pages)
    books = fetch.fetch_books(2, urlopen=limited, sleep=lambda s: None)
    assert [b["ol_id"] for b in books] == ["OL1M", "OL2M"]
    assert len(limited.requests) == 1  # the second page is not requested


def test_tc340_main_writes_file_and_reports_network_error(tmp_path, monkeypatch, capsys):
    out = tmp_path / "çıktı klasörü" / "books.json"
    out.parent.mkdir()
    monkeypatch.setattr(fetch, "_urlopen", FakeOpener([[doc(1)], []]))
    monkeypatch.setattr(fetch.time, "sleep", lambda s: None)
    assert fetch.main(["--out", str(out), "--limit", "300"]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["_meta"]["count"] == 1
    assert "1 kayıt yazıldı" in capsys.readouterr().out

    def refused(request, timeout=None):
        raise fetch.urllib.error.URLError("Tunnel connection failed: 403 Forbidden")

    monkeypatch.setattr(fetch, "_urlopen", refused)
    other = tmp_path / "other.json"
    assert fetch.main(["--out", str(other)]) == 1
    assert "Open Library'ye erişilemedi" in capsys.readouterr().err
    assert not other.exists()


@pytest.mark.parametrize("value", ["0", "-1", "x"])
def test_tc340_limit_must_be_positive(value):
    with pytest.raises(SystemExit) as exc:
        fetch.main(["--out", "x.json", "--limit", value])
    assert exc.value.code == 2


def test_tc357_turkish_edition_supplies_title_isbn_and_id():
    """ADR-0059: the record is the matching Turkish edition, not the work."""
    other = isbn13(900)
    raw = [
        # the work title is the original; the Turkish edition's title and ISBN are taken
        doc(1, title="Atomik Alışkanlıklar", work_title="Atomic Habits", author="James Clear"),
        doc(2, editions=[]),  # no matching edition
        {**doc(3), "editions": {}},  # field without docs
        # a non-Turkish edition is skipped; the next Turkish one is taken
        doc(4, author="Antoine de Saint-Exupéry", editions=[
            edition(40, title="Le Petit Prince", isbn=[other], language=["fre"]),
            edition(41, title="Küçük Prens"),
        ]),
        doc(5, editions=[edition(5, language=[])]),  # edition without language
        # rules apply to the edition: Turkish letters only in the work title do not count
        doc(6, title="Dune", work_title="Düne", author="Frank Herbert"),
    ]
    records = fetch.filter_records(raw)
    assert records == [
        {"ol_id": "OL1M", "title": "Atomik Alışkanlıklar", "author": "James Clear",
         "year": 1922, "isbn13": isbn13(1)},
        {"ol_id": "OL41M", "title": "Küçük Prens", "author": "Antoine de Saint-Exupéry",
         "year": 1922, "isbn13": isbn13(41)},
    ]


def test_tc357_request_asks_for_edition_fields_and_meta_records_version_2():
    opener = FakeOpener([[doc(1)], []])
    fetch.fetch_books(300, urlopen=opener, sleep=lambda s: None)
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(opener.requests[0].full_url).query)
    fields = set(query["fields"][0].split(","))
    assert {"editions", "editions.key", "editions.title", "editions.isbn",
            "editions.language"} <= fields
    assert fetch.FILTER_VERSION == 2


def http_error(code: int) -> Exception:
    return fetch.urllib.error.HTTPError(fetch.SEARCH_URL, code, "error", {}, None)


class FlakyOpener:
    """Serves a scripted outcome per call: an exception to raise or a page of docs."""

    def __init__(self, outcomes: list) -> None:
        self.outcomes = outcomes
        self.pages: list[int] = []

    def __call__(self, request, timeout=None):
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.full_url).query)
        self.pages.append(int(query["page"][0]))
        outcome = self.outcomes[len(self.pages) - 1] if len(self.pages) <= len(self.outcomes) else []
        if isinstance(outcome, BaseException):
            raise outcome
        return io.BytesIO(json.dumps({"docs": outcome}).encode("utf-8"))


def test_tc358_server_error_and_timeout_retried_with_backoff():
    opener = FlakyOpener([http_error(500), TimeoutError("timed out"),
                          fetch.urllib.error.URLError(TimeoutError("connect")), [doc(1)],
                          http_error(503), [doc(2)], []])
    waits: list[float] = []
    books = fetch.fetch_books(300, urlopen=opener, sleep=waits.append)
    assert [b["ol_id"] for b in books] == ["OL1M", "OL2M"]
    assert opener.pages == [1, 1, 1, 1, 2, 2, 3]  # the same page is asked again
    # retry waits grow 2, 4, 8 (reset per page); 1 s between pages
    assert waits == [2.0, 4.0, 8.0, 1.0, 2.0, 1.0]


def test_tc358_retries_exhausted_or_client_error_raise(monkeypatch, tmp_path, capsys):
    waits: list[float] = []
    opener = FlakyOpener([http_error(500)] * 4)
    with pytest.raises(fetch.urllib.error.HTTPError):
        fetch.fetch_books(300, urlopen=opener, sleep=waits.append)
    assert opener.pages == [1, 1, 1, 1] and waits == [2.0, 4.0, 8.0]

    waits.clear()
    opener = FlakyOpener([http_error(404)])
    with pytest.raises(fetch.urllib.error.HTTPError):
        fetch.fetch_books(300, urlopen=opener, sleep=waits.append)
    assert opener.pages == [1] and waits == []  # 4xx is not retried

    monkeypatch.setattr(fetch, "_urlopen", FlakyOpener([http_error(502)] * 4))
    monkeypatch.setattr(fetch.time, "sleep", lambda s: None)
    out = tmp_path / "books.json"
    assert fetch.main(["--out", str(out)]) == 1
    assert "Open Library'ye erişilemedi" in capsys.readouterr().err
    assert not out.exists()

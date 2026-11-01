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


def doc(n: int, title: str = "Çalıkuşu", author: str = "Reşat Nuri Güntekin", **extra) -> dict:
    """An Open Library search document."""
    base = {
        "key": f"/works/OL{n}W",
        "title": title,
        "author_name": [author],
        "first_publish_year": 1922,
        "isbn": [isbn13(n)],
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
    assert [r["ol_id"] for r in records] == ["OL8W"]


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
    assert [r["ol_id"] for r in records] == ["OL2W", "OL6W"]
    assert records[1]["isbn13"] == isbn13(6)


def test_tc216_duplicate_isbn_and_first_300_with_meta(tmp_path):
    raw = [doc(1), doc(2, isbn=[isbn13(1)], title="İkinci kayıt")]
    records = fetch.filter_records(raw)
    assert [r["ol_id"] for r in records] == ["OL1W"]
    assert records[0] == {
        "ol_id": "OL1W",
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
    assert data["books"][0]["ol_id"] == "OL1W"
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
    assert [b["ol_id"] for b in books] == ["OL1W", "OL2W", "OL3W"]
    assert len(opener.requests) == 3  # stops at the empty page
    assert len(waits) == 2 and all(w >= 1.0 for w in waits)  # between requests only
    for number, request in enumerate(opener.requests, start=1):
        assert request.get_header("User-agent").startswith("kutuphane-odunc-sistemi")
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.full_url).query)
        assert query["q"] == ["language:tur isbn:978605*"]
        assert query["page"] == [str(number)]

    limited = FakeOpener(pages)
    books = fetch.fetch_books(2, urlopen=limited, sleep=lambda s: None)
    assert [b["ol_id"] for b in books] == ["OL1W", "OL2W"]
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

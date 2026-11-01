"""Tests of the load test script (plan G18, ADR-0031, ADR-0058, KL-17).

The script itself never imports Django (G17–G18 small decision 11). Some
tests build their ``--db`` file with the Django factories so that the
script's SQL is checked against the real schema.
"""

from __future__ import annotations

import http.server
import random
import sqlite3
import subprocess
import sys
import threading
import tomllib
import urllib.parse
from collections import Counter
from pathlib import Path

import pytest

from scripts import loadtest
from tests.support.concurrency import file_db  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# --- TC-221, TC-222: report logic -------------------------------------------------


def stats_with(**durations: list[float]) -> dict[str, loadtest.OpStats]:
    stats = {op: loadtest.OpStats(durations_ms=[10.0]) for op in loadtest.OPERATIONS}
    for op, values in durations.items():
        stats[op] = loadtest.OpStats(durations_ms=values)
    return stats


def test_tc221_p95_and_error_thresholds():
    assert loadtest.passes(stats_with(**{"ödünç": [499.0] * 20}))
    assert not loadtest.passes(stats_with(**{"ödünç": [500.0] * 20}))
    with_error = stats_with()
    with_error["iade"].errors = 1
    assert not loadtest.passes(with_error)
    # A type without requests proves nothing: the run fails (plan §11).
    missing = stats_with()
    missing["uzatma"] = loadtest.OpStats()
    assert not loadtest.passes(missing)


def test_tc221_report_columns():
    stats = stats_with(**{"kitap arama": [100.0] * 96 + [900.0] * 4})
    stats["iade"] = loadtest.OpStats()
    lines = loadtest.report_lines(stats)
    assert lines[0].split() == ["işlem", "istek", "p50", "(ms)", "p95", "(ms)", "hata"]
    book = next(line for line in lines if line.startswith("kitap arama"))
    assert book.split()[2:] == ["100", "100.0", "100.0", "0"]
    returns = next(line for line in lines if line.startswith("iade"))
    assert returns.split()[1:] == ["0", "-", "-", "0"]
    assert lines[-1] == "Sonuç: kaldı"
    assert loadtest.report_lines(stats_with())[-1] == "Sonuç: geçti"


def test_tc222_nearest_rank_percentile():
    values = [100.0] * 96 + [900.0] * 4
    assert loadtest.percentile(values, 95) == 100.0
    assert loadtest.percentile(values, 50) == 100.0
    assert loadtest.percentile(values, 97) == 900.0
    assert len(values) == 100
    assert loadtest.percentile([3.0, 1.0, 2.0], 100) == 3.0
    with pytest.raises(ValueError):
        loadtest.percentile([], 95)


# --- TC-318: mix and candidates ----------------------------------------------------


def test_tc318_operation_mix():
    rng = random.Random(42)
    counts = Counter(loadtest.pick_operation(rng) for _ in range(10_000))
    expected = dict(zip(loadtest.OPERATIONS, (40, 20, 20, 10, 10), strict=True))
    for op, share in expected.items():
        assert abs(counts[op] / 100 - share) <= 2, (op, counts[op])


@pytest.fixture
def seeded_db(file_db):  # noqa: F811
    """Eligible and ineligible members and copies in a migrated file database."""
    from billing.models import EntryKind
    from tests.support.factories import make_book, make_charge, make_copy, make_loan, make_member

    eligible = set()
    for n in range(1, 13):
        email = None if n % 2 else f"uye{n}@example.invalid"
        eligible.add(make_member(f"Üye Kaya{n}", email=email, member_no=n).member_no)
    book = make_book("Güz Sonu Çiçekleri", "Ayşe Öz")
    shelf = {make_copy(book).barcode for _ in range(15)}
    busy = make_member("Ödünçlü Üye", member_no=20)
    make_loan(member=busy, copy=make_copy(book))  # open loan: ON_LOAN copy
    make_member("Pasif Üye", member_no=21, is_active=False)
    make_member(member_no=22, anonymized=True)
    debtor = make_member("Borçlu Üye", member_no=23)
    make_charge(debtor, EntryKind.FINE, 500)
    return file_db, eligible, shelf


@pytest.mark.django_db(transaction=True)
def test_tc318_candidates_split_disjoint_over_read_only_connection(seeded_db, monkeypatch):
    path, eligible, shelf = seeded_db
    uris = []
    real_connect = sqlite3.connect

    def recording_connect(database, *args, **kwargs):
        uris.append((database, kwargs.get("uri")))
        return real_connect(database, *args, **kwargs)

    monkeypatch.setattr(loadtest.sqlite3, "connect", recording_connect)
    con = loadtest.connect_ro(path)
    assert uris and "mode=ro" in uris[0][0] and uris[0][1] is True
    with pytest.raises(sqlite3.OperationalError):
        con.execute("DELETE FROM member")
    plans, max_open = loadtest.load_candidates(con, 5, random.Random(42))
    assert max_open == 3
    assert len(plans) == 5
    members = [set(plan.members) for plan in plans]
    copies = [set(plan.copies) for plan in plans]
    assert set().union(*members) == eligible
    assert set().union(*copies) == shelf
    assert sum(map(len, members)) == len(eligible)
    assert sum(map(len, copies)) == len(shelf)
    assert all(plan.book_words and plan.member_words for plan in plans)
    assert "Çiçekleri" in plans[0].book_words


# --- TC-353: seed-only guard (ADR-0058) ---------------------------------------------


def plain_db(path: Path, emails: list[str | None]) -> Path:
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE member (id INTEGER PRIMARY KEY, email TEXT)")
    con.executemany("INSERT INTO member (email) VALUES (?)", [(e,) for e in emails])
    con.commit()
    con.close()
    return path


def test_tc353_real_member_stops_before_any_request(tmp_path, monkeypatch, capsys):
    db = plain_db(tmp_path / "gercek.sqlite3", ["uye1@example.invalid", "ali@ornek.com", None])
    password = tmp_path / "parola.txt"
    password.write_text("parola\n", encoding="utf-8")

    def no_requests(*args, **kwargs):
        raise AssertionError("an HTTP client was created")

    monkeypatch.setattr(loadtest, "Client", no_requests)
    monkeypatch.setattr(loadtest.urllib.request, "urlopen", no_requests)
    code = loadtest.main([
        "--base-url", "http://127.0.0.1:9", "--user", "demo",
        "--password-file", str(password), "--db", str(db),
    ])
    assert code == 1
    assert capsys.readouterr().err.strip() == "Tohum verisi olmayan veritabanı"


def test_tc353_seed_emails_and_blank_emails_pass(tmp_path):
    db = plain_db(tmp_path / "tohum.sqlite3", ["uye1@example.invalid", None, "uye3@example.invalid"])
    loadtest.check_seed_only(loadtest.connect_ro(db))  # no exception
    other = plain_db(tmp_path / "karisik.sqlite3", ["uye1@example.invalid.com"])
    with pytest.raises(loadtest.NotSeedData):
        loadtest.check_seed_only(loadtest.connect_ro(other))


# --- TC-354: worker state (small decision 10) ---------------------------------------


class FakeClient:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str, dict | None]] = []

    def request(self, method: str, path: str, fields: dict | None = None) -> int:
        self.requests.append((method, path, fields))
        return 303 if method == "POST" else 200


def scripted(monkeypatch, ops: list[str]) -> None:
    sequence = iter(ops)
    monkeypatch.setattr(loadtest, "pick_operation", lambda rng: next(sequence))


def test_tc354_repick_without_own_loans_and_renewal_pool(monkeypatch):
    client = FakeClient()
    plan = loadtest.WorkerPlan(members=[7], copies=["00000005"], book_words=["Güz"],
                               member_words=["Kaya"])
    worker = loadtest.Worker(client, plan, random.Random(1), lambda barcode: 77, max_open_loans=3)
    scripted(monkeypatch, [
        loadtest.RETURN, loadtest.RENEW, loadtest.CHECKOUT,  # first two are re-picked
        loadtest.RENEW,
        loadtest.RENEW, loadtest.RETURN,  # the renewed loan is not renewed again
        loadtest.RENEW, loadtest.CHECKOUT,  # the returned copy is back on the shelf
    ])
    for _ in range(4):
        worker.step()
    assert client.requests == [
        ("POST", "/odunc/", {"uye": "7", "nusha": "00000005"}),
        ("POST", "/odunc/77/uzat/", {}),
        ("POST", "/iade/", {"nusha": "00000005"}),
        ("POST", "/odunc/", {"uye": "7", "nusha": "00000005"}),
    ]
    counts = {op: len(s.durations_ms) for op, s in worker.stats.items()}
    assert counts == {"kitap arama": 0, "ödünç": 2, "iade": 1, "uzatma": 1, "üye arama": 0}
    assert all(s.errors == 0 for s in worker.stats.values())


def test_tc354_failed_request_counts_as_error(monkeypatch):
    class Refusing(FakeClient):
        def request(self, method, path, fields=None):
            super().request(method, path, fields)
            return 200  # a rule violation is shown with 200, not 303

    client = Refusing()
    plan = loadtest.WorkerPlan(members=[7], copies=["00000005"], book_words=["Güz"],
                               member_words=["Kaya"])
    worker = loadtest.Worker(client, plan, random.Random(1), lambda barcode: 77, max_open_loans=3)
    scripted(monkeypatch, [loadtest.CHECKOUT, loadtest.BOOK_SEARCH, loadtest.MEMBER_SEARCH])
    for _ in range(3):
        worker.step()
    assert worker.stats[loadtest.CHECKOUT].errors == 1
    assert worker.stats[loadtest.BOOK_SEARCH].errors == 0
    assert client.requests[1] == ("GET", "/kitaplar/?q=G%C3%BCz", None)
    assert client.requests[2] == ("GET", "/uyeler/?q=Kaya", None)


# --- TC-355: no Django, testpaths (small decision 11) --------------------------------


def test_tc355_script_does_not_import_django():
    code = "import sys, scripts.loadtest; print('django' in sys.modules)"
    result = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, capture_output=True,
                            text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False"
    helped = subprocess.run([sys.executable, "scripts/loadtest.py", "--help"], cwd=REPO_ROOT,
                            capture_output=True, text=True, timeout=60)
    assert helped.returncode == 0 and "--password-file" in helped.stdout


def test_tc355_testpaths_include_scripts_and_every_test_folder():
    config = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    testpaths = config["tool"]["pytest"]["ini_options"]["testpaths"]
    assert "scripts" in testpaths
    folders = {path.parent.parent.name for path in REPO_ROOT.glob("*/tests/__init__.py")}
    folders.add("tests")
    assert folders <= set(testpaths)


# --- TC-356: login, CSRF header and cookies (KL-17) ----------------------------------


class _Handler(http.server.BaseHTTPRequestHandler):
    log: list[tuple[str, str, dict, str]] = []

    def log_message(self, *args):  # keep the test output quiet
        pass

    def _cookies(self) -> dict[str, str]:
        header = self.headers.get("Cookie", "")
        pairs = [part.strip().split("=", 1) for part in header.split(";") if "=" in part]
        return {k: v for k, v in pairs}

    def _record(self, body: str = "") -> None:
        _Handler.log.append(
            (self.command, self.path, {k.lower(): v for k, v in self.headers.items()}, body)
        )

    def _send(self, status: int, headers: list[tuple[str, str]] = ()) -> None:
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_GET(self):
        self._record()
        if self.path == "/giris/":
            self._send(200, [("Set-Cookie", "csrftoken=tok1; Path=/")])
        elif self.path.startswith("/kitaplar/") and self._cookies().get("sessionid") == "s1":
            self._send(200)
        else:
            self._send(302, [("Location", "/giris/")])

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        self._record(body)
        token = self.headers.get("X-CSRFToken")
        if self.path == "/giris/":
            form = urllib.parse.parse_qs(body)
            if token == "tok1" and form == {"username": ["demo"], "password": ["parola"]}:
                self._send(302, [
                    ("Location", "/"),
                    ("Set-Cookie", "sessionid=s1; Path=/; Secure; HttpOnly"),
                    ("Set-Cookie", "csrftoken=tok2; Path=/; Secure"),
                ])
            else:
                self._send(403)
        elif token == "tok2" and self._cookies().get("sessionid") == "s1":
            self._send(303, [("Location", self.path)])
        else:
            self._send(403)


@pytest.fixture
def stub_server():
    _Handler.log = []
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_tc356_login_csrf_header_and_secure_cookie_over_http(stub_server):
    client = loadtest.Client(stub_server)
    assert client.login("demo", "parola") is True
    assert client.request("GET", "/kitaplar/?q=G%C3%BCz") == 200
    assert client.request("POST", "/iade/", {"nusha": "00000001"}) == 303
    methods_paths = [(m, p) for m, p, _, _ in _Handler.log]
    assert methods_paths == [
        ("GET", "/giris/"), ("POST", "/giris/"), ("GET", "/kitaplar/?q=G%C3%BCz"),
        ("POST", "/iade/"),
    ]  # neither the 302 after login nor the 303 is followed
    login_post = _Handler.log[1]
    assert login_post[2]["x-csrftoken"] == "tok1"
    assert _Handler.log[2][2]["cookie"].count("sessionid=s1") == 1  # Secure cookie over HTTP
    assert _Handler.log[3][2]["x-csrftoken"] == "tok2"  # the rotated token


def test_tc356_wrong_password_is_refused(stub_server):
    client = loadtest.Client(stub_server)
    assert client.login("demo", "yanlis") is False

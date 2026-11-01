"""NFR-01 load test with the standard library (ADR-0031, KL-17, plan G18).

Usage::

    python scripts/loadtest.py --base-url http://127.0.0.1:8000 --user U \\
        --password-file F --db PATH --workers 5 --duration 120 [--seed 42]

The script talks to waitress directly (no Caddy). It opens ``--db`` read-only,
refuses a database with a non-seed member (ADR-0058), splits members without
blockers and copies on the shelf between the workers, and runs the mix
40/20/20/10/10 (book search, checkout, check-in, renewal, member search).
Checkout, renewal and check-in work on the worker's own loans. The report
gives requests, p50, p95 and errors per operation; the exit code is 0 only
when every operation has p95 < 500 ms and no errors.

It never imports Django (G17–G18 small decision 11).
"""

from __future__ import annotations

import argparse
import http.cookiejar
import math
import random
import re
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

BOOK_SEARCH = "kitap arama"
CHECKOUT = "ödünç"
RETURN = "iade"
RENEW = "uzatma"
MEMBER_SEARCH = "üye arama"
OPERATIONS = (BOOK_SEARCH, CHECKOUT, RETURN, RENEW, MEMBER_SEARCH)
WEIGHTS = (40, 20, 20, 10, 10)  # ADR-0031
P95_LIMIT_MS = 500.0  # NFR-01
TIMEOUT_SECONDS = 30
SEED_EMAIL_SUFFIX = "@example.invalid"
NOT_SEED_MESSAGE = "Tohum verisi olmayan veritabanı"
_WORD = re.compile(r"[^\W\d_]{3,}")


# --- Report ----------------------------------------------------------------------


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile: the ⌈p/100 · n⌉-th smallest value; O(n log n)."""
    if not values:
        raise ValueError("percentile of no values")
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


def pick_operation(rng: random.Random) -> str:
    return rng.choices(OPERATIONS, weights=WEIGHTS)[0]


@dataclass
class OpStats:
    durations_ms: list[float] = field(default_factory=list)
    errors: int = 0

    def merge(self, other: OpStats) -> None:
        self.durations_ms.extend(other.durations_ms)
        self.errors += other.errors


def _empty_stats() -> dict[str, OpStats]:
    return {op: OpStats() for op in OPERATIONS}


def passes(stats: dict[str, OpStats]) -> bool:
    """Every operation has requests, p95 < 500 ms and no errors."""
    for op in OPERATIONS:
        s = stats[op]
        if not s.durations_ms or s.errors or percentile(s.durations_ms, 95) >= P95_LIMIT_MS:
            return False
    return True


def report_lines(stats: dict[str, OpStats]) -> list[str]:
    lines = [f"{'işlem':<12}{'istek':>8}{'p50 (ms)':>11}{'p95 (ms)':>11}{'hata':>7}"]
    for op in OPERATIONS:
        s = stats[op]
        if s.durations_ms:
            p50 = f"{percentile(s.durations_ms, 50):.1f}"
            p95 = f"{percentile(s.durations_ms, 95):.1f}"
        else:
            p50 = p95 = "-"
        lines.append(f"{op:<12}{len(s.durations_ms):>8}{p50:>11}{p95:>11}{s.errors:>7}")
    lines.append("Sonuç: geçti" if passes(stats) else "Sonuç: kaldı")
    return lines


# --- Database (read-only) -----------------------------------------------------------


class NotSeedData(Exception):
    """``--db`` holds a member whose e-mail is not a seed address (ADR-0058)."""


def ro_uri(path: Path) -> str:
    return f"file:{urllib.parse.quote(str(Path(path).resolve()))}?mode=ro"


def connect_ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(ro_uri(path), uri=True)


def check_seed_only(con: sqlite3.Connection) -> None:
    rows = con.execute("SELECT email FROM member WHERE email IS NOT NULL")
    if any(not email.endswith(SEED_EMAIL_SUFFIX) for (email,) in rows):
        raise NotSeedData(NOT_SEED_MESSAGE)


@dataclass
class WorkerPlan:
    members: list[int]  # member numbers
    copies: list[str]  # barcodes of copies on the shelf
    book_words: list[str]
    member_words: list[str]


# Active, not anonymized, no open loan and a zero balance: no checkout blocker
# and renewals are allowed (FR-08, FR-10).
_ELIGIBLE_MEMBERS = """
SELECT m.member_no FROM member m
WHERE m.is_active = 1 AND m.anonymized_at IS NULL
  AND NOT EXISTS (SELECT 1 FROM loan l WHERE l.member_id = m.id AND l.closed_on IS NULL)
  AND COALESCE((
    SELECT SUM(CASE WHEN e.kind IN ('FINE', 'FEE') THEN e.amount_kurus
                    WHEN e.kind IN ('PAYMENT', 'WAIVER', 'CANCELLATION') THEN -e.amount_kurus
                    ELSE 0 END)
    FROM ledger_entry e WHERE e.member_id = m.id), 0) = 0
ORDER BY m.member_no
"""


def _words(texts: list[str]) -> list[str]:
    return list(dict.fromkeys(word for text in texts for word in _WORD.findall(text)))


def load_candidates(
    con: sqlite3.Connection, workers: int, rng: random.Random
) -> tuple[list[WorkerPlan], int]:
    """Split the candidates into ``workers`` disjoint plans; also the loan limit."""
    members = [row[0] for row in con.execute(_ELIGIBLE_MEMBERS)]
    copies = [
        row[0]
        for row in con.execute("SELECT barcode FROM copy WHERE status = 'ON_SHELF' ORDER BY barcode")
    ]
    book_words = _words([row[0] for row in con.execute("SELECT title FROM book ORDER BY id")])
    surnames = [
        row[0].split()[-1]
        for row in con.execute(
            "SELECT full_name FROM member WHERE full_name IS NOT NULL ORDER BY id"
        )
        if row[0].split()
    ]
    member_words = _words(surnames)
    (max_open,) = con.execute("SELECT max_open_loans FROM library_settings WHERE id = 1").fetchone()
    rng.shuffle(members)
    rng.shuffle(copies)
    plans = [
        WorkerPlan(members[i::workers], copies[i::workers], book_words, member_words)
        for i in range(workers)
    ]
    return plans, max_open


# --- HTTP client -----------------------------------------------------------------


class _LocalCookiePolicy(http.cookiejar.DefaultCookiePolicy):
    """Send ``Secure`` cookies over plain HTTP too: the script talks to
    waitress on the server itself, behind Caddy's TLS (ADR-0031)."""

    def return_ok_secure(self, cookie, request) -> bool:
        return True


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    """One staff session: its own cookies; POSTs carry ``X-CSRFToken`` from
    the ``csrftoken`` cookie (KL-17). Redirects are not followed."""

    def __init__(self, base_url: str, timeout: float = TIMEOUT_SECONDS) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.jar = http.cookiejar.CookieJar(policy=_LocalCookiePolicy())
        self.opener = urllib.request.build_opener(
            _NoRedirect(), urllib.request.HTTPCookieProcessor(self.jar)
        )

    def _cookie(self, name: str) -> str | None:
        return next((c.value for c in self.jar if c.name == name), None)

    def request(self, method: str, path: str, fields: dict | None = None) -> int:
        """The HTTP status; network errors propagate."""
        data = None
        if method == "POST":
            data = urllib.parse.urlencode(fields or {}).encode("utf-8")
        request = urllib.request.Request(self.base_url + path, data=data, method=method)
        if method == "POST":
            token = self._cookie("csrftoken")
            if token:
                request.add_header("X-CSRFToken", token)
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                response.read()
                return response.status
        except urllib.error.HTTPError as exc:
            exc.read()
            exc.close()
            return exc.code

    def login(self, user: str, password: str) -> bool:
        self.request("GET", "/giris/")
        status = self.request("POST", "/giris/", {"username": user, "password": password})
        return status == 302 and self._cookie("sessionid") is not None


# --- Worker ------------------------------------------------------------------------


@dataclass
class _OwnLoan:
    barcode: str
    member_no: int
    loan_id: int | None


class Worker:
    """One thread's state: its members and shelf copies, its open loans and
    the subset that may still be renewed (small decision 10)."""

    def __init__(
        self,
        client,
        plan: WorkerPlan,
        rng: random.Random,
        lookup_loan: Callable[[str], int | None],
        max_open_loans: int,
    ) -> None:
        self.client = client
        self.rng = rng
        self.lookup_loan = lookup_loan
        self.max_open = max_open_loans
        self.members = list(plan.members)
        self.shelf = list(plan.copies)
        self.book_words = plan.book_words or [""]
        self.member_words = plan.member_words or [""]
        self.loans: list[_OwnLoan] = []
        self.renewable: list[_OwnLoan] = []
        self.open_count: dict[int, int] = {}
        self.stats = _empty_stats()

    def _free_members(self) -> list[int]:
        return [m for m in self.members if self.open_count.get(m, 0) < self.max_open]

    def _possible(self, op: str) -> bool:
        if op == RETURN:
            return bool(self.loans)
        if op == RENEW:
            return bool(self.renewable)
        if op == CHECKOUT:
            return bool(self.shelf) and bool(self._free_members())
        return True

    def next_operation(self) -> str:
        """Pick again, without a request, while the pick cannot run."""
        while True:
            op = pick_operation(self.rng)
            if self._possible(op):
                return op

    def _timed(self, op: str, method: str, path: str, fields: dict | None, expected: int) -> bool:
        start = time.perf_counter()
        try:
            status = self.client.request(method, path, fields)
        except (urllib.error.URLError, OSError):
            status = 0
        self.stats[op].durations_ms.append((time.perf_counter() - start) * 1000)
        ok = status == expected
        if not ok:
            self.stats[op].errors += 1
        return ok

    def _take(self, items: list):
        index = self.rng.randrange(len(items))
        items[index], items[-1] = items[-1], items[index]
        return items.pop()

    def step(self) -> None:
        op = self.next_operation()
        if op == BOOK_SEARCH:
            q = urllib.parse.quote(self.rng.choice(self.book_words))
            self._timed(op, "GET", f"/kitaplar/?q={q}", None, 200)
        elif op == MEMBER_SEARCH:
            q = urllib.parse.quote(self.rng.choice(self.member_words))
            self._timed(op, "GET", f"/uyeler/?q={q}", None, 200)
        elif op == CHECKOUT:
            member_no = self.rng.choice(self._free_members())
            barcode = self._take(self.shelf)
            fields = {"uye": str(member_no), "nusha": barcode}
            if self._timed(op, "POST", "/odunc/", fields, 303):
                loan = _OwnLoan(barcode, member_no, self.lookup_loan(barcode))
                self.loans.append(loan)
                if loan.loan_id is not None:
                    self.renewable.append(loan)
                self.open_count[member_no] = self.open_count.get(member_no, 0) + 1
        elif op == RENEW:
            loan = self._take(self.renewable)  # leaves the renewal pool either way
            self._timed(op, "POST", f"/odunc/{loan.loan_id}/uzat/", {}, 303)
        else:
            loan = self._take(self.loans)
            if loan in self.renewable:
                self.renewable.remove(loan)
            if self._timed(op, "POST", "/iade/", {"nusha": loan.barcode}, 303):
                self.shelf.append(loan.barcode)
                self.open_count[loan.member_no] -= 1

    def run(self, deadline: float) -> None:
        while time.monotonic() < deadline:
            self.step()


# --- Main ------------------------------------------------------------------------


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"pozitif bir tam sayı olmalı: {value}") from None
    if number <= 0:
        raise argparse.ArgumentTypeError(f"pozitif bir tam sayı olmalı: {value}")
    return number


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "NFR-01 yük testi: tohum verili bir sunucuya 5 eşzamanlı personel gibi istek "
            "atar ve işlem türü başına p50, p95 ve hata sayısını raporlar."
        )
    )
    parser.add_argument("--base-url", required=True, help="Waitress adresi, ör. http://127.0.0.1:8000")
    parser.add_argument("--user", required=True, help="Personel kullanıcı adı")
    parser.add_argument("--password-file", required=True, type=Path, help="Parolanın bulunduğu dosya")
    parser.add_argument("--db", required=True, type=Path, help="Sunucunun SQLite veritabanı (salt okunur açılır)")
    parser.add_argument("--workers", type=_positive_int, default=5, help="İş parçacığı sayısı; varsayılan 5")
    parser.add_argument("--duration", type=_positive_int, default=120, help="Süre (saniye); varsayılan 120")
    parser.add_argument("--seed", type=int, default=42, help="Rastgele üretecin tohumu; varsayılan 42")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        password = args.password_file.read_text(encoding="utf-8-sig").rstrip("\r\n")
    except OSError:
        print(f"Parola dosyası okunamadı: {args.password_file}", file=sys.stderr)
        return 1
    try:
        con = connect_ro(args.db)
        check_seed_only(con)
        plans, max_open = load_candidates(con, args.workers, random.Random(args.seed))
        con.close()
    except NotSeedData as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except sqlite3.Error as exc:
        print(f"Veritabanı okunamadı: {args.db}: {exc}", file=sys.stderr)
        return 1

    clients = []
    for _ in plans:
        client = Client(args.base_url)
        try:
            ok = client.login(args.user, password)
        except (urllib.error.URLError, OSError) as exc:
            print(f"Sunucuya bağlanılamadı: {args.base_url}: {exc}", file=sys.stderr)
            return 1
        if not ok:
            print(f"Giriş başarısız: {args.user}", file=sys.stderr)
            return 1
        clients.append(client)

    deadline = time.monotonic() + args.duration
    workers: list[Worker] = []

    def run(index: int) -> None:
        lookup_con = connect_ro(args.db)

        def lookup(barcode: str) -> int | None:
            row = lookup_con.execute(
                "SELECT l.id FROM loan l JOIN copy c ON c.id = l.copy_id "
                "WHERE c.barcode = ? AND l.closed_on IS NULL",
                (barcode,),
            ).fetchone()
            return row[0] if row else None

        try:
            worker = Worker(
                clients[index], plans[index], random.Random(args.seed * 1000 + index),
                lookup, max_open,
            )
            workers.append(worker)
            worker.run(deadline)
        finally:
            lookup_con.close()

    threads = [threading.Thread(target=run, args=(i,)) for i in range(len(plans))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    total = _empty_stats()
    for worker in workers:
        for op, s in worker.stats.items():
            total[op].merge(s)
    for line in report_lines(total):
        print(line)
    return 0 if passes(total) else 1


if __name__ == "__main__":
    sys.exit(main())

"""Backup, encrypted export and restore commands (G14): TC-186…TC-200,
TC-299 (command side), TC-300…TC-304 and TC-320…TC-329 (ADR-0054, G14–G16
small decisions 1–4).

Every test runs on a migrated temporary database file (``ops``). The
"database unchanged" checks compare the main file, the counts and the folder
listing; a failed restore must not close connections or rename anything.
"""

from __future__ import annotations

import re
import sqlite3
import struct
import threading
from datetime import date
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import CommandError, call_command
from django.db import connections, transaction

from administration.models import Job, JobRun
from operations import backup, libx
from operations.tests.conftest import PASSPHRASE, Ops
from operations.tests.support import counts, lock_held_elsewhere, manage, migration_rows
from tests.support.factories import make_book, make_copy, make_loan, make_member

pytestmark = pytest.mark.django_db(transaction=True)

INITIAL = (2, 3, 1)


def populate() -> tuple[int, int, int]:
    first = make_member()
    make_member("Mehmet Kaya", "0555 222 33 44")
    book = make_book()
    copies = [make_copy(book) for _ in range(3)]
    make_loan(first, copies[0])
    return INITIAL


def run(*args: str) -> str:
    out = StringIO()
    call_command(*args, stdout=out)
    return out.getvalue()


def fails(*args: str) -> CommandError:
    with pytest.raises(CommandError) as info:
        call_command(*args, stdout=StringIO())
    assert info.value.returncode == 1
    return info.value


def guard_copies(db: Path) -> list[Path]:
    pattern = re.compile(re.escape(db.name) + r"\.pre-restore-\d{8}-\d{6}(-wal|-shm)?$")
    return sorted(p for p in db.parent.iterdir() if pattern.match(p.name))


def close_and_delete(db: Path) -> None:
    connections.close_all()
    for suffix in ("", "-wal", "-shm"):
        Path(str(db) + suffix).unlink(missing_ok=True)


def take_backup(ops: Ops, day: str = "2026-11-02") -> Path:
    run("backup_db", "--date", day)
    return ops.backups / f"library-{day.replace('-', '')}.sqlite3"


def take_export(ops: Ops, day: str = "2026-11-02") -> Path:
    run("export_backup", "--date", day)
    return ops.exports / f"library-export-{day.replace('-', '')}.libx"


class Unchanged:
    """Snapshot of the live database: main file bytes, counts and folder."""

    def __init__(self, db: Path) -> None:
        self.db = db
        self.data = db.read_bytes()
        self.counts = counts(db)
        self.names = self.listing()

    def listing(self) -> list[str]:
        # The lock file stays after the first restore attempt (KL-4).
        return sorted(p.name for p in self.db.parent.iterdir() if not p.name.endswith(".app.lock"))

    def check(self) -> None:
        assert self.db.read_bytes() == self.data
        assert counts(self.db) == self.counts
        assert self.listing() == self.names
        assert guard_copies(self.db) == []


# --- backup_db ------------------------------------------------------------------


def test_tc186_backup_file_counts_and_job(ops: Ops) -> None:
    populate()
    output = run("backup_db", "--date", "2026-11-02")
    target = ops.backups / "library-20261102.sqlite3"
    assert output.splitlines() == [f"Yedek alındı: {target}", "Silinen eski yedek: 0"]
    con = sqlite3.connect(target)
    try:
        assert con.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        # A self-contained file: rollback journal, not WAL.
        assert con.execute("PRAGMA journal_mode").fetchone() == ("delete",)
    finally:
        con.close()
    assert counts(target) == INITIAL
    run_row = JobRun.objects.get()
    assert (run_row.job, run_row.run_on, run_row.status, run_row.detail) == (
        Job.BACKUP,
        date(2026, 11, 2),
        JobRun.Status.SUCCESS,
        "library-20261102.sqlite3, silinen=0",
    )
    assert sorted(p.name for p in ops.backups.iterdir()) == ["library-20261102.sqlite3"]


def test_tc187_old_backups_deleted_after_success(ops: Ops) -> None:
    for name in ("library-20261201.sqlite3", "library-20261130.sqlite3", "notlar.txt"):
        (ops.backups / name).write_bytes(b"eski")
    output = run("backup_db", "--date", "2026-12-31")
    assert output.splitlines()[-1] == "Silinen eski yedek: 1"
    assert sorted(p.name for p in ops.backups.iterdir()) == [
        "library-20261201.sqlite3",
        "library-20261231.sqlite3",
        "notlar.txt",
    ]


def test_tc188_missing_backup_folder(ops: Ops, settings) -> None:
    missing = ops.backups / "takılı olmayan disk"
    settings.LIBRARY_BACKUP_DIR = str(missing)
    error = fails("backup_db", "--date", "2026-11-02")
    assert str(error) == f"Yedek klasörü bulunamadı: {missing}"
    assert JobRun.objects.get().status == JobRun.Status.FAILED
    assert not (ops.backups / "takılı olmayan disk").exists()


def test_tc188_tc328_failed_write_keeps_old_files(ops: Ops, monkeypatch) -> None:
    old = ops.backups / "library-20260901.sqlite3"  # older than 30 days
    same_day = ops.backups / "library-20261102.sqlite3"
    old.write_bytes(b"eski yedek")
    same_day.write_bytes(b"ayni gunun eski yedegi")

    def refuse(src, dst):
        raise PermissionError(13, "Erişim engellendi", str(dst))

    monkeypatch.setattr(backup, "_replace", refuse)
    error = fails("backup_db", "--date", "2026-11-02")
    assert str(error).startswith("Yedek alınamadı: PermissionError: ")
    assert "Erişim engellendi" in str(error)
    assert old.read_bytes() == b"eski yedek"
    assert same_day.read_bytes() == b"ayni gunun eski yedegi"
    assert sorted(p.name for p in ops.backups.iterdir()) == [old.name, same_day.name]
    run_row = JobRun.objects.get()
    assert run_row.status == JobRun.Status.FAILED
    assert "PermissionError" in run_row.detail


def test_tc189_paths_with_spaces_and_turkish_letters(ops: Ops) -> None:
    populate()
    backup_file = take_backup(ops)
    export_file = take_export(ops)
    assert " " in str(backup_file) and "Ğüş" in str(backup_file)
    assert backup_file.is_file() and export_file.is_file()
    assert export_file.parent == ops.exports


def test_tc190_backup_during_an_open_write(ops: Ops) -> None:
    """The backup holds the committed state while another connection has an
    open write transaction (service level: the command would also write a
    ``job_run`` row and wait for the writer)."""
    populate()
    started, finish = threading.Event(), threading.Event()

    def writer() -> None:
        try:
            with transaction.atomic():
                make_member("Yazılıyor Henüz")
                started.set()
                finish.wait(timeout=30)
        finally:
            connections.close_all()

    thread = threading.Thread(target=writer)
    thread.start()
    assert started.wait(timeout=30)
    try:
        result = backup.backup_db(date(2026, 11, 2))
    finally:
        finish.set()
        thread.join(timeout=30)
    assert counts(result.path) == INITIAL
    con = sqlite3.connect(result.path)
    try:
        assert con.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    finally:
        con.close()
    assert counts(ops.db)[0] == INITIAL[0] + 1


# --- restore_backup -------------------------------------------------------------


def test_tc191_backup_then_restore_into_a_deleted_database(ops: Ops) -> None:
    populate()
    backup_file = take_backup(ops)
    close_and_delete(ops.db)
    output = run("restore_backup", str(backup_file), "--yes")
    assert output.splitlines() == [
        "Geri yüklendi: üye=2, nüsha=3, ödünç=1",
        "Gerekirse python manage.py migrate çalıştırın.",
    ]
    assert counts(ops.db) == INITIAL
    assert guard_copies(ops.db) == []


def test_tc320_restore_keeps_the_current_files(ops: Ops) -> None:
    populate()
    backup_file = take_backup(ops)
    make_member("Yedekten Sonra")
    connections.close_all()
    wal, shm = Path(f"{ops.db}-wal"), Path(f"{ops.db}-shm")
    wal.write_bytes(b"yarim kalmis wal")  # e.g. left by a killed process
    shm.write_bytes(b"shm")
    before = ops.db.read_bytes()

    output = run("restore_backup", str(backup_file), "--yes")

    main, guard_shm, guard_wal = guard_copies(ops.db)
    assert guard_wal.name == main.name + "-wal" and guard_shm.name == main.name + "-shm"
    assert main.read_bytes() == before
    assert guard_wal.read_bytes() == b"yarim kalmis wal"
    assert guard_shm.read_bytes() == b"shm"
    assert counts(main) == (3, 3, 1)
    assert counts(ops.db) == INITIAL
    assert output.splitlines() == [
        "Geri yüklendi: üye=2, nüsha=3, ödünç=1",
        f"Önceki veritabanı korundu: {main}",
        "Gerekirse python manage.py migrate çalıştırın.",
    ]


def test_tc321_corrupt_current_database_is_kept(ops: Ops) -> None:
    populate()
    backup_file = take_backup(ops)
    close_and_delete(ops.db)
    ops.db.write_bytes(b"\x00bozuk veritabani\xff" * 100)
    run("restore_backup", str(backup_file), "--yes")
    (guard,) = guard_copies(ops.db)
    assert guard.read_bytes() == b"\x00bozuk veritabani\xff" * 100
    assert counts(ops.db) == INITIAL


@pytest.mark.parametrize("kind", ["not_sqlite", "no_migrations", "liby"])
def test_tc322_tc196_invalid_backup_file(ops: Ops, tmp_path: Path, kind: str) -> None:
    populate()
    candidate = tmp_path / "aday.sqlite3"
    if kind == "not_sqlite":
        candidate.write_bytes(b"bu bir veritabani degil" * 50)
    elif kind == "liby":
        candidate.write_bytes(b"LIBY" + libx.encrypt(b"x", PASSPHRASE, n=2**10)[4:])
    else:
        con = sqlite3.connect(candidate)
        con.execute("CREATE TABLE member (id INTEGER)")
        con.commit()
        con.close()
    unchanged = Unchanged(ops.db)
    error = fails("restore_backup", str(candidate), "--yes")
    assert str(error) == f"Geçerli bir veritabanı yedeği değil: {candidate}"
    unchanged.check()


def test_tc327_restore_runs_no_migrations(ops: Ops) -> None:
    populate()
    backup_file = take_backup(ops)
    con = sqlite3.connect(backup_file)
    con.execute("DELETE FROM django_migrations WHERE id = (SELECT MAX(id) FROM django_migrations)")
    con.commit()
    con.close()
    expected = migration_rows(backup_file)
    output = run("restore_backup", str(backup_file), "--yes")
    assert migration_rows(ops.db) == expected
    assert "Gerekirse python manage.py migrate çalıştırın." in output


def test_tc199_application_running(ops: Ops) -> None:
    populate()
    backup_file = take_backup(ops)
    unchanged = Unchanged(ops.db)
    with lock_held_elsewhere(ops.db):
        error = fails("restore_backup", str(backup_file), "--yes")
    assert str(error) == "Uygulama çalışıyor; önce servisi durdurun"
    unchanged.check()


def test_tc200_usage_errors_exit_two(ops: Ops, tmp_path: Path) -> None:
    db = tmp_path / "ayri" / "library.sqlite3"
    env = {"LIBRARY_DB_PATH": str(db)}
    for args in ([], [str(tmp_path / "yedek.sqlite3")]):
        result = manage("restore_backup", *args, env=env)
        assert result.returncode == 2, result.stderr
        assert "--yes" in result.stderr or "path" in result.stderr.lower()
    assert not db.parent.exists()


def test_tc301_missing_file(ops: Ops) -> None:
    populate()
    unchanged = Unchanged(ops.db)
    error = fails("restore_backup", "yok.sqlite3", "--yes")
    assert str(error) == "Dosya bulunamadı: yok.sqlite3"
    unchanged.check()


# --- export_backup and .libx restore --------------------------------------------


def test_tc192_export_header(ops: Ops, monkeypatch) -> None:
    monkeypatch.setattr(backup, "KDF_PARAMS", {"n": 2**17, "r": 8, "p": 1})
    populate()
    take_backup(ops)
    output = run(
        "export_backup", "--date", "2026-11-02", "--passphrase-file", str(ops.passphrase_file)
    )
    target = ops.exports / "library-export-20261102.libx"
    assert output.splitlines() == [
        f"Dışa aktarıldı: {target} (kaynak: library-20261102.sqlite3)",
        "Silinen eski dışa aktarma: 0",
    ]
    blob = target.read_bytes()
    assert struct.unpack(">4sBIII", blob[:17]) == (b"LIBX", 1, 2**17, 8, 1)
    assert len(blob[17:33]) == 16 and len(blob[33:45]) == 12
    run_row = JobRun.objects.get(job=Job.EXPORT)
    assert (run_row.run_on, run_row.status, run_row.detail) == (
        date(2026, 11, 2),
        JobRun.Status.SUCCESS,
        "library-export-20261102.libx (kaynak library-20261102.sqlite3), silinen=0",
    )


def test_tc193_export_restored_into_an_empty_environment(ops: Ops) -> None:
    populate()
    take_backup(ops)
    export_file = take_export(ops)
    close_and_delete(ops.db)
    output = run(
        "restore_backup", str(export_file), "--passphrase-file", str(ops.passphrase_file), "--yes"
    )
    assert output.splitlines()[0] == "Geri yüklendi: üye=2, nüsha=3, ödünç=1"
    assert counts(ops.db) == INITIAL


def test_tc194_wrong_passphrase(ops: Ops, tmp_path: Path) -> None:
    populate()
    take_backup(ops)
    export_file = take_export(ops)
    wrong = tmp_path / "yanlis.txt"
    wrong.write_text("yanlış parola\n", encoding="utf-8")
    unchanged = Unchanged(ops.db)
    error = fails("restore_backup", str(export_file), "--passphrase-file", str(wrong), "--yes")
    assert str(error) == "Parola hatalı ya da dosya bozuk"
    unchanged.check()


@pytest.mark.parametrize("index", [20, -5])  # a salt byte; a ciphertext byte
def test_tc195_changed_byte(ops: Ops, index: int) -> None:
    populate()
    take_backup(ops)
    export_file = take_export(ops)
    blob = bytearray(export_file.read_bytes())
    blob[index] ^= 0x40
    export_file.write_bytes(bytes(blob))
    unchanged = Unchanged(ops.db)
    error = fails("restore_backup", str(export_file), "--yes")
    assert str(error) == "Parola hatalı ya da dosya bozuk"
    unchanged.check()


def test_tc195_changed_kdf_field(ops: Ops) -> None:
    populate()
    take_backup(ops)
    export_file = take_export(ops)
    blob = bytearray(export_file.read_bytes())
    blob[16] = 2  # p: 1 -> 2, authenticated as part of the header
    export_file.write_bytes(bytes(blob))
    unchanged = Unchanged(ops.db)
    assert str(fails("restore_backup", str(export_file), "--yes")) == (
        "Parola hatalı ya da dosya bozuk"
    )
    unchanged.check()


def test_tc196_unknown_version_and_short_file(ops: Ops, tmp_path: Path) -> None:
    populate()
    take_backup(ops)
    export_file = take_export(ops)
    blob = export_file.read_bytes()
    version_two = tmp_path / "surum2.libx"
    version_two.write_bytes(blob[:4] + b"\x02" + blob[5:])
    short = tmp_path / "kisa.libx"
    short.write_bytes(blob[:30])
    unchanged = Unchanged(ops.db)
    assert str(fails("restore_backup", str(version_two), "--yes")) == "Desteklenmeyen dosya sürümü"
    assert str(fails("restore_backup", str(short), "--yes")) == "Parola hatalı ya da dosya bozuk"
    unchanged.check()


def test_tc197_two_exports_differ(ops: Ops) -> None:
    populate()
    take_backup(ops)
    first = take_export(ops).read_bytes()
    second = take_export(ops).read_bytes()
    assert first[17:33] != second[17:33]
    assert first[33:45] != second[33:45]
    assert first[45:] != second[45:]
    assert libx.decrypt(first, PASSPHRASE) == libx.decrypt(second, PASSPHRASE)


def test_tc198_no_daily_backup(ops: Ops) -> None:
    error = fails("export_backup", "--date", "2026-11-02")
    assert str(error) == f"Günlük yedek bulunamadı: {ops.backups}"
    assert list(ops.exports.iterdir()) == []
    assert JobRun.objects.get(job=Job.EXPORT).status == JobRun.Status.FAILED


def test_tc198_no_passphrase_file(ops: Ops, tmp_path: Path) -> None:
    populate()
    take_backup(ops)
    missing = tmp_path / "olmayan parola.txt"
    error = fails("export_backup", "--date", "2026-11-02", "--passphrase-file", str(missing))
    assert str(error) == f"Parola dosyası bulunamadı: {missing}"
    assert list(ops.exports.iterdir()) == []


def test_tc300_failed_export_keeps_old_exports(ops: Ops, tmp_path: Path) -> None:
    populate()
    take_backup(ops)
    old = ops.exports / "library-export-20260903.libx"  # 60 days before 11-02
    old.write_bytes(b"eski")
    fails("export_backup", "--date", "2026-11-02", "--passphrase-file", str(tmp_path / "yok.txt"))
    assert sorted(p.name for p in ops.exports.iterdir()) == [old.name]


def test_tc300_successful_export_deletes_old_exports(ops: Ops) -> None:
    populate()
    take_backup(ops)
    for name in (
        "library-export-20260906.libx",
        "library-export-20260907.libx",
        "eski.libx",
    ):  # −57, −56
        (ops.exports / name).write_bytes(b"eski")
    output = run("export_backup", "--date", "2026-11-02")
    assert output.splitlines()[-1] == "Silinen eski dışa aktarma: 1"
    assert sorted(p.name for p in ops.exports.iterdir()) == [
        "eski.libx",
        "library-export-20260907.libx",
        "library-export-20261102.libx",
    ]


def test_tc303_export_uses_the_newest_backup(ops: Ops) -> None:
    populate()
    take_backup(ops, "2026-11-01")
    make_member("Yeni Üye")
    take_backup(ops, "2026-11-02")
    export_file = take_export(ops, "2026-11-02")
    close_and_delete(ops.db)
    run("restore_backup", str(export_file), "--yes")
    assert counts(ops.db) == (3, 3, 1)


def test_tc304_passphrase_line_end_and_empty_file(ops: Ops, tmp_path: Path) -> None:
    populate()
    take_backup(ops)
    secret = tmp_path / "gizli.txt"
    secret.write_bytes(b"gizli\n")
    run("export_backup", "--date", "2026-11-02", "--passphrase-file", str(secret))
    blob = (ops.exports / "library-export-20261102.libx").read_bytes()
    assert libx.decrypt(blob, "gizli")

    empty = tmp_path / "bos.txt"
    empty.write_bytes(b"")
    error = fails("export_backup", "--date", "2026-11-03", "--passphrase-file", str(empty))
    assert str(error) == f"Parola dosyası boş: {empty}"
    assert not (ops.exports / "library-export-20261103.libx").exists()


def test_tc323_invalid_dates(ops: Ops) -> None:
    for command, value in (("backup_db", "2026-13-40"), ("export_backup", "2026-02-30")):
        error = fails(command, "--date", value)
        assert str(error) == f"Geçersiz tarih: {value}"
    assert JobRun.objects.count() == 0
    assert list(ops.backups.iterdir()) == [] and list(ops.exports.iterdir()) == []


def test_tc324_export_defaults_to_the_configured_passphrase_file(ops: Ops) -> None:
    populate()
    take_backup(ops)
    run("export_backup", "--date", "2026-11-02")
    blob = (ops.exports / "library-export-20261102.libx").read_bytes()
    assert counts_of_plaintext(libx.decrypt(blob, PASSPHRASE), ops) == INITIAL


def counts_of_plaintext(data: bytes, ops: Ops) -> tuple[int, int, int]:
    path = ops.db.parent / "cozulmus.sqlite3"
    path.write_bytes(data)
    try:
        return counts(path)
    finally:
        path.unlink()


def test_tc325_type_comes_from_the_magic_bytes(ops: Ops, tmp_path: Path) -> None:
    populate()
    backup_file = take_backup(ops)
    export_file = take_export(ops)
    libx_named_sqlite = tmp_path / "yedek.sqlite3"
    libx_named_sqlite.write_bytes(export_file.read_bytes())
    sqlite_named_libx = tmp_path / "yedek.libx"
    sqlite_named_libx.write_bytes(backup_file.read_bytes())
    make_member("Sonradan")
    for candidate in (libx_named_sqlite, sqlite_named_libx):
        output = run("restore_backup", str(candidate), "--yes")
        assert output.splitlines()[0] == "Geri yüklendi: üye=2, nüsha=3, ödünç=1"
        assert counts(ops.db) == INITIAL


def test_tc326_libx_without_any_passphrase_file(ops: Ops) -> None:
    populate()
    take_backup(ops)
    export_file = take_export(ops)
    ops.passphrase_file.unlink()
    unchanged = Unchanged(ops.db)
    error = fails("restore_backup", str(export_file), "--yes")
    assert str(error) == f"Parola dosyası bulunamadı: {ops.passphrase_file}"
    unchanged.check()


def test_tc328_failed_export_write_leaves_no_tmp(ops: Ops, monkeypatch) -> None:
    populate()
    take_backup(ops)
    same_day = ops.exports / "library-export-20261102.libx"
    same_day.write_bytes(b"ayni gunun eski disa aktarmasi")

    def refuse(src, dst):
        raise PermissionError(13, "Erişim engellendi", str(dst))

    monkeypatch.setattr(backup, "_replace", refuse)
    fails("export_backup", "--date", "2026-11-02")
    assert sorted(p.name for p in ops.exports.iterdir()) == [same_day.name]
    assert same_day.read_bytes() == b"ayni gunun eski disa aktarmasi"
    assert JobRun.objects.get(job=Job.EXPORT).status == JobRun.Status.FAILED


def test_tc329_same_day_runs_overwrite(ops: Ops) -> None:
    populate()
    take_backup(ops)
    take_export(ops)
    make_member("Öğleden Sonra")
    backup_file = take_backup(ops)
    export_file = take_export(ops)
    assert sorted(p.name for p in ops.backups.iterdir()) == [backup_file.name]
    assert sorted(p.name for p in ops.exports.iterdir()) == [export_file.name]
    assert counts(backup_file) == (3, 3, 1)
    close_and_delete(ops.db)
    run("restore_backup", str(export_file), "--yes")
    assert counts(ops.db) == (3, 3, 1)


def test_backup_date_defaults_to_today(ops: Ops, monkeypatch) -> None:
    monkeypatch.setattr("administration.clock.today", lambda: date(2026, 11, 5))
    run("backup_db")
    assert (ops.backups / "library-20261105.sqlite3").is_file()
    assert JobRun.objects.get().run_on == date(2026, 11, 5)

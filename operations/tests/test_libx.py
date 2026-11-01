"""``.libx`` format tests (architecture §6.3, ADR-0011): round trip, header,
tampering, unknown versions and uniqueness. Command-level checks of the same
rules are in ``test_commands.py`` (TC-192…TC-197)."""

from __future__ import annotations

import struct

import pytest

from operations import libx

FAST = {"n": 2**10, "r": 8, "p": 1}
HEADER = 4 + 1 + 12 + 16 + 12


def test_round_trip() -> None:
    blob = libx.encrypt(b"veri \x00\xff", "gizli", **FAST)
    assert libx.decrypt(blob, "gizli") == b"veri \x00\xff"
    assert libx.is_libx(blob)
    assert not libx.is_libx(b"SQLite format 3\x00")


def test_header_layout() -> None:
    blob = libx.encrypt(b"x", "gizli", **FAST)
    magic, version, n, r, p = struct.unpack(">4sBIII", blob[:17])
    assert (magic, version, n, r, p) == (b"LIBX", 1, 2**10, 8, 1)
    # salt 16 + nonce 12, then ciphertext with the 16-byte GCM tag.
    assert len(blob) == HEADER + 1 + 16


def test_wrong_passphrase() -> None:
    blob = libx.encrypt(b"x", "gizli", **FAST)
    with pytest.raises(libx.LibxError, match="^Parola hatalı ya da dosya bozuk$"):
        libx.decrypt(blob, "yanlış")


@pytest.mark.parametrize("index", [5 + 12, 30, HEADER - 1, HEADER, -1])
def test_tc195_any_changed_byte_fails(index: int) -> None:
    """Salt (17), nonce, ciphertext and tag bytes are all authenticated."""
    blob = bytearray(libx.encrypt(b"veri", "gizli", **FAST))
    blob[index] ^= 0x01
    with pytest.raises(libx.LibxError, match="^Parola hatalı ya da dosya bozuk$"):
        libx.decrypt(bytes(blob), "gizli")


@pytest.mark.parametrize(
    "fields",
    [
        (2**10 + 1, 8, 1),  # n not a power of two
        (2**10, 0, 1),
        (2**10, 8, 0),
        (2**30, 8, 1),  # would need far too much memory
        (2**10, 1000, 1),
    ],
)
def test_tc195_changed_kdf_fields_fail_without_running_scrypt(fields) -> None:
    blob = bytearray(libx.encrypt(b"veri", "gizli", **FAST))
    blob[5:17] = struct.pack(">III", *fields)
    with pytest.raises(libx.LibxError, match="^Parola hatalı ya da dosya bozuk$"):
        libx.decrypt(bytes(blob), "gizli")


def test_tc196_unknown_version_magic_and_short_file() -> None:
    blob = libx.encrypt(b"veri", "gizli", **FAST)
    with pytest.raises(libx.LibxError, match="^Desteklenmeyen dosya sürümü$"):
        libx.decrypt(blob[:4] + b"\x02" + blob[5:], "gizli")
    with pytest.raises(libx.LibxError, match="^Parola hatalı ya da dosya bozuk$"):
        libx.decrypt(b"LIBY" + blob[4:], "gizli")
    for short in (b"", b"LIB", b"LIBX", blob[:HEADER], blob[: HEADER + 15]):
        with pytest.raises(libx.LibxError, match="^Parola hatalı ya da dosya bozuk$"):
            libx.decrypt(short, "gizli")


def test_tc197_salt_nonce_and_ciphertext_differ() -> None:
    first = libx.encrypt(b"ayni veri", "gizli", **FAST)
    second = libx.encrypt(b"ayni veri", "gizli", **FAST)
    assert first[17:33] != second[17:33]  # salt
    assert first[33:45] != second[33:45]  # nonce
    assert first[45:] != second[45:]


def test_default_parameters_are_phase_4_values() -> None:
    """Phase 4 small decision 6: n = 2^17, r = 8, p = 1 (checked without
    running the slow derivation)."""
    assert libx.encrypt.__defaults__ == (2**17, 8, 1)

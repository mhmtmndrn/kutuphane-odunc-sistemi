"""Encrypted export file format ``.libx`` (architecture §6.3, ADR-0011).

Layout: magic ``LIBX`` (4), version ``0x01`` (1), scrypt n, r, p (3 × 4,
big endian), salt (16), nonce (12), then AES-256-GCM ciphertext and tag. The
whole header is authenticated as associated data, so a changed KDF field or
salt fails like a wrong passphrase.
"""

from __future__ import annotations

import os
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC = b"LIBX"
VERSION = 1
_FIELDS = struct.Struct(">4sBIII")
HEADER_SIZE = _FIELDS.size + 16 + 12
_TAG_SIZE = 16
# Bounds for header values read from a file: a tampered header must fail
# fast instead of asking scrypt for gigabytes of memory.
_MAX_N = 2**20
_MAX_R = 32
_MAX_P = 16
_MAX_MEMORY = 1024 * 1024 * 1024

BAD_FILE = "Parola hatalı ya da dosya bozuk"
UNSUPPORTED = "Desteklenmeyen dosya sürümü"


class LibxError(Exception):
    """A ``.libx`` file that cannot be opened; the message is user-facing."""


def is_libx(data: bytes) -> bool:
    """The file type comes from the magic bytes, not the extension (G14–G16
    small decision 2)."""
    return data[:4] == MAGIC


def _key(passphrase: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return Scrypt(salt=salt, length=32, n=n, r=r, p=p).derive(passphrase.encode("utf-8"))


def encrypt(plaintext: bytes, passphrase: str, n: int = 2**17, r: int = 8, p: int = 1) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    header = _FIELDS.pack(MAGIC, VERSION, n, r, p) + salt + nonce
    return header + AESGCM(_key(passphrase, salt, n, r, p)).encrypt(nonce, plaintext, header)


def _sane(n: int, r: int, p: int) -> bool:
    return (
        2 <= n <= _MAX_N
        and n & (n - 1) == 0
        and 1 <= r <= _MAX_R
        and 1 <= p <= _MAX_P
        and 128 * r * n <= _MAX_MEMORY
    )


def decrypt(blob: bytes, passphrase: str) -> bytes:
    if len(blob) < 5 or blob[:4] != MAGIC:
        raise LibxError(BAD_FILE)
    if blob[4] != VERSION:
        raise LibxError(UNSUPPORTED)
    if len(blob) < HEADER_SIZE + _TAG_SIZE:
        raise LibxError(BAD_FILE)
    _, _, n, r, p = _FIELDS.unpack(blob[: _FIELDS.size])
    if not _sane(n, r, p):
        raise LibxError(BAD_FILE)
    header = blob[:HEADER_SIZE]
    salt = header[_FIELDS.size : _FIELDS.size + 16]
    nonce = header[_FIELDS.size + 16 :]
    try:
        return AESGCM(_key(passphrase, salt, n, r, p)).decrypt(nonce, blob[HEADER_SIZE:], header)
    except InvalidTag:
        raise LibxError(BAD_FILE) from None

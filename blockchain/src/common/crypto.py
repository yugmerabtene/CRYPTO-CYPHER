from __future__ import annotations

import base64
import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def hash_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hash_hex(data: bytes) -> str:
    return hash_bytes(data).hex()


def generate_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def sign(private_key: Ed25519PrivateKey, message_bytes: bytes) -> bytes:
    return private_key.sign(message_bytes)


def verify(
    public_key: Ed25519PublicKey | bytes,
    message_bytes: bytes,
    signature_bytes: bytes,
) -> bool:
    key = public_key
    if isinstance(public_key, bytes):
        key = Ed25519PublicKey.from_public_bytes(public_key)

    try:
        key.verify(signature_bytes, message_bytes)
        return True
    except InvalidSignature:
        return False


def private_key_to_bytes(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_to_bytes(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def load_private_key(private_key_bytes: bytes) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(private_key_bytes)


def load_public_key(public_key_bytes: bytes) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(public_key_bytes)


def pubkey_to_address(pubkey_bytes: bytes) -> str:
    """Address format for PoC: cc1 + base32(sha256(pubkey)[:20])."""
    digest = hash_bytes(pubkey_bytes)[:20]
    encoded = base64.b32encode(digest).decode("ascii").rstrip("=").lower()
    return f"cc1{encoded}"

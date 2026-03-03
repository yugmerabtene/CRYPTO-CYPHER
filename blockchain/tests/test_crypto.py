from src.common.crypto import (
    generate_keypair,
    hash_bytes,
    hash_hex,
    pubkey_to_address,
    public_key_to_bytes,
    sign,
    verify,
)


def test_hash_helpers_are_deterministic() -> None:
    data = b"cryptocypher"
    assert hash_bytes(data) == hash_bytes(data)
    assert len(hash_bytes(data)) == 32
    assert len(hash_hex(data)) == 64


def test_ed25519_sign_and_verify() -> None:
    private_key, public_key = generate_keypair()
    message = b"hello-chain"

    signature = sign(private_key, message)
    assert verify(public_key, message, signature)
    assert not verify(public_key, b"tampered", signature)


def test_pubkey_to_address_format() -> None:
    _, public_key = generate_keypair()
    public_key_bytes = public_key_to_bytes(public_key)

    address = pubkey_to_address(public_key_bytes)
    assert address.startswith("cc1")
    assert len(address) > 10

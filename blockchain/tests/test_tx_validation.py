import pytest

from src.common.crypto import generate_keypair, pubkey_to_address, public_key_to_bytes, sign
from src.common.errors import ValidationError
from src.common.types import Transaction, TransactionType
from src.node.storage_state import WorldState
from src.node.validation import validate_tx


def build_payment_tx(
    sender_priv,
    sender_pub_bytes: bytes,
    receiver_address: str,
    nonce: int,
    amount: int,
) -> Transaction:
    tx = Transaction(
        tx_type=TransactionType.PAYMENT,
        from_address=pubkey_to_address(sender_pub_bytes),
        to_address=receiver_address,
        amount=amount,
        nonce=nonce,
        payload={},
        pubkey=sender_pub_bytes.hex(),
        timestamp=1_700_000_000,
    )
    tx.signature = sign(sender_priv, tx.canonical_bytes()).hex()
    tx.tx_id = tx.compute_tx_id()
    return tx


def test_validate_tx_accepts_valid_payment() -> None:
    sender_priv, sender_pub = generate_keypair()
    sender_pub_bytes = public_key_to_bytes(sender_pub)

    _, receiver_pub = generate_keypair()
    receiver_address = pubkey_to_address(public_key_to_bytes(receiver_pub))

    state = WorldState()
    sender_address = pubkey_to_address(sender_pub_bytes)
    state.set_balance(sender_address, 100)
    state.set_nonce(sender_address, 0)

    tx = build_payment_tx(sender_priv, sender_pub_bytes, receiver_address, nonce=0, amount=25)
    validate_tx(tx, state)


def test_validate_tx_rejects_bad_nonce() -> None:
    sender_priv, sender_pub = generate_keypair()
    sender_pub_bytes = public_key_to_bytes(sender_pub)

    _, receiver_pub = generate_keypair()
    receiver_address = pubkey_to_address(public_key_to_bytes(receiver_pub))

    state = WorldState()
    sender_address = pubkey_to_address(sender_pub_bytes)
    state.set_balance(sender_address, 100)
    state.set_nonce(sender_address, 0)

    tx = build_payment_tx(sender_priv, sender_pub_bytes, receiver_address, nonce=1, amount=25)
    with pytest.raises(ValidationError, match="Invalid nonce"):
        validate_tx(tx, state)


def test_validate_tx_rejects_insufficient_balance() -> None:
    sender_priv, sender_pub = generate_keypair()
    sender_pub_bytes = public_key_to_bytes(sender_pub)

    _, receiver_pub = generate_keypair()
    receiver_address = pubkey_to_address(public_key_to_bytes(receiver_pub))

    state = WorldState()
    sender_address = pubkey_to_address(sender_pub_bytes)
    state.set_balance(sender_address, 10)
    state.set_nonce(sender_address, 0)

    tx = build_payment_tx(sender_priv, sender_pub_bytes, receiver_address, nonce=0, amount=25)
    with pytest.raises(ValidationError, match="Insufficient balance"):
        validate_tx(tx, state)


def test_validate_tx_rejects_invalid_signature() -> None:
    sender_priv, sender_pub = generate_keypair()
    sender_pub_bytes = public_key_to_bytes(sender_pub)

    _, receiver_pub = generate_keypair()
    receiver_address = pubkey_to_address(public_key_to_bytes(receiver_pub))

    state = WorldState()
    sender_address = pubkey_to_address(sender_pub_bytes)
    state.set_balance(sender_address, 100)
    state.set_nonce(sender_address, 0)

    tx = build_payment_tx(sender_priv, sender_pub_bytes, receiver_address, nonce=0, amount=25)
    tx.amount = 26
    tx.tx_id = tx.compute_tx_id()

    with pytest.raises(ValidationError, match="Invalid signature"):
        validate_tx(tx, state)


def test_validate_tx_rejects_tx_id_mismatch() -> None:
    sender_priv, sender_pub = generate_keypair()
    sender_pub_bytes = public_key_to_bytes(sender_pub)

    _, receiver_pub = generate_keypair()
    receiver_address = pubkey_to_address(public_key_to_bytes(receiver_pub))

    state = WorldState()
    sender_address = pubkey_to_address(sender_pub_bytes)
    state.set_balance(sender_address, 100)
    state.set_nonce(sender_address, 0)

    tx = build_payment_tx(sender_priv, sender_pub_bytes, receiver_address, nonce=0, amount=25)
    tx.tx_id = "0" * 64

    with pytest.raises(ValidationError, match="tx_id mismatch"):
        validate_tx(tx, state)


def test_validate_tx_accepts_coinbase() -> None:
    state = WorldState()
    tx = Transaction(
        tx_type=TransactionType.COINBASE,
        from_address="COINBASE",
        to_address="cc1mineraddress",
        amount=50,
        nonce=0,
        payload={},
        pubkey="",
        timestamp=1_700_000_000,
        signature=None,
    )
    tx.tx_id = tx.compute_tx_id()
    validate_tx(tx, state)


def test_validate_tx_rejects_coinbase_with_signature() -> None:
    state = WorldState()
    tx = Transaction(
        tx_type=TransactionType.COINBASE,
        from_address="COINBASE",
        to_address="cc1mineraddress",
        amount=50,
        nonce=0,
        payload={},
        pubkey="",
        timestamp=1_700_000_000,
        signature="deadbeef",
    )
    tx.tx_id = tx.compute_tx_id()
    with pytest.raises(ValidationError, match="must not include a signature"):
        validate_tx(tx, state)

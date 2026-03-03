from src.common.crypto import generate_keypair, pubkey_to_address, public_key_to_bytes, sign
from src.common.types import Transaction, TransactionType
from src.node.storage_state import WorldState


def test_apply_payment_updates_balances_and_nonce() -> None:
    sender_priv, sender_pub = generate_keypair()
    sender_pub_bytes = public_key_to_bytes(sender_pub)
    sender = pubkey_to_address(sender_pub_bytes)

    _, receiver_pub = generate_keypair()
    receiver = pubkey_to_address(public_key_to_bytes(receiver_pub))

    state = WorldState()
    state.set_balance(sender, 50)
    state.set_nonce(sender, 0)

    tx = Transaction(
        tx_type=TransactionType.PAYMENT,
        from_address=sender,
        to_address=receiver,
        amount=20,
        nonce=0,
        payload={},
        pubkey=sender_pub_bytes.hex(),
        timestamp=1_700_000_000,
    )
    tx.signature = sign(sender_priv, tx.canonical_bytes()).hex()

    state.apply_transaction(tx)

    assert state.get_balance(sender) == 30
    assert state.get_balance(receiver) == 20
    assert state.get_nonce(sender) == 1


def test_apply_coinbase_credits_miner_without_nonce_increment() -> None:
    state = WorldState()
    miner_address = "cc1miner000000000000000000000000000000"
    state.set_nonce(miner_address, 7)

    coinbase = Transaction(
        tx_type=TransactionType.COINBASE,
        from_address="COINBASE",
        to_address=miner_address,
        amount=50,
        nonce=0,
        payload={},
        pubkey="",
        timestamp=1_700_000_000,
        signature=None,
    )
    coinbase.tx_id = coinbase.compute_tx_id()

    state.apply_transaction(coinbase)

    assert state.get_balance(miner_address) == 50
    assert state.get_nonce(miner_address) == 7

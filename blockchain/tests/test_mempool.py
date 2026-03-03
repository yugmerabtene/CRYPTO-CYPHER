from src.common.crypto import generate_keypair, pubkey_to_address, public_key_to_bytes, sign
from src.common.types import Transaction, TransactionType
from src.node.mempool import Mempool


def _build_tx(nonce: int) -> Transaction:
    private_key, public_key = generate_keypair()
    pubkey_bytes = public_key_to_bytes(public_key)
    address = pubkey_to_address(pubkey_bytes)

    tx = Transaction(
        tx_type=TransactionType.PAYMENT,
        from_address=address,
        to_address=address,
        amount=1,
        nonce=nonce,
        payload={},
        pubkey=pubkey_bytes.hex(),
        timestamp=1_700_000_000 + nonce,
    )
    tx.signature = sign(private_key, tx.canonical_bytes()).hex()
    tx.tx_id = tx.compute_tx_id()
    return tx


def test_mempool_add_dedup_and_remove() -> None:
    pool = Mempool()
    tx = _build_tx(nonce=0)

    assert pool.add(tx) is True
    assert pool.add(tx) is False
    assert len(pool) == 1

    pool.remove([tx.tx_id or ""])
    assert len(pool) == 0


def test_mempool_get_batch_limit() -> None:
    pool = Mempool()
    tx0 = _build_tx(nonce=0)
    tx1 = _build_tx(nonce=1)
    tx2 = _build_tx(nonce=2)

    pool.add(tx0)
    pool.add(tx1)
    pool.add(tx2)

    batch = pool.get_batch(limit=2)
    assert len(batch) == 2

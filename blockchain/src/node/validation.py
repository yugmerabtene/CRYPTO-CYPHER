from __future__ import annotations

from src.common.config import BLOCK_REWARD
from src.common.crypto import pubkey_to_address, verify
from src.common.errors import ValidationError
from src.common.types import Block, Transaction, TransactionType
from src.node.consensus_pow import verify_pow
from src.node.storage_chain import ChainStorage
from src.node.storage_state import WorldState


def validate_tx(tx: Transaction, state: WorldState) -> None:
    expected_tx_id = tx.compute_tx_id()
    if tx.tx_id and tx.tx_id != expected_tx_id:
        raise ValidationError("tx_id mismatch with canonical serialization")

    if tx.tx_type == TransactionType.COINBASE:
        if tx.from_address != "COINBASE":
            raise ValidationError("COINBASE must use from_address=COINBASE")
        if tx.nonce != 0:
            raise ValidationError("COINBASE nonce must be 0")
        if tx.amount <= 0:
            raise ValidationError("COINBASE amount must be strictly positive")
        if not tx.to_address:
            raise ValidationError("COINBASE transaction requires to_address")
        if tx.pubkey:
            raise ValidationError("COINBASE must not include a pubkey")
        if tx.signature:
            raise ValidationError("COINBASE must not include a signature")
        return

    if not tx.signature:
        raise ValidationError("Missing transaction signature")

    try:
        pubkey_bytes = bytes.fromhex(tx.pubkey)
        signature_bytes = bytes.fromhex(tx.signature)
    except ValueError as exc:
        raise ValidationError("pubkey/signature must be hex encoded") from exc

    if pubkey_to_address(pubkey_bytes) != tx.from_address:
        raise ValidationError("from_address does not match pubkey")

    if not verify(pubkey_bytes, tx.canonical_bytes(), signature_bytes):
        raise ValidationError("Invalid signature")

    expected_nonce = state.get_nonce(tx.from_address)
    if tx.nonce != expected_nonce:
        raise ValidationError(f"Invalid nonce: expected {expected_nonce}, got {tx.nonce}")

    if tx.tx_type == TransactionType.PAYMENT:
        if not tx.to_address:
            raise ValidationError("PAYMENT transaction requires to_address")
        if tx.amount <= 0:
            raise ValidationError("PAYMENT amount must be strictly positive")
        if state.get_balance(tx.from_address) < tx.amount:
            raise ValidationError("Insufficient balance")


def validate_block(
    block: Block,
    chain: ChainStorage,
    state_snapshot: WorldState,
    block_reward: int = BLOCK_REWARD,
) -> WorldState:
    expected_height = chain.height() + 1
    if block.height != expected_height:
        raise ValidationError(f"Invalid block height: expected {expected_height}, got {block.height}")

    if not verify_pow(block.header):
        raise ValidationError("Invalid proof of work")

    if block.header.prev_hash != chain.head_hash():
        raise ValidationError("Invalid prev_hash")

    expected_merkle_root = Block.compute_merkle_root([tx.compute_tx_id() for tx in block.transactions])
    if block.header.merkle_root != expected_merkle_root:
        raise ValidationError("Invalid merkle_root")

    coinbase_txs = [tx for tx in block.transactions if tx.tx_type == TransactionType.COINBASE]
    if len(coinbase_txs) > 1:
        raise ValidationError("Block cannot contain more than one COINBASE transaction")
    if coinbase_txs:
        if block.transactions[0].tx_type != TransactionType.COINBASE:
            raise ValidationError("COINBASE transaction must be first in block")
        if coinbase_txs[0].amount != block_reward:
            raise ValidationError("Invalid COINBASE reward amount")

    candidate_state = state_snapshot.clone()
    for tx in block.transactions:
        validate_tx(tx, candidate_state)
        candidate_state.apply_transaction(tx)

    return candidate_state

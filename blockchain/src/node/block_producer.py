from __future__ import annotations

from src.common.types import Block, BlockHeader, Transaction, TransactionType
from src.common.utils import utc_timestamp
from src.node.mempool import Mempool
from src.node.storage_chain import ChainStorage


def build_coinbase_tx(miner_address: str, reward: int) -> Transaction:
    tx = Transaction(
        tx_type=TransactionType.COINBASE,
        from_address="COINBASE",
        to_address=miner_address,
        amount=reward,
        nonce=0,
        payload={},
        pubkey="",
        timestamp=utc_timestamp(),
        signature=None,
    )
    tx.ensure_tx_id()
    return tx


def build_candidate_block(
    chain: ChainStorage,
    mempool: Mempool,
    limit: int = 100,
    difficulty: int = 1,
    miner_address: str | None = None,
    block_reward: int = 50,
) -> Block:
    txs = mempool.get_batch(limit)
    if miner_address:
        txs = [build_coinbase_tx(miner_address, block_reward)] + txs

    tx_ids = [tx.ensure_tx_id() for tx in txs]

    header = BlockHeader(
        prev_hash=chain.head_hash(),
        merkle_root=Block.compute_merkle_root(tx_ids),
        difficulty=difficulty,
    )
    return Block(
        height=chain.height() + 1,
        header=header,
        transactions=txs,
    )

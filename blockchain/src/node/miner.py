from __future__ import annotations

from dataclasses import dataclass

from src.common.config import BLOCK_REWARD, DEFAULT_DIFFICULTY
from src.common.types import Block, TransactionType
from src.node.block_producer import build_candidate_block
from src.node.consensus_pow import mine
from src.node.mempool import Mempool
from src.node.storage_chain import ChainStorage
from src.node.storage_state import WorldState
from src.node.validation import validate_block


@dataclass
class MiningResult:
    block: Block
    included_tx_ids: list[str]


def mine_pending_transactions(
    chain: ChainStorage,
    state: WorldState,
    mempool: Mempool,
    miner_address: str,
    difficulty: int = DEFAULT_DIFFICULTY,
    block_reward: int = BLOCK_REWARD,
    tx_limit: int = 100,
    max_nonce: int = 5_000_000,
) -> MiningResult:
    candidate_block = build_candidate_block(
        chain=chain,
        mempool=mempool,
        limit=tx_limit,
        difficulty=difficulty,
        miner_address=miner_address,
        block_reward=block_reward,
    )

    mine(candidate_block.header, max_nonce=max_nonce)
    next_state = validate_block(candidate_block, chain, state, block_reward=block_reward)
    chain.add_block(candidate_block)

    # Commit in-memory state atomically from validated snapshot.
    state.balances = next_state.balances
    state.nonces = next_state.nonces

    included_tx_ids = [
        tx.ensure_tx_id()
        for tx in candidate_block.transactions
        if tx.tx_type != TransactionType.COINBASE
    ]
    mempool.remove(included_tx_ids)
    return MiningResult(block=candidate_block, included_tx_ids=included_tx_ids)

import pytest

from src.common.errors import ValidationError
from src.node.block_producer import build_candidate_block
from src.node.consensus_pow import mine
from src.node.mempool import Mempool
from src.node.storage_chain import ChainStorage
from src.node.storage_state import WorldState
from src.node.validation import validate_block


def test_chain_has_genesis_block() -> None:
    chain = ChainStorage()
    assert chain.height() == 0
    assert chain.head().height == 0


def test_validate_block_rejects_invalid_pow() -> None:
    chain = ChainStorage()
    state = WorldState()
    mempool = Mempool()

    block = build_candidate_block(chain, mempool, difficulty=8)
    with pytest.raises(ValidationError, match="Invalid proof of work"):
        validate_block(block, chain, state)


def test_validate_block_rejects_wrong_coinbase_reward() -> None:
    chain = ChainStorage()
    state = WorldState()
    mempool = Mempool()

    block = build_candidate_block(
        chain=chain,
        mempool=mempool,
        difficulty=1,
        miner_address="cc1miner",
        block_reward=10,
    )
    mine(block.header, max_nonce=500_000)

    with pytest.raises(ValidationError, match="Invalid COINBASE reward amount"):
        validate_block(block, chain, state, block_reward=50)

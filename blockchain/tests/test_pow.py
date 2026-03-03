from src.common.types import BlockHeader
from src.node.consensus_pow import mine, target_from_difficulty, verify_pow


def test_target_from_difficulty() -> None:
    assert target_from_difficulty(1) == "0"
    assert target_from_difficulty(4) == "0000"


def test_mine_and_verify_pow() -> None:
    header = BlockHeader(
        prev_hash="a" * 64,
        merkle_root="b" * 64,
        difficulty=2,
        nonce=0,
        timestamp=1_700_000_000,
    )

    nonce = mine(header, max_nonce=500_000)
    assert nonce >= 0
    assert verify_pow(header) is True

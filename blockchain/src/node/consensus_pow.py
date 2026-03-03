from __future__ import annotations

from src.common.types import BlockHeader


def target_from_difficulty(difficulty: int) -> str:
    return "0" * difficulty


def mine(header: BlockHeader, max_nonce: int = 5_000_000) -> int:
    target_prefix = target_from_difficulty(header.difficulty)
    for nonce in range(max_nonce):
        header.nonce = nonce
        if header.header_hash().startswith(target_prefix):
            return nonce
    raise RuntimeError("Unable to mine a block with max_nonce limit")


def verify_pow(header: BlockHeader) -> bool:
    return header.header_hash().startswith(target_from_difficulty(header.difficulty))

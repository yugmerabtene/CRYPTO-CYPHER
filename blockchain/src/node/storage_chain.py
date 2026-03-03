from __future__ import annotations

from src.common.crypto import hash_hex
from src.common.types import Block, BlockHeader


class ChainStorage:
    def __init__(self) -> None:
        self._blocks: list[Block] = []
        self.ensure_genesis()

    def ensure_genesis(self) -> None:
        if self._blocks:
            return
        genesis_header = BlockHeader(
            prev_hash="0" * 64,
            merkle_root=hash_hex(b"genesis"),
            difficulty=1,
            nonce=0,
        )
        self._blocks.append(
            Block(
                height=0,
                header=genesis_header,
                transactions=[],
            )
        )

    def add_block(self, block: Block) -> None:
        self._blocks.append(block)

    def height(self) -> int:
        return self._blocks[-1].height

    def head(self) -> Block:
        return self._blocks[-1]

    def head_hash(self) -> str:
        return self.head().block_hash()

    def get_block(self, height: int) -> Block | None:
        for block in self._blocks:
            if block.height == height:
                return block
        return None

    def all_blocks(self) -> list[Block]:
        return list(self._blocks)

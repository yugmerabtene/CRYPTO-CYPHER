from __future__ import annotations

from src.common.types import Transaction


class Mempool:
    def __init__(self) -> None:
        self._pool: dict[str, Transaction] = {}

    def add(self, tx: Transaction) -> bool:
        tx_id = tx.ensure_tx_id()
        if tx_id in self._pool:
            return False
        self._pool[tx_id] = tx
        return True

    def get_batch(self, limit: int) -> list[Transaction]:
        return list(self._pool.values())[:limit]

    def remove(self, tx_ids: list[str]) -> None:
        for tx_id in tx_ids:
            self._pool.pop(tx_id, None)

    def __len__(self) -> int:
        return len(self._pool)

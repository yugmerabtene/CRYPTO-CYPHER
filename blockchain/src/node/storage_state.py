from __future__ import annotations

import json
from pathlib import Path

from src.common.errors import StorageError, ValidationError
from src.common.types import Transaction, TransactionType


class WorldState:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.balances: dict[str, int] = {}
        self.nonces: dict[str, int] = {}
        if self.path and self.path.exists():
            self.load()

    def clone(self) -> "WorldState":
        clone_state = WorldState()
        clone_state.balances = dict(self.balances)
        clone_state.nonces = dict(self.nonces)
        return clone_state

    def get_balance(self, address: str) -> int:
        return self.balances.get(address, 0)

    def set_balance(self, address: str, amount: int) -> None:
        self.balances[address] = amount

    def get_nonce(self, address: str) -> int:
        return self.nonces.get(address, 0)

    def set_nonce(self, address: str, nonce: int) -> None:
        self.nonces[address] = nonce

    def increment_nonce(self, address: str) -> None:
        self.nonces[address] = self.get_nonce(address) + 1

    def debit(self, address: str, amount: int) -> None:
        if self.get_balance(address) < amount:
            raise ValidationError("Insufficient balance")
        self.balances[address] = self.get_balance(address) - amount

    def credit(self, address: str, amount: int) -> None:
        self.balances[address] = self.get_balance(address) + amount

    def apply_transaction(self, tx: Transaction) -> None:
        if tx.tx_type == TransactionType.COINBASE:
            if tx.to_address is None:
                raise ValidationError("COINBASE requires to_address")
            self.credit(tx.to_address, tx.amount)
            return

        if tx.tx_type == TransactionType.PAYMENT:
            if tx.to_address is None:
                raise ValidationError("PAYMENT requires to_address")
            self.debit(tx.from_address, tx.amount)
            self.credit(tx.to_address, tx.amount)

        self.increment_nonce(tx.from_address)

    def to_dict(self) -> dict[str, dict[str, int]]:
        return {
            "balances": self.balances,
            "nonces": self.nonces,
        }

    def save(self) -> None:
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Failed to save world state to {self.path}") from exc

    def load(self) -> None:
        if not self.path:
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            self.balances = {k: int(v) for k, v in payload.get("balances", {}).items()}
            self.nonces = {k: int(v) for k, v in payload.get("nonces", {}).items()}
        except OSError as exc:
            raise StorageError(f"Failed to load world state from {self.path}") from exc

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.common.crypto import hash_hex
from src.common.utils import canonical_json_dumps, utc_timestamp


class TransactionType(str, Enum):
    COINBASE = "COINBASE"
    PAYMENT = "PAYMENT"
    DEPLOY_CONTRACT = "DEPLOY_CONTRACT"
    CALL_CONTRACT = "CALL_CONTRACT"


class Transaction(BaseModel):
    tx_type: TransactionType
    from_address: str
    to_address: str | None = None
    amount: int = Field(default=0, ge=0)
    nonce: int = Field(default=0, ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)
    pubkey: str
    timestamp: int = Field(default_factory=utc_timestamp)
    signature: str | None = None
    tx_id: str | None = None

    def canonical_dict(self) -> dict[str, Any]:
        """Canonical transaction content used for tx_id and signature."""
        return {
            "amount": self.amount,
            "from_address": self.from_address,
            "nonce": self.nonce,
            "payload": self.payload,
            "pubkey": self.pubkey,
            "timestamp": self.timestamp,
            "to_address": self.to_address,
            "tx_type": self.tx_type.value,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json_dumps(self.canonical_dict()).encode("utf-8")

    def compute_tx_id(self) -> str:
        return hash_hex(self.canonical_bytes())

    def ensure_tx_id(self) -> str:
        tx_id = self.compute_tx_id()
        self.tx_id = tx_id
        return tx_id


class BlockHeader(BaseModel):
    version: int = 1
    prev_hash: str
    merkle_root: str
    timestamp: int = Field(default_factory=utc_timestamp)
    nonce: int = 0
    difficulty: int = Field(default=1, ge=1)

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "difficulty": self.difficulty,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "version": self.version,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json_dumps(self.canonical_dict()).encode("utf-8")

    def header_hash(self) -> str:
        return hash_hex(self.canonical_bytes())


class Block(BaseModel):
    height: int = Field(ge=0)
    header: BlockHeader
    transactions: list[Transaction] = Field(default_factory=list)

    @staticmethod
    def compute_merkle_root(tx_ids: list[str]) -> str:
        if not tx_ids:
            return hash_hex(b"")
        return hash_hex("".join(tx_ids).encode("utf-8"))

    def refresh_merkle_root(self) -> str:
        tx_ids = [tx.ensure_tx_id() for tx in self.transactions]
        root = self.compute_merkle_root(tx_ids)
        self.header.merkle_root = root
        return root

    def block_hash(self) -> str:
        return self.header.header_hash()

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.common.crypto import (
    generate_keypair,
    load_private_key,
    private_key_to_bytes,
    pubkey_to_address,
    public_key_to_bytes,
    sign,
)
from src.common.types import Transaction


@dataclass
class Wallet:
    address: str
    private_key_hex: str
    public_key_hex: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> "Wallet":
        return cls(
            address=payload["address"],
            private_key_hex=payload["private_key_hex"],
            public_key_hex=payload["public_key_hex"],
        )


def create_wallet() -> Wallet:
    private_key, public_key = generate_keypair()
    public_key_bytes = public_key_to_bytes(public_key)
    return Wallet(
        address=pubkey_to_address(public_key_bytes),
        private_key_hex=private_key_to_bytes(private_key).hex(),
        public_key_hex=public_key_bytes.hex(),
    )


def sign_transaction(wallet: Wallet, tx: Transaction) -> Transaction:
    private_key = load_private_key(bytes.fromhex(wallet.private_key_hex))
    tx.signature = sign(private_key, tx.canonical_bytes()).hex()
    tx.tx_id = tx.compute_tx_id()
    return tx

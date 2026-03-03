from __future__ import annotations

import json
from pathlib import Path

from src.client.wallet import Wallet


def save_wallet(wallet: Wallet, out_path: str | Path) -> None:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(wallet.to_dict(), indent=2), encoding="utf-8")


def load_wallet(path: str | Path) -> Wallet:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return Wallet.from_dict(payload)

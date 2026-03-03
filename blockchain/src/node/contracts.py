from __future__ import annotations


class SmartContractEngine:
    """Minimal placeholder engine for future smart-contract support."""

    def __init__(self) -> None:
        self._contracts: dict[str, dict] = {}

    def deploy(self, contract_id: str, payload: dict) -> None:
        self._contracts[contract_id] = payload

    def call(self, contract_id: str, method: str, args: dict | None = None) -> dict:
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError("Unknown contract")
        return {"contract_id": contract_id, "method": method, "args": args or {}}

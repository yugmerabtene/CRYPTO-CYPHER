from fastapi.testclient import TestClient

from src.client.wallet import create_wallet, sign_transaction
from src.common.config import BLOCK_REWARD
from src.common.types import Transaction, TransactionType
from src.node import api as node_api
from src.node.mempool import Mempool
from src.node.storage_chain import ChainStorage
from src.node.storage_state import WorldState


def _reset_node_globals() -> None:
    node_api.state = WorldState()
    node_api.chain = ChainStorage()
    node_api.mempool = Mempool()


def test_api_submit_tx_then_mine_block() -> None:
    _reset_node_globals()
    client = TestClient(node_api.app)

    sender = create_wallet()
    receiver = create_wallet()
    miner = create_wallet()

    node_api.state.set_balance(sender.address, 100)
    node_api.state.set_nonce(sender.address, 0)

    tx = Transaction(
        tx_type=TransactionType.PAYMENT,
        from_address=sender.address,
        to_address=receiver.address,
        amount=15,
        nonce=0,
        payload={},
        pubkey=sender.public_key_hex,
        timestamp=1_700_000_000,
    )
    sign_transaction(sender, tx)

    tx_resp = client.post("/tx", json=tx.model_dump(mode="json"))
    assert tx_resp.status_code == 200
    assert tx_resp.json()["accepted"] is True

    mine_resp = client.post(
        "/mine",
        json={
            "miner_address": miner.address,
            "difficulty": 1,
            "tx_limit": 100,
            "block_reward": BLOCK_REWARD,
        },
    )
    assert mine_resp.status_code == 200
    body = mine_resp.json()
    assert body["height"] == 1
    assert body["tx_count"] == 2
    assert len(body["included_tx_ids"]) == 1

    height_resp = client.get("/chain/height")
    assert height_resp.status_code == 200
    assert height_resp.json()["height"] == 1

    assert node_api.state.get_balance(sender.address) == 85
    assert node_api.state.get_balance(receiver.address) == 15
    assert node_api.state.get_balance(miner.address) == BLOCK_REWARD


def test_api_rejects_coinbase_submission_from_client() -> None:
    _reset_node_globals()
    client = TestClient(node_api.app)

    coinbase = Transaction(
        tx_type=TransactionType.COINBASE,
        from_address="COINBASE",
        to_address="cc1mineraddress",
        amount=BLOCK_REWARD,
        nonce=0,
        payload={},
        pubkey="",
        timestamp=1_700_000_000,
        signature=None,
    )

    resp = client.post("/tx", json=coinbase.model_dump(mode="json"))
    assert resp.status_code == 400
    assert "COINBASE is reserved" in resp.json()["detail"]

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.common.config import BLOCK_REWARD, DEFAULT_DIFFICULTY
from src.common.errors import ValidationError
from src.common.types import Transaction, TransactionType
from src.node.miner import mine_pending_transactions
from src.node.mempool import Mempool
from src.node.storage_chain import ChainStorage
from src.node.storage_state import WorldState
from src.node.validation import validate_tx

app = FastAPI(title="CryptoCypher Node API", version="0.1.0")

state = WorldState()
chain = ChainStorage()
mempool = Mempool()


class MineRequest(BaseModel):
    miner_address: str
    difficulty: int = Field(default=DEFAULT_DIFFICULTY, ge=1)
    block_reward: int = Field(default=BLOCK_REWARD, ge=1)
    tx_limit: int = Field(default=100, ge=1)


@app.post("/tx")
def submit_transaction(tx: Transaction) -> dict[str, str | bool]:
    if tx.tx_type == TransactionType.COINBASE:
        raise HTTPException(status_code=400, detail="COINBASE is reserved for block mining")

    try:
        validate_tx(tx, state)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tx.ensure_tx_id()
    accepted = mempool.add(tx)
    return {
        "tx_id": tx.tx_id or "",
        "accepted": accepted,
    }


@app.get("/chain/head")
def get_chain_head() -> dict[str, str | int]:
    head = chain.head()
    return {
        "height": head.height,
        "hash": head.block_hash(),
        "prev_hash": head.header.prev_hash,
        "tx_count": len(head.transactions),
    }


@app.get("/chain/height")
def get_chain_height() -> dict[str, int]:
    return {"height": chain.height()}


@app.get("/chain/block/{height}")
def get_chain_block(height: int) -> dict:
    block = chain.get_block(height)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return block.model_dump()


@app.post("/mine")
def mine_block(req: MineRequest) -> dict:
    try:
        result = mine_pending_transactions(
            chain=chain,
            state=state,
            mempool=mempool,
            miner_address=req.miner_address,
            difficulty=req.difficulty,
            block_reward=req.block_reward,
            tx_limit=req.tx_limit,
        )
    except (ValidationError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "height": result.block.height,
        "hash": result.block.block_hash(),
        "nonce": result.block.header.nonce,
        "difficulty": result.block.header.difficulty,
        "included_tx_ids": result.included_tx_ids,
        "tx_count": len(result.block.transactions),
    }

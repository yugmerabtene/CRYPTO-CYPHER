from src.client.wallet import create_wallet, sign_transaction
from src.common.config import BLOCK_REWARD
from src.common.types import Transaction, TransactionType
from src.node.miner import mine_pending_transactions
from src.node.mempool import Mempool
from src.node.storage_chain import ChainStorage
from src.node.storage_state import WorldState
from src.node.validation import validate_tx


def test_two_wallets_transfer_and_mine_block() -> None:
    wallet_a = create_wallet()
    wallet_b = create_wallet()
    miner_wallet = create_wallet()

    assert wallet_a.address.startswith("cc1")
    assert wallet_b.address.startswith("cc1")
    assert wallet_a.address != wallet_b.address

    state = WorldState()
    chain = ChainStorage()
    mempool = Mempool()

    # Bootstrap balance for wallet A (faucet/genesis style for PoC tests).
    state.set_balance(wallet_a.address, 100)
    state.set_balance(wallet_b.address, 0)
    state.set_nonce(wallet_a.address, 0)
    state.set_nonce(wallet_b.address, 0)

    tx = Transaction(
        tx_type=TransactionType.PAYMENT,
        from_address=wallet_a.address,
        to_address=wallet_b.address,
        amount=30,
        nonce=0,
        payload={},
        pubkey=wallet_a.public_key_hex,
        timestamp=1_700_000_123,
    )
    sign_transaction(wallet_a, tx)

    validate_tx(tx, state)
    assert mempool.add(tx) is True

    result = mine_pending_transactions(
        chain=chain,
        state=state,
        mempool=mempool,
        miner_address=miner_wallet.address,
        difficulty=2,
        tx_limit=10,
        max_nonce=500_000,
    )

    assert chain.height() == 1
    assert len(mempool) == 0
    assert result.block.transactions[0].tx_type == TransactionType.COINBASE
    assert result.block.transactions[0].to_address == miner_wallet.address
    assert result.block.transactions[0].amount == BLOCK_REWARD
    assert state.get_balance(wallet_a.address) == 70
    assert state.get_balance(wallet_b.address) == 30
    assert state.get_balance(miner_wallet.address) == BLOCK_REWARD
    assert state.get_nonce(wallet_a.address) == 1

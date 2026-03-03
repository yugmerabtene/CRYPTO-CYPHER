from __future__ import annotations

import argparse
import json

import httpx

from src.client.keystore import load_wallet, save_wallet
from src.client.wallet import create_wallet, sign_transaction
from src.common.config import DEFAULT_NODE_URL
from src.common.types import Transaction, TransactionType


def send_transaction(node_url: str, tx: Transaction) -> dict:
    response = httpx.post(f"{node_url}/tx", json=tx.model_dump(mode="json"), timeout=10.0)
    response.raise_for_status()
    return response.json()


def command_wallet_create(args: argparse.Namespace) -> None:
    wallet = create_wallet()
    save_wallet(wallet, args.out)
    print(json.dumps({"address": wallet.address, "wallet_file": args.out}, indent=2))


def command_tx_send(args: argparse.Namespace) -> None:
    wallet = load_wallet(args.wallet)
    tx = Transaction(
        tx_type=TransactionType.PAYMENT,
        from_address=wallet.address,
        to_address=args.to,
        amount=args.amount,
        nonce=args.nonce,
        payload={},
        pubkey=wallet.public_key_hex,
    )
    sign_transaction(wallet, tx)
    result = send_transaction(args.node, tx)
    print(json.dumps(result, indent=2))


def command_tx_deploy(args: argparse.Namespace) -> None:
    wallet = load_wallet(args.wallet)
    tx = Transaction(
        tx_type=TransactionType.DEPLOY_CONTRACT,
        from_address=wallet.address,
        amount=0,
        nonce=args.nonce,
        payload={"code": args.code},
        pubkey=wallet.public_key_hex,
    )
    sign_transaction(wallet, tx)
    result = send_transaction(args.node, tx)
    print(json.dumps(result, indent=2))


def command_tx_call(args: argparse.Namespace) -> None:
    wallet = load_wallet(args.wallet)
    payload_args = json.loads(args.args) if args.args else {}
    tx = Transaction(
        tx_type=TransactionType.CALL_CONTRACT,
        from_address=wallet.address,
        to_address=args.contract,
        amount=0,
        nonce=args.nonce,
        payload={"method": args.method, "args": payload_args},
        pubkey=wallet.public_key_hex,
    )
    sign_transaction(wallet, tx)
    result = send_transaction(args.node, tx)
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CryptoCypher client CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    wallet_parser = subparsers.add_parser("wallet", help="Wallet operations")
    wallet_subparsers = wallet_parser.add_subparsers(dest="wallet_cmd", required=True)

    wallet_create = wallet_subparsers.add_parser("create", help="Create a wallet")
    wallet_create.add_argument("--out", required=True, help="Output wallet JSON file")
    wallet_create.set_defaults(func=command_wallet_create)

    tx_parser = subparsers.add_parser("tx", help="Transaction operations")
    tx_subparsers = tx_parser.add_subparsers(dest="tx_cmd", required=True)

    tx_send = tx_subparsers.add_parser("send", help="Send payment transaction")
    tx_send.add_argument("--wallet", required=True)
    tx_send.add_argument("--to", required=True)
    tx_send.add_argument("--amount", type=int, required=True)
    tx_send.add_argument("--nonce", type=int, required=True)
    tx_send.add_argument("--node", default=DEFAULT_NODE_URL)
    tx_send.set_defaults(func=command_tx_send)

    tx_deploy = tx_subparsers.add_parser("deploy_contract", help="Deploy contract transaction")
    tx_deploy.add_argument("--wallet", required=True)
    tx_deploy.add_argument("--code", required=True)
    tx_deploy.add_argument("--nonce", type=int, required=True)
    tx_deploy.add_argument("--node", default=DEFAULT_NODE_URL)
    tx_deploy.set_defaults(func=command_tx_deploy)

    tx_call = tx_subparsers.add_parser("call_contract", help="Call contract transaction")
    tx_call.add_argument("--wallet", required=True)
    tx_call.add_argument("--contract", required=True)
    tx_call.add_argument("--method", required=True)
    tx_call.add_argument("--args", default="{}", help="JSON object")
    tx_call.add_argument("--nonce", type=int, required=True)
    tx_call.add_argument("--node", default=DEFAULT_NODE_URL)
    tx_call.set_defaults(func=command_tx_call)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

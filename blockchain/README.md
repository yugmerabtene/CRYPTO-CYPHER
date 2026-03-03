# Blockchain PoC (Python)

Base locale pour un mini projet blockchain (node + client) en Python.

## Prerequis

- Python 3.11+

## Installation locale (PyCharm / terminal)

```bash
cd blockchain
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Lancer le node (sans Docker)

```bash
cd blockchain
python -m src.node.node_main
```

Node API (FastAPI):
- `POST /tx`
- `POST /mine`
- `GET /chain/head`
- `GET /chain/height`
- `GET /chain/block/{height}`

## Lancer le client CLI (sans Docker)

```bash
cd blockchain
python -m src.client.client_main --help
```

Exemples:

```bash
python -m src.client.client_main wallet create --out wallet_a.json
python -m src.client.client_main wallet create --out wallet_b.json
python -m src.client.client_main tx send --wallet wallet_a.json --to cc1... --amount 10 --nonce 0
```

## Tests

```bash
cd blockchain
python -m pytest -q
```

## Test manuel minage (end-to-end)

1) Lancer le node:

```bash
python -m src.node.node_main
```

2) Dans un autre terminal, soumettre une transaction puis miner:

```bash
python -m src.client.client_main wallet create --out wallet_sender.json
python -m src.client.client_main wallet create --out wallet_receiver.json
python -m src.client.client_main wallet create --out wallet_miner.json

# 1) Miner un premier bloc pour crediter sender (reward)
curl -s -X POST http://127.0.0.1:8080/mine \
  -H "Content-Type: application/json" \
  -d '{"miner_address":"<ADDRESS_SENDER>","difficulty":1}'

# 2) Envoyer une tx sender -> receiver
python -m src.client.client_main tx send --wallet wallet_sender.json --to <ADDRESS_RECEIVER> --amount 10 --nonce 0

# 3) Miner le bloc qui inclut la tx
curl -s -X POST http://127.0.0.1:8080/mine \
  -H "Content-Type: application/json" \
  -d '{"miner_address":"<ADDRESS_MINER>","difficulty":2}'
```

## Docker

Les fichiers `docker/` sont poses, mais la containerisation est volontairement la phase suivante
apres stabilisation locale.

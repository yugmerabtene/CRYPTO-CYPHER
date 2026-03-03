from __future__ import annotations

import uvicorn

from src.common.config import NODE_HOST, NODE_PORT


def main() -> None:
    uvicorn.run("src.node.api:app", host=NODE_HOST, port=NODE_PORT, reload=False)


if __name__ == "__main__":
    main()

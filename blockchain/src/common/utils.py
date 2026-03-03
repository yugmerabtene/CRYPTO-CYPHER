from __future__ import annotations

import json
import time
from typing import Any


def canonical_json_dumps(payload: Any) -> str:
    """Canonical JSON representation (stable keys and separators)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def utc_timestamp() -> int:
    return int(time.time())

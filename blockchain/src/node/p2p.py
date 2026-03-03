from __future__ import annotations


class PeerManager:
    """In-memory peer list for P2P bootstrap/gossip placeholder."""

    def __init__(self) -> None:
        self._peers: set[str] = set()

    def add_peer(self, peer: str) -> None:
        self._peers.add(peer)

    def remove_peer(self, peer: str) -> None:
        self._peers.discard(peer)

    def list_peers(self) -> list[str]:
        return sorted(self._peers)

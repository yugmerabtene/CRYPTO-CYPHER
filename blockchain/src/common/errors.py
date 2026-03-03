class BlockchainError(Exception):
    """Base error for blockchain application."""


class ValidationError(BlockchainError):
    """Raised when an object fails validation."""


class StorageError(BlockchainError):
    """Raised when persistence fails."""

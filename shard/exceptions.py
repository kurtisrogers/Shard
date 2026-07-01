class ShardError(Exception):
    """Base error for the Shard framework."""


class ComponentNotFoundError(ShardError):
    """Raised when a component cannot be resolved from the registry."""


class PropValidationError(ShardError):
    """Raised when component props fail validation."""


class ActionNotFoundError(ShardError):
    """Raised when an HTMX action does not exist on a component."""


class StateNotFoundError(ShardError):
    """Raised when component state cannot be loaded for an instance."""


class ViewDataError(ShardError):
    """Raised when view data is invalid or references a disallowed component."""

class CacheIDError(Exception):
    """Raised when the ID for a cached resource cannot be inferred."""
    def __init__(self, message: str = "Could not infer ID for cached resource.") -> None:
        super().__init__(message)


class UnsupportedRequestError(Exception):
    """Raised when the type of request is not supported."""
    def __init__(self, message: str = "Request type not supported.") -> None:
        super().__init__(message)


class ClientMissingError(Exception):
    """Raised when a required client object is None."""
    def __init__(self, message: str = "Client instance is None.") -> None:
        super().__init__(message)

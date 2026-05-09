class StockDataError(Exception):
    """Raised when upstream market data cannot be fetched or parsed."""


class StockDataUnavailable(StockDataError):
    """Raised when upstream market data returns no usable values."""

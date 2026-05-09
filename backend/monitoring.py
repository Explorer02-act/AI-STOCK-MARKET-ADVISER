from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from prometheus_client import Counter, Gauge

from configs.settings import DAILY_COST_LIMIT_USD, RATE_LIMIT_WARNING_THRESHOLD


API_REQUESTS = Counter(
    "stock_api_requests_total",
    "Total upstream API requests.",
    ["provider", "endpoint", "status"],
)
API_FAILURES = Counter(
    "stock_api_failures_total",
    "Total upstream API failures.",
    ["provider", "endpoint", "error_type"],
)
ESTIMATED_COST = Counter(
    "stock_api_estimated_cost_usd_total",
    "Estimated API cost in USD.",
    ["provider"],
)
RATE_LIMIT_REMAINING = Gauge(
    "stock_api_rate_limit_remaining",
    "Latest upstream rate limit remaining value.",
    ["provider"],
)


@dataclass
class UsageEvent:
    provider: str
    endpoint: str
    status: str
    estimated_cost_usd: float = 0.0
    rate_limit_remaining: int | None = None
    metadata: dict[str, Any] | None = None


class ApiUsageMonitor:
    def __init__(self) -> None:
        self._daily_costs: dict[tuple[str, date], float] = {}

    def record(self, event: UsageEvent) -> list[str]:
        API_REQUESTS.labels(event.provider, event.endpoint, event.status).inc()
        if event.estimated_cost_usd:
            ESTIMATED_COST.labels(event.provider).inc(event.estimated_cost_usd)

        warnings: list[str] = []
        if event.rate_limit_remaining is not None:
            RATE_LIMIT_REMAINING.labels(event.provider).set(event.rate_limit_remaining)
            if event.rate_limit_remaining <= RATE_LIMIT_WARNING_THRESHOLD:
                warnings.append(
                    f"{event.provider} rate limit is low: {event.rate_limit_remaining} remaining."
                )

        if event.estimated_cost_usd:
            key = (event.provider, date.today())
            self._daily_costs[key] = self._daily_costs.get(key, 0.0) + event.estimated_cost_usd
            if self._daily_costs[key] >= DAILY_COST_LIMIT_USD:
                warnings.append(
                    f"{event.provider} estimated daily cost reached ${self._daily_costs[key]:.4f}."
                )

        return warnings

    def record_failure(self, provider: str, endpoint: str, exc: Exception) -> None:
        API_FAILURES.labels(provider, endpoint, exc.__class__.__name__).inc()
        API_REQUESTS.labels(provider, endpoint, "failure").inc()


usage_monitor = ApiUsageMonitor()

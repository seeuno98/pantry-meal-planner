from prometheus_client import Histogram, Counter

REQUEST_LATENCY = Histogram("api_latency_seconds", "Latency by route", ["route"])
REQUESTS = Counter(
    "api_requests_total", "Requests by route/status", ["route", "status"]
)

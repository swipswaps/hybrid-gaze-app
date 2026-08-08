# Prometheus Metrics Exporter Middleware and Endpoint Integration for FastAPI
# Reference: Prometheus Python Client Documentation (https://github.com/prometheus/client_python)

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint', 'status_code']
)
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total count of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        endpoint = request.url.path
        response = await call_next(request)
        duration = time.time() - start_time
        status_code = response.status_code
        if endpoint != "/metrics":
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint, status_code=status_code).observe(duration)
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        return response

def setup_metrics_endpoint(app):
    app.add_middleware(PrometheusMiddleware)
    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

import time
import logging
from fastapi import Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    """
    Middleware that runs on every single request.
    Logs: method, path, status code, and how long it took.
    Example output:
        INFO | GET /api/v1/products/ → 200 | 12.4ms
    """
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} | {duration_ms}ms"
    )
    return response

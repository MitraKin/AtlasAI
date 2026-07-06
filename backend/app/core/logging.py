import logging
import time

logger = logging.getLogger("citypulse")


def log_request(method: str, path: str, status: int, duration_ms: float):
    logger.info("request %s %s -> %d (%.2fms)", method, path, status, duration_ms)

"""CityPulse FastAPI application."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.logging import log_request
from app.core.exceptions import CityPulseError
from app.api.v1.router import router as v1_router
from app.dependencies import get_repo

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("citypulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup env=%s", get_settings().env)
    get_repo()
    yield
    logger.info("shutdown")


app = FastAPI(
    title="CityPulse API",
    description="AI Civic Decision Copilot for Municipal Resource Allocation",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CityPulseError)
async def citypulse_error_handler(request: Request, exc: CityPulseError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "detail": exc.detail},
    )


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    log_request(request.method, request.url.path, response.status_code, duration)
    response.headers["X-Response-Time-ms"] = str(round(duration, 2))
    return response


app.include_router(v1_router)

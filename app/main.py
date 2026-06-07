import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import chart, notes, terminology

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Larkspur EMR started")
    yield
    logger.info("Larkspur EMR shutting down, store is durable on disk")


app = FastAPI(title="Larkspur EMR", lifespan=lifespan)
app.include_router(chart.router)
app.include_router(notes.router)
app.include_router(terminology.router)

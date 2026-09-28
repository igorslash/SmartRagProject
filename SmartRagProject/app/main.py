from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.endpoints import router
from app.rag_engine import load_index
from app.logger import setup_logging, get_logger

import phoenix as px
px.launch_app()

import llama_index.core
llama_index.core.set_global_handler("arize_phoenix")

# Инициализируем логирование
setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("server_starting", port=8000)
    load_index()
    logger.info("server_ready")
    yield
    logger.info("server_stopped")


app = FastAPI(
    title="Smart RAG API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, logging
from app.api.routes import router as api_router
from app.core.database import test_connection
from contextlib import asynccontextmanager

# Configuración del logger
logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    test_connection()
    yield

app = FastAPI(
    title="AI Docs Agent",
    description="Backend API for AI Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",  # Vite u otros frontends locales
    "http://127.0.0.1:5173",
    "http://localhost:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Puedes poner ["*"] si solo estás probando
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
      # Test connection on startup
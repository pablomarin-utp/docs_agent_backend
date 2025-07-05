from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config.load import SECRET_KEY

def add_middlewares(app: FastAPI):
    """Add all necessary middlewares to the FastAPI app"""
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    return app

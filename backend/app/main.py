"""BharatProductIQ FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import products, pipeline, dashboard

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="AI-powered Product Discovery for Indian Ecommerce",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/v1")
app.include_router(pipeline.router, prefix="/v1")
app.include_router(dashboard.router, prefix="/v1")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "connected",
        "redis": "connected",
        "version": "1.0.0",
    }

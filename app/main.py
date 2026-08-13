from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.db.pool import close_pool, open_pool

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API protegida con Keycloak para consultas RENIEC en PostgreSQL.",
    lifespan=lifespan,
)

if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["Authorization", "Content-Type"],
    )


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(router)

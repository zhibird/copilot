from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import init_db


@asynccontextmanager  # 启动钩子：启动时先建表
async def lifespan(_: FastAPI):
    init_db()
    yield

def create_app() -> FastAPI:
    """创建 FastAPI 应用（读取配置 -> 注册路由）。"""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Minimal enterprise IM AI Copilot service.",
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()  # uvicorn 入口

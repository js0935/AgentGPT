"""
AgentGPT FastAPI 應用程式工廠
=============================

負責建立 FastAPI 實例、註冊中介軟體（CORS）、掛載 API 路由、
以及註冊啟動／關閉生命週期事件。

所有 `/api` 路徑的請求都會由此分發至對應的 router。
"""

from importlib import metadata

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse

from reworkd_platform.logging import configure_logging
from reworkd_platform.settings import settings
from reworkd_platform.web.api.error_handling import platformatic_exception_handler
from reworkd_platform.web.api.errors import PlatformaticError
from reworkd_platform.web.api.router import api_router
from reworkd_platform.web.lifetime import (
    register_shutdown_event,
    register_startup_event,
)


def get_app() -> FastAPI:
    """
    建立並回傳已完全配置的 FastAPI 應用實例。

    配置項目包括：
    - 日誌系統 (loguru)
    - CORS 白名單（來自 settings.frontend_url）
    - API 路由（前綴 /api）
    - 自訂例外處理（PlatformaticError → JSON 錯誤回應）
    - 啟動／關閉生命週期事件（資料庫連線等）

    :return: 已配置的 FastAPI 應用實例
    """
    configure_logging()

    app = FastAPI(
        title="Reworkd Platform API",
        version=metadata.version("reworkd_platform"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_origin_regex=settings.allowed_origins_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_startup_event(app)
    register_shutdown_event(app)

    app.include_router(router=api_router, prefix="/api")

    app.exception_handler(PlatformaticError)(platformatic_exception_handler)

    return app

"""全域錯誤處理介接程式 — 將自訂例外轉換為標準化 JSON 回應。"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger

from reworkd_platform.web.api.errors import PlatformaticError


async def platformatic_exception_handler(
    _: Request,
    platform_exception: PlatformaticError,
) -> JSONResponse:
    if platform_exception.should_log:
        logger.exception(platform_exception)

    return JSONResponse(
        status_code=platform_exception.code,
        content={
            "error": platform_exception.__class__.__name__,
            "detail": platform_exception.detail,
            "code": platform_exception.code,
        },
    )


async def http_exception_handler(
    _: Request,
    exc: HTTPException,
) -> JSONResponse:
    """處理 FastAPI 原生 HTTPException（404/422 等），統一為相同 JSON 格式。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "detail": str(exc.detail),
            "code": exc.status_code,
        },
    )


async def unhandled_exception_handler(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    """最後防線：未預期例外一律回傳 500，不向客戶端洩漏內部細節。"""
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": "伺服器內部錯誤，請稍後再試。",
            "code": 500,
        },
    )

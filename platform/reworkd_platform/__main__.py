"""
AgentGPT 後端服務入口
=====================

啟動 FastAPI 應用程式伺服器，負責處理所有 AI Agent 的任務排程、
OpenAI API 呼叫、資料庫操作與串流回應。

使用方式：
    poetry run python -m reworkd_platform
"""

import uvicorn

from reworkd_platform.settings import settings


def main() -> None:
    """啟動 Uvicorn 伺服器，根據 settings 配置決定 host、port、worker 數量與 hot-reload。"""
    uvicorn.run(
        "reworkd_platform.web.application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        factory=True,
    )


if __name__ == "__main__":
    main()

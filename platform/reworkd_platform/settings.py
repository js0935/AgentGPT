"""
AgentGPT 應用程式設定
=====================

所有環境變數透過 Pydantic BaseSettings 自動從 .env 載入。
變數前綴為 REWORKD_PLATFORM_（例如 REWORKD_PLATFORM_DB_HOST）。

使用方式：
    from reworkd_platform.settings import settings
    settings.db_host  # 取得資料庫主機
"""

from pathlib import Path
from tempfile import gettempdir
from typing import Literal, Optional

from pydantic import BaseSettings
from yarl import URL

from reworkd_platform.constants import ENV_PREFIX

TEMP_DIR = Path(gettempdir())

LOG_LEVEL = Literal[
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "FATAL",
]

ENVIRONMENT = Literal[
    "development",
    "production",
]


class Settings(BaseSettings):
    """應用程式設定，所有欄位皆可透過環境變數覆寫。"""

    host: str = "127.0.0.1"
    port: int = 8000
    workers_count: int = 1
    reload: bool = True
    environment: ENVIRONMENT = "development"
    log_level: LOG_LEVEL = "INFO"
    secret_signing_key: str = "JF52S66x6WMoifP5gZreiguYs9LYMn0lkXqgPYoNMD0="

    # ── OpenAI ────────────────────────────────────
    openai_api_base: str = "https://api.openai.com/v1"
    openai_api_key: str = "<Should be updated via env>"
    openai_api_version: str = "2023-08-01-preview"
    azure_openai_deployment_name: str = "<Should be updated via env if using azure>"

    # ── Helicone（OpenAI 代理／監控）─────────────
    helicone_api_base: str = "https://oai.hconeai.com/v1"
    helicone_api_key: Optional[str] = None

    # ── 第三方服務 ───────────────────────────────
    replicate_api_key: Optional[str] = None
    serp_api_key: Optional[str] = None

    # ── CORS ─────────────────────────────────────
    frontend_url: str = "http://localhost:3000"
    allowed_origins_regex: Optional[str] = None

    # ── 資料庫 ───────────────────────────────────
    db_host: str = "localhost"
    db_port: int = 3308
    db_user: str = "reworkd_platform"
    db_pass: str = "reworkd_platform"
    db_base: str = "reworkd_platform"
    db_echo: bool = False
    db_ca_path: Optional[str] = None

    # ── Pinecone 向量資料庫 ──────────────────────
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    pinecone_environment: Optional[str] = None

    # ── Sentry 錯誤追蹤 ──────────────────────────
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = 1.0

    # ── 功能設定 ─────────────────────────────────
    ff_mock_mode_enabled: bool = False
    max_loops: int = 25

    # ── SID 認證 ─────────────────────────────────
    sid_client_id: Optional[str] = None
    sid_client_secret: Optional[str] = None
    sid_redirect_uri: Optional[str] = None

    @property
    def db_url(self) -> URL:
        """以設定值組合成 MySQL 連線 URL。"""
        return URL.build(
            scheme="mysql+aiomysql",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def helicone_enabled(self) -> bool:
        """Helicone 代理是否已完整配置。"""
        return all(
            [
                self.helicone_api_base,
                self.helicone_api_key,
            ]
        )

    @property
    def sid_enabled(self) -> bool:
        """SID 認證是否已完整配置。"""
        return all(
            [
                self.sid_client_id,
                self.sid_client_secret,
                self.sid_redirect_uri,
            ]
        )

    class Config:
        env_file = ".env"
        env_prefix = ENV_PREFIX
        env_file_encoding = "utf-8"


settings = Settings()

"""CRUD 基底類別 — 提供資料庫操作共用的 session 初始化。"""

from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound="BaseCrud")


class BaseCrud:
    def __init__(self, session: AsyncSession):
        self.session = session

from abc import ABC, abstractmethod
from typing import Optional

from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from langchain_core.language_models import BaseChatModel

from reworkd_platform.db.crud.oauth import OAuthCrud
from reworkd_platform.schemas.user import UserBase


class Tool(ABC):
    description: str = ""
    public_description: str = ""
    arg_description: str = "The argument to the function."
    image_url: str = "/tools/openai-white.png"

    model: BaseChatModel
    language: str

    def __init__(self, model: BaseChatModel, language: str):
        self.model = model
        self.language = language

    @staticmethod
    def available() -> bool:
        return True

    @staticmethod
    async def dynamic_available(user: UserBase, oauth_crud: OAuthCrud) -> bool:
        return True

    @abstractmethod
    async def call(
        self,
        goal: str,
        task: str,
        input_str: str,
        user: UserBase,
        oauth_crud: OAuthCrud,
    ) -> FastAPIStreamingResponse:
        pass

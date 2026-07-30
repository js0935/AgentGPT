"""LLM 模型工廠 — 根據設定建立 OpenAI / Azure OpenAI 聊天模型實例。"""

from typing import Any, Dict, Optional, Tuple, Type, Union

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import BaseModel, Field

from reworkd_platform.schemas.agent import LLM_Model, ModelSettings
from reworkd_platform.schemas.user import UserBase
from reworkd_platform.settings import Settings


class WrappedChatOpenAI(ChatOpenAI):
    """Wrapped ChatOpenAI with explicit field declarations for type safety."""

    max_tokens: int = Field(default=500)
    model_name: LLM_Model = Field(default="meta/llama-3.1-8b-instruct", alias="model")


class WrappedAzureChatOpenAI(AzureChatOpenAI, WrappedChatOpenAI):
    openai_api_base: str
    openai_api_version: str
    deployment_name: str


WrappedChat = Union[WrappedAzureChatOpenAI, WrappedChatOpenAI]


def create_model(
    settings: Settings,
    model_settings: ModelSettings,
    user: UserBase,
    streaming: bool = False,
    force_model: Optional[LLM_Model] = None,
) -> WrappedChat:
    use_azure = (
        not model_settings.custom_api_key and "azure" in settings.openai_api_base
    )

    llm_model = force_model or model_settings.model
    model_class: Type[WrappedChat] = WrappedChatOpenAI
    base, headers, use_helicone = get_base_and_headers(settings, model_settings, user)
    model_kwargs: Dict[str, Any] = {"user": user.email}
    if headers is not None:
        model_kwargs["headers"] = headers

    kwargs = {
        "openai_api_base": base,
        "openai_api_key": model_settings.custom_api_key or settings.openai_api_key,
        "temperature": model_settings.temperature,
        "model": llm_model,
        "max_tokens": model_settings.max_tokens,
        "streaming": streaming,
        "max_retries": 5,
        "model_kwargs": model_kwargs,
    }

    if use_azure:
        model_class = WrappedAzureChatOpenAI
        deployment_name = llm_model.replace(".", "")
        kwargs.update(
            {
                "openai_api_version": settings.openai_api_version,
                "deployment_name": deployment_name,
                "openai_api_type": "azure",
                "openai_api_base": base.rstrip("v1"),
            }
        )

        if use_helicone:
            kwargs["model"] = deployment_name

    return model_class(**kwargs)


def get_base_and_headers(
    settings_: Settings, model_settings: ModelSettings, user: UserBase
) -> Tuple[str, Optional[Dict[str, str]], bool]:
    use_helicone = settings_.helicone_enabled and not model_settings.custom_api_key
    base = (
        settings_.helicone_api_base
        if use_helicone
        else (
            "https://api.openai.com/v1"
            if model_settings.custom_api_key
            else settings_.openai_api_base
        )
    )

    headers = (
        {
            "Helicone-Auth": f"Bearer {settings_.helicone_api_key}",
            "Helicone-Cache-Enabled": "true",
            "Helicone-User-Id": user.id,
            "Helicone-OpenAI-Api-Base": settings_.openai_api_base,
        }
        if use_helicone
        else None
    )

    return base, headers, use_helicone

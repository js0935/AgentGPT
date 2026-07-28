"""AI 模型呼叫輔助函式 — 封裝 LangChain 模型呼叫與錯誤處理邏輯。"""

import asyncio
from typing import Any, Dict, TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import BaseOutputParser, OutputParserException
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import Runnable
from loguru import logger

from reworkd_platform.schemas.agent import ModelSettings
from reworkd_platform.web.api.errors import OpenAIError

T = TypeVar("T")


def parse_with_handling(parser: BaseOutputParser[T], completion: str) -> T:
    try:
        return parser.parse(completion)
    except OutputParserException as e:
        raise OpenAIError(
            e, "There was an issue parsing the response from the AI model."
        )


async def call_model_with_handling(
    model: BaseChatModel,
    prompt: BasePromptTemplate,
    args: Dict[str, str],
    settings: ModelSettings,
    **kwargs: Any,
) -> str:
    """Execute a prompt and model using LCEL (LangChain Expression Language).

    Retries on transient errors (rate limit, server unavailable) with
    exponential backoff. Non-transient errors (auth, quota, model access)
    fail fast.
    """
    chain: Runnable = prompt | model
    max_retries = 3
    last_exception: Exception = Exception()

    for attempt in range(max_retries):
        try:
            result = await chain.ainvoke(args, **kwargs)
            if hasattr(result, "content"):
                return result.content
            return str(result)
        except Exception as e:
            last_exception = e
            error_msg = str(e)

            # Non-retriable errors → fail fast
            if "InsufficientQuota" in error_msg or "quota" in error_msg.lower():
                raise OpenAIError(
                    e,
                    "Your API key exceeded your current quota, please check your plan and billing details.",
                    should_log=not settings.custom_api_key,
                )
            if "Authentication" in error_msg or "401" in error_msg:
                raise OpenAIError(
                    e,
                    "Authentication error: Ensure a valid API key is being used.",
                    should_log=not settings.custom_api_key,
                )
            if "access_to_model" in error_msg or "model_not_found" in error_msg:
                raise OpenAIError(
                    e,
                    "Your API key does not have access to your current model. Please use a different model.",
                    should_log=not settings.custom_api_key,
                )

            # Transient errors → retry with backoff
            is_transient = (
                "ServiceUnavailable" in error_msg
                or "503" in error_msg
                or "RateLimit" in error_msg
                or "429" in error_msg
                or "timeout" in error_msg.lower()
                or "server_error" in error_msg.lower()
            )
            if is_transient and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
                logger.warning(
                    f"Transient OpenAI error (attempt {attempt + 1}/{max_retries}): "
                    f"{error_msg[:120]}. Retrying in {wait}s..."
                )
                await asyncio.sleep(wait)
                continue

            # Last attempt or non-retriable → surface error
            if is_transient:
                raise OpenAIError(
                    e,
                    "OpenAI is temporarily unavailable. Please try again later.",
                )
            raise OpenAIError(
                e,
                "There was an unexpected issue getting a response from the AI model.",
            )

    # Shouldn't reach here, but just in case
    raise OpenAIError(last_exception, "Failed to get a response after all retries.")

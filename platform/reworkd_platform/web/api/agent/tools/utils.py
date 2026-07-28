from dataclasses import dataclass
from typing import AsyncGenerator, List

from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable


@dataclass
class CitedSnippet:
    index: int
    text: str
    url: str = ""

    def __repr__(self) -> str:
        """
        The string representation the AI model will see
        """
        return f"{{i: {self.index}, text: {self.text}, url: {self.url}}}"


@dataclass
class Snippet:
    text: str

    def __repr__(self) -> str:
        """
        The string representation the AI model will see
        """
        return f"{{text: {self.text}}}"


async def _stream_chain(
    chain: Runnable,
    inputs: dict,
) -> AsyncGenerator[str, None]:
    """Stream an LCEL chain's output chunk by chunk."""
    async for chunk in chain.astream(inputs):
        if isinstance(chunk, str):
            yield chunk
        elif hasattr(chunk, "content") and chunk.content:
            yield chunk.content


def summarize(
    model: BaseChatModel,
    language: str,
    goal: str,
    text: str,
) -> FastAPIStreamingResponse:
    from reworkd_platform.web.api.agent.prompts import summarize_prompt

    chain: Runnable = summarize_prompt | model

    return FastAPIStreamingResponse(
        _stream_chain(chain, {"goal": goal, "language": language, "text": text}),
        media_type="text/event-stream",
    )


def summarize_with_sources(
    model: BaseChatModel,
    language: str,
    goal: str,
    query: str,
    snippets: List[CitedSnippet],
) -> FastAPIStreamingResponse:
    from reworkd_platform.web.api.agent.prompts import summarize_with_sources_prompt

    chain: Runnable = summarize_with_sources_prompt | model

    return FastAPIStreamingResponse(
        _stream_chain(
            chain,
            {
                "goal": goal,
                "query": query,
                "language": language,
                "snippets": snippets,
            },
        ),
        media_type="text/event-stream",
    )


def summarize_sid(
    model: BaseChatModel,
    language: str,
    goal: str,
    query: str,
    snippets: List[Snippet],
) -> FastAPIStreamingResponse:
    from reworkd_platform.web.api.agent.prompts import summarize_sid_prompt

    chain: Runnable = summarize_sid_prompt | model

    return FastAPIStreamingResponse(
        _stream_chain(
            chain,
            {
                "goal": goal,
                "query": query,
                "language": language,
                "snippets": snippets,
            },
        ),
        media_type="text/event-stream",
    )

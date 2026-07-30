"""DuckDuckGo 搜尋工具 — 免 API key，直接從公開搜尋引擎獲取即時資訊。"""

from typing import Any, List

from duckduckgo_search import DDGS
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from loguru import logger

from reworkd_platform.web.api.agent.stream_mock import stream_string
from reworkd_platform.web.api.agent.tools.reason import Reason
from reworkd_platform.web.api.agent.tools.tool import Tool
from reworkd_platform.web.api.agent.tools.utils import (
    CitedSnippet,
    summarize_with_sources,
)


async def _duckduckgo_search_results(
    search_term: str, max_results: int = 5
) -> List[dict[str, Any]]:
    """使用 DuckDuckGo 搜尋並回傳結構化結果。"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_term, max_results=max_results))
            return results
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return []


class DuckDuckSearch(Tool):
    description = (
        "Search the web via DuckDuckGo for current information, news, and real-time data. "
        "Use this when you need up-to-date information beyond the model's training data."
    )
    public_description = (
        "Search DuckDuckGo for current information about any topic."
    )
    arg_description = "The search query to look up on the web."
    image_url = "/tools/search.png"

    @staticmethod
    def available() -> bool:
        return True  # 無需 API key，永遠可用

    async def call(
        self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any
    ) -> FastAPIStreamingResponse:
        try:
            return await self._call(goal, task, input_str, *args, **kwargs)
        except Exception:
            logger.exception("DuckDuckGo search failed, falling back to reasoning")
            return await Reason(self.model, self.language).call(
                goal, task, input_str, *args, **kwargs
            )

    async def _call(
        self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any
    ) -> FastAPIStreamingResponse:
        raw_results = await _duckduckgo_search_results(input_str, max_results=5)

        snippets: List[CitedSnippet] = []
        for i, result in enumerate(raw_results):
            title = result.get("title", "")
            body = result.get("body", "")
            href = result.get("href", "")
            text = f"{title}: {body}" if title else body
            snippets.append(CitedSnippet(i + 1, text, href))

        if len(snippets) == 0:
            return stream_string(
                "No search results found. Please try a different query.", True
            )

        return summarize_with_sources(self.model, self.language, goal, task, snippets)


async def web_search_simple(query: str, max_results: int = 5) -> str:
    """簡易網頁搜尋，回傳純文字格式結果（供 chat 端點直接使用）。

    回傳格式：
    [1] title: body (url)
    [2] title: body (url)
    ...
    若無結果則回傳空字串。
    """
    raw_results = await _duckduckgo_search_results(query, max_results=max_results)
    if not raw_results:
        return ""

    lines: list[str] = []
    for i, result in enumerate(raw_results):
        title = result.get("title", "")
        body = result.get("body", "")
        href = result.get("href", "")
        if title or body:
            text = f"{title}: {body}" if title and body else (title or body)
            lines.append(f"[{i + 1}] {text} ({href})")

    return "\n".join(lines)

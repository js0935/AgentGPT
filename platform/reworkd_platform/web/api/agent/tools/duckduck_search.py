"""網頁搜尋與即時資料工具 — DuckDuckGo 搜尋 + Yahoo Finance 股市即時資料。"""

from datetime import datetime
from typing import Any, List
from urllib.parse import quote

import aiohttp
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


STOCK_MARKET_KEYWORDS = [
    "股市", "股票", "股價", "加權指數", "大盤", "指數", "收盤", "開盤",
    "盤勢", "漲跌", "台股", "證交所", "上市", "上櫃",
    "台積電", "聯發科", "鴻海", "中華電", "0050", "2330", "2454", "2317",
    "stock", "market", "TAIEX", "TWII", "shares", "share price",
]


def is_stock_market_query(message: str) -> bool:
    """判斷查詢是否與股市/股價相關。"""
    lower = message.lower()
    return any(kw in lower for kw in STOCK_MARKET_KEYWORDS)


async def fetch_stock_market() -> str:
    """從 Yahoo Finance 抓取台灣股市即時行情（免 API key）。

    回傳格式：
    [1] 加權指數 ^TWII: 42593.78 (前收 43634.19, 漲跌 -1040.41, -2.38%) (更新時間 ...)
    ...
    失敗時回傳空字串。
    """
    symbols = [
        "^TWII",   # 台灣加權指數
        "0050.TW", # 元大台灣50 ETF
        "2330.TW", # 台積電
        "2454.TW", # 聯發科
        "2317.TW", # 鴻海
        "2412.TW", # 中華電
    ]
    lines: list[str] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            url = (
                f"https://query1.finance.yahoo.com/v8/finance/chart/"
                f"{quote(symbol)}?interval=1d&range=5d"
            )
            try:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Yahoo Finance {symbol}: HTTP {response.status}")
                        continue
                    data = await response.json()
                    meta = data["chart"]["result"][0]["meta"]
                    price = meta.get("regularMarketPrice")
                    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
                    name = meta.get("shortName") or meta.get("longName") or symbol
                    if price is None or prev is None:
                        continue
                    change = price - prev
                    pct = change / prev * 100
                    ts = meta.get("regularMarketTime")
                    time_str = (
                        datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
                        if ts
                        else "unknown"
                    )
                    lines.append(
                        f"[{len(lines) + 1}] {name} ({symbol}): 現價 {price:.2f}, "
                        f"漲跌 {change:+.2f} ({pct:+.2f}%), 更新時間 {time_str}"
                    )
            except Exception as e:
                logger.warning(f"Yahoo Finance {symbol} failed: {e}")

    if not lines:
        return ""

    return (
        "以下為台灣股市即時行情（來源：Yahoo Finance）：\n"
        + "\n".join(lines)
        + "\n\n請依據以上即時數據回答，不要使用訓練資料中的舊數據。"
    )


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

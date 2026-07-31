"""網頁搜尋與即時資料工具 — DuckDuckGo 搜尋 + 台灣證交所(TWSE)股市即時資料。"""

import ssl
import time
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
    "台積電", "聯發科", "鴻海", "中華電", "台達電", "聯電", "廣達", "緯創",
    "大立光", "華碩", "長榮", "陽明", "富邦金", "國泰金", "中信金", "玉山金",
    "中鋼", "台塑", "統一",
    "0050", "0056", "006208", "00878", "00919", "00929", "00940", "00900", "00713",
    "2330", "2454", "2317", "2308", "2303", "2382", "3231", "3008", "2357",
    "2603", "2609", "2881", "2882", "2891", "2884", "2002", "1301", "6505", "1216",
    "stock", "market", "TAIEX", "TWII", "shares", "share price",
]

ETF_KEYWORDS = ["etf", "基金", "配息", "殖利率", "投資組合"]

SYMBOL_ZH_NAMES = {
    "^TWII": "台灣加權指數",
    "0050.TW": "元大台灣50",
    "0056.TW": "元大高股息",
    "006208.TW": "富邦台50",
    "00878.TW": "國泰永續高股息",
    "00919.TW": "群益台灣精選高息",
    "00929.TW": "復華台灣科技優息",
    "00940.TW": "元大台灣價值高息",
    "00900.TW": "富邦特選高股息30",
    "00713.TW": "元大台灣高息低波",
    "00679B.TW": "元大美債20年",
    "2330.TW": "台積電",
    "2454.TW": "聯發科",
    "2317.TW": "鴻海",
    "2412.TW": "中華電",
    "2308.TW": "台達電",
    "2303.TW": "聯電",
    "2382.TW": "廣達",
    "3231.TW": "緯創",
    "3008.TW": "大立光",
    "2357.TW": "華碩",
    "2603.TW": "長榮",
    "2609.TW": "陽明",
    "2881.TW": "富邦金",
    "2882.TW": "國泰金",
    "2891.TW": "中信金",
    "2884.TW": "玉山金",
    "2002.TW": "中鋼",
    "1301.TW": "台塑",
    "6505.TW": "台塑化",
    "1216.TW": "統一",
}


def is_stock_market_query(message: str) -> bool:
    """判斷查詢是否與股市/股價/ETF 相關。"""
    lower = message.lower()
    return any(kw in lower for kw in STOCK_MARKET_KEYWORDS) or any(
        kw in lower for kw in ETF_KEYWORDS
    )


# TWSE 官方即時報價的代號（tse_ = 上市；t00 = 加權指數）
TWSE_INDEX_CODE = "tse_t00.tw"

# 行情快取：短時間內重複查詢直接回傳，避免每次打 TWSE API（30 秒 TTL）
_MARKET_CACHE: dict[str, tuple[float, str]] = {}
_MARKET_CACHE_TTL = 30.0


def _is_etf_query(query: str) -> bool:
    lower = query.lower()
    return any(kw in lower for kw in ETF_KEYWORDS)


def _twse_code_to_yahoo_symbol(ex_ch: str) -> str:
    """把 TWSE 代號（tse_2330.tw / tse_t00.tw）轉成 Yahoo symbol（2330.TW / ^TWII）。"""
    if ex_ch == TWSE_INDEX_CODE:
        return "^TWII"
    return ex_ch.removeprefix("tse_").removesuffix(".tw").upper() + ".TW"


async def _fetch_twse_quotes(
    session: aiohttp.ClientSession, ex_codes: list[str]
) -> list[str]:
    """從台灣證交所（TWSE）官方即時報價 API 抓取行情。

    API: mis.twse.com.tw/stock/api/getStockInfo.jsp
    欄位：z=最新成交價, y=昨收, o=開盤, h=最高, l=最低, n=中文名稱,
          d=日期(YYYYMMDD), t=時間(HH:MM:SS), ch=代號, c=股票代碼
    注意：Yahoo Finance 的台股 previousClose 基準錯亂，不可用；TWSE 為唯一可靠來源。
    """
    lines: list[str] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"

    # 分批查詢（每批最多 10 檔，避免 URL 過長）
    for i in range(0, len(ex_codes), 10):
        batch = ex_codes[i : i + 10]
        params = {"ex_ch": "|".join(batch), "json": "1"}
        try:
            async with session.get(
                url, params=params, headers=headers, timeout=10
            ) as response:
                if response.status != 200:
                    logger.warning(f"TWSE API: HTTP {response.status}")
                    continue
                # TWSE 的 content-type 是 text/html 但內容為 JSON，需忽略 mimetype
                data = await response.json(content_type=None)
        except Exception as e:
            logger.warning(f"TWSE API failed: {e}")
            continue

        for item in data.get("msgArray", []):
            raw_ch = item.get("ch", "")
            ex_ch = raw_ch if raw_ch.startswith("tse_") else f"tse_{raw_ch}"
            z = item.get("z", "-")  # 最新成交價
            y = item.get("y", "-")  # 昨收
            if z == "-" or y == "-":
                continue
            try:
                price = float(z)
                prev = float(y)
            except ValueError:
                continue
            if price <= 0 or prev <= 0:
                continue
            name = (
                "台灣加權指數"
                if ex_ch == TWSE_INDEX_CODE
                else item.get("n", item.get("c", ex_ch))
            )
            symbol = _twse_code_to_yahoo_symbol(ex_ch)
            change = price - prev
            pct = change / prev * 100
            arrow = "▲" if change > 0 else ("▼" if change < 0 else "—")
            date = item.get("d", "")
            tm = item.get("t", "")
            if len(date) == 8 and tm:
                time_str = f"{date[:4]}-{date[4:6]}-{date[6:]} {tm[:5]}"
            else:
                time_str = "unknown"
            lines.append(
                f"| {name} | {symbol} | {price:.2f} | {arrow} {change:+.2f} | "
                f"{pct:+.2f}% | {time_str} |"
            )
    return lines


async def _fetch_yahoo_fallback(
    session: aiohttp.ClientSession, ex_codes: list[str]
) -> list[str]:
    """TWSE 失敗時的備援：用 Yahoo Finance 歷史日線的最後兩根 K 線計算漲跌。

    注意：Yahoo 的 meta.previousClose/chartPreviousClose 對台股錯亂
    （把開盤價或其他日期的收盤當昨收），必須用歷史序列自行推算。
    """
    lines: list[str] = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    for ex_ch in ex_codes:
        symbol = _twse_code_to_yahoo_symbol(ex_ch)
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/"
            f"{quote(symbol)}?interval=1d&range=10d"
        )
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    continue
                data = await response.json()
                closes = [
                    c
                    for c in data["chart"]["result"][0]["indicators"]["quote"][0].get(
                        "close"
                    )
                    or []
                    if c is not None
                ]
                if len(closes) < 2:
                    continue
                price = closes[-1]
                prev = closes[-2]
                name = SYMBOL_ZH_NAMES.get(symbol) or data["chart"]["result"][0][
                    "meta"
                ].get("shortName") or symbol
                change = price - prev
                pct = change / prev * 100
                arrow = "▲" if change > 0 else ("▼" if change < 0 else "—")
                lines.append(
                    f"| {name} | {symbol} | {price:.2f} | {arrow} {change:+.2f} | "
                    f"{pct:+.2f}% | unknown |"
                )
        except Exception as e:
            logger.warning(f"Yahoo Finance {symbol} failed: {e}")
    return lines


async def fetch_stock_market(query: str = "") -> str:
    """從台灣證交所（TWSE）官方 API 抓取台灣股市即時行情（免 API key）。

    query 含 ETF/基金相關字詞時抓熱門 ETF 報價，否則抓指數與權值股。
    TWSE 失敗時 fallback 到 Yahoo Finance 歷史日線。
    全部失敗時回傳空字串。
    """
    cache_key = "etf" if _is_etf_query(query) else "stocks"
    now = time.monotonic()
    cached = _MARKET_CACHE.get(cache_key)
    if cached and now - cached[0] < _MARKET_CACHE_TTL:
        return cached[1]

    if _is_etf_query(query):
        ex_codes = [
            "tse_t00.tw",    # 台灣加權指數
            "tse_0050.tw",   # 元大台灣50 ETF
            "tse_0056.tw",   # 元大高股息 ETF
            "tse_006208.tw", # 富邦台50 ETF
            "tse_00878.tw",  # 國泰永續高股息 ETF
            "tse_00919.tw",  # 群益台灣精選高息 ETF
            "tse_00929.tw",  # 復華台灣科技優息 ETF
            "tse_00940.tw",  # 元大台灣價值高息 ETF
            "tse_00900.tw",  # 富邦特選高股息30 ETF
            "tse_00713.tw",  # 元大台灣高息低波 ETF
            "tse_00679B.tw", # 元大美債20年 ETF
        ]
    else:
        ex_codes = [
            "tse_t00.tw",  # 台灣加權指數
            "tse_2330.tw", # 台積電
            "tse_2454.tw", # 聯發科
            "tse_2317.tw", # 鴻海
            "tse_2412.tw", # 中華電
            "tse_2308.tw", # 台達電
            "tse_2303.tw", # 聯電
            "tse_2382.tw", # 廣達
            "tse_3231.tw", # 緯創
            "tse_3008.tw", # 大立光
            "tse_2603.tw", # 長榮
            "tse_2881.tw", # 富邦金
            "tse_2002.tw", # 中鋼
            "tse_0050.tw", # 元大台灣50 ETF
        ]

    # mis.twse.com.tw 的 TLS 憑證缺少 Subject Key Identifier 擴充，
    # Python OpenSSL 3.x 嚴格驗證會拒絕（curl/瀏覽器不受影響），
    # 因此僅對 TWSE 官方行情查詢使用不驗證憑證的 SSL context。
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_ctx)
    ) as session:
        lines = await _fetch_twse_quotes(session, ex_codes)
        source = "台灣證交所（TWSE）"
        if not lines:
            async with aiohttp.ClientSession() as yahoo_session:
                lines = await _fetch_yahoo_fallback(yahoo_session, ex_codes)
            source = "Yahoo Finance（TWSE 暫時無法連線）"

    if not lines:
        return ""

    header = "| 名稱 | 代碼 | 現價 | 漲跌 | 漲跌幅 | 更新時間 |"
    separator = "|---|---|---|---|---|---|"
    result = (
        f"以下為台灣股市即時行情（來源：{source}）：\n\n"
        f"{header}\n{separator}\n"
        + "\n".join(lines)
        + "\n\n請依據以上即時數據回答，不要使用訓練資料中的舊數據。"
    )
    _MARKET_CACHE[cache_key] = (time.monotonic(), result)
    return result


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
        if is_stock_market_query(input_str) or is_stock_market_query(task):
            market_data = await fetch_stock_market(query=f"{task} {input_str}")
            if market_data:
                snippet = CitedSnippet(1, market_data, "https://finance.yahoo.com")
                return summarize_with_sources(
                    self.model, self.language, goal, task, [snippet]
                )

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

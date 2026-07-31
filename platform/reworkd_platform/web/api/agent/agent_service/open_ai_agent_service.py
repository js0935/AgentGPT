"""OpenAI Agent 服務實作 — 透過 LangChain 串接 OpenAI API 執行 agent 工作流程。"""

from typing import Any, AsyncGenerator, List, Optional

import asyncio
import json
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import Runnable
from loguru import logger
from pydantic import ValidationError

from reworkd_platform.db.crud.oauth import OAuthCrud
from reworkd_platform.schemas.agent import ModelSettings
from reworkd_platform.schemas.user import UserBase
from reworkd_platform.services.tokenizer.token_service import TokenService
from reworkd_platform.web.api.agent.agent_service.agent_service import AgentService
from reworkd_platform.web.api.agent.analysis import Analysis, AnalysisArguments
from reworkd_platform.web.api.agent.helpers import (
    call_model_with_handling,
    parse_with_handling,
)
from reworkd_platform.web.api.agent.model_factory import WrappedChatOpenAI
from reworkd_platform.web.api.agent.prompts import (
    analyze_task_prompt,
    chat_prompt,
    create_tasks_prompt,
    debate_analyst_prompt,
    debate_synthesis_prompt,
    start_goal_prompt,
)
from reworkd_platform.web.api.agent.task_output_parser import TaskOutputParser
from reworkd_platform.web.api.agent.tools.open_ai_function import get_tool_function
from reworkd_platform.web.api.agent.tools.tools import (
    get_default_tool,
    get_tool_from_name,
    get_tool_name,
    get_user_tools,
)
from reworkd_platform.web.api.agent.tools.duckduck_search import (
    fetch_stock_market,
    is_stock_market_query,
    web_search_simple,
)
from reworkd_platform.web.api.agent.tools.utils import summarize
from reworkd_platform.web.api.errors import OpenAIError


DEBATE_KEYWORDS = [
    "分析", "推薦", "建議", "比較", "評估", "看法", "評價",
    "優缺點", "討論", "辯論", "值得", "如何選擇", "怎麼選",
    "哪個", "選哪", "利弊",
]

DEBATE_PERSPECTIVES = [
    (
        "成長與機會分析師",
        "從成長潛力與投資機會的角度分析。指出最有潛力的標的或方向、潛在催化劑、以及為何現在值得關注。不要重複或回應其他分析師的觀點。",
    ),
    (
        "風險與保守分析師",
        "從風險管理與保守穩健的角度分析。指出風險因素、波動來源、估值過高的可能、下行風險，以及資產配置上的注意事項。不要重複或回應其他分析師的觀點。",
    ),
    (
        "平衡與價值分析師",
        "從基本面與長期價值的角度分析。評估標的品質、當前價格是否合理、長期持有價值，並給出務實的取捨建議。不要重複或回應其他分析師的觀點。",
    ),
]


def is_debate_query(message: str) -> bool:
    """判斷是否為需要多方觀點討論的深度分析問題。"""
    lower = message.lower()
    return any(kw in lower for kw in DEBATE_KEYWORDS)


async def _stream_lcel(
    chain: Runnable,
    inputs: dict[str, Any],
) -> AsyncGenerator[str, None]:
    """Stream LCEL chain output as text chunks."""
    async for chunk in chain.astream(inputs):
        if isinstance(chunk, str):
            yield chunk
        elif hasattr(chunk, "content") and chunk.content:
            yield chunk.content


class OpenAIAgentService(AgentService):
    def __init__(
        self,
        model: WrappedChatOpenAI,
        settings: ModelSettings,
        token_service: TokenService,
        callbacks: Optional[List[Any]],
        user: UserBase,
        oauth_crud: OAuthCrud,
    ):
        self.model = model
        self.settings = settings
        self.token_service = token_service
        self.callbacks = callbacks
        self.user = user
        self.oauth_crud = oauth_crud

    async def start_goal_agent(self, *, goal: str) -> List[str]:
        prompt = ChatPromptTemplate.from_messages(
            [SystemMessagePromptTemplate(prompt=start_goal_prompt)]
        )

        self.token_service.calculate_max_tokens(
            self.model,
            prompt.format_prompt(
                goal=goal,
                language=self.settings.language,
            ).to_string(),
        )

        completion = await call_model_with_handling(
            self.model,
            ChatPromptTemplate.from_messages(
                [SystemMessagePromptTemplate(prompt=start_goal_prompt)]
            ),
            {"goal": goal, "language": self.settings.language},
            settings=self.settings,
            callbacks=self.callbacks,
        )

        task_output_parser = TaskOutputParser(completed_tasks=[])
        tasks = parse_with_handling(task_output_parser, completion)

        return tasks

    async def analyze_task_agent(
        self, *, goal: str, task: str, tool_names: List[str]
    ) -> Analysis:
        user_tools = await get_user_tools(tool_names, self.user, self.oauth_crud)
        functions = list(map(get_tool_function, user_tools))
        prompt = analyze_task_prompt.format_prompt(
            goal=goal,
            task=task,
            language=self.settings.language,
        )

        self.token_service.calculate_max_tokens(
            self.model,
            prompt.to_string(),
            str(functions),
        )

        try:
            tools = [
                {"type": "function", "function": func}
                for func in functions
            ]
            response = await self.model.ainvoke(
                prompt.to_messages(),
                tools=tools,
            )

            completion = ""
            action = ""
            if response.additional_kwargs.get("function_call"):
                function_call = response.additional_kwargs["function_call"]
                action = function_call.get("name", "")
                completion = function_call.get("arguments", "")
            elif response.tool_calls:
                tool_call = response.tool_calls[0]
                action = tool_call.get("name", "")
                args = tool_call.get("args", "")
                completion = json.dumps(args) if isinstance(args, dict) else str(args)

            try:
                pydantic_parser = PydanticOutputParser(pydantic_object=AnalysisArguments)
                analysis_arguments = parse_with_handling(pydantic_parser, completion)
                return Analysis(
                    action=action or get_tool_name(get_default_tool()),
                    **analysis_arguments.model_dump(),
                )
            except (OpenAIError, ValidationError):
                return Analysis.get_default_analysis(task)
        except Exception as e:
            logger.error(f"Error analyzing task: {e}")
            return Analysis.get_default_analysis(task)

    async def execute_task_agent(
        self,
        *,
        goal: str,
        task: str,
        analysis: Analysis,
    ) -> FastAPIStreamingResponse:
        # TODO: More mature way of calculating max_tokens
        if self.model.max_tokens > 3000:
            self.model.max_tokens = max(self.model.max_tokens - 1000, 3000)

        tool_class = get_tool_from_name(analysis.action)
        if is_stock_market_query(task) or is_stock_market_query(goal):
            tool_class = get_tool_from_name("duckducksearch")
        return await tool_class(self.model, self.settings.language).call(
            goal,
            task,
            analysis.arg,
            self.user,
            self.oauth_crud,
        )

    async def create_tasks_agent(
        self,
        *,
        goal: str,
        tasks: List[str],
        last_task: str,
        result: str,
        completed_tasks: Optional[List[str]] = None,
    ) -> List[str]:
        prompt = ChatPromptTemplate.from_messages(
            [SystemMessagePromptTemplate(prompt=create_tasks_prompt)]
        )

        args = {
            "goal": goal,
            "language": self.settings.language,
            "tasks": "\n".join(tasks),
            "lastTask": last_task,
            "result": result,
        }

        self.token_service.calculate_max_tokens(
            self.model, prompt.format_prompt(**args).to_string()
        )

        completion = await call_model_with_handling(
            self.model, prompt, args, settings=self.settings, callbacks=self.callbacks
        )

        previous_tasks = (completed_tasks or []) + tasks
        return [completion] if completion not in previous_tasks else []

    async def summarize_task_agent(
        self,
        *,
        goal: str,
        results: List[str],
    ) -> FastAPIStreamingResponse:
        self.model.model_name = "meta/llama-3.1-8b-instruct"
        self.model.max_tokens = 16000

        snippet_max_tokens = 14000
        text_tokens = self.token_service.tokenize("".join(results))
        text = self.token_service.detokenize(text_tokens[0:snippet_max_tokens])
        logger.info(f"Summarizing text: {text}")

        return summarize(
            model=self.model,
            language=self.settings.language,
            goal=goal,
            text=text,
        )

    async def chat(
        self,
        *,
        message: str,
        results: List[str],
    ) -> FastAPIStreamingResponse:
        self.model.model_name = "meta/llama-3.1-8b-instruct"

        # 自動取得即時資訊：股市問題用 Yahoo Finance 即時行情，其餘用網頁搜尋
        search_context = ""
        try:
            if is_stock_market_query(message):
                search_result = await fetch_stock_market(query=message)
            else:
                search_result = await web_search_simple(message, max_results=5)
            if search_result:
                search_context = (
                    f"以下為即時取得的資訊（查詢：{message}）：\n"
                    f"{search_result}\n\n"
                    "請優先使用以上資訊回答。如果資訊與問題無關，請忽略它們。"
                )
        except Exception:
            logger.warning("Real-time data fetch failed in chat, continuing without it")

        if is_debate_query(message):
            return await self._run_debate(message, search_context)

        messages = [SystemMessagePromptTemplate(prompt=chat_prompt)]
        if search_context:
            messages.append(SystemMessage(content=search_context))
        messages.extend(
            HumanMessage(content=result) for result in results
        )
        messages.append(HumanMessage(content=message))

        prompt = ChatPromptTemplate.from_messages(messages)

        self.token_service.calculate_max_tokens(
            self.model,
            prompt.format_prompt(
                language=self.settings.language,
            ).to_string(),
        )

        chain: Runnable = prompt | self.model

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream({"language": self.settings.language}):
                if isinstance(chunk, str):
                    yield chunk
                elif hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        return FastAPIStreamingResponse(
            generate(),
            media_type="text/event-stream",
        )

    async def _run_debate(
        self,
        message: str,
        search_context: str,
    ) -> FastAPIStreamingResponse:
        self.model.max_tokens = 2000

        context = (
            search_context
            or "沒有提供外部即時資料。請基於你的知識回答，並明確說明資訊可能不是最新的。"
        )

        async def analyst(role: str, role_instruction: str) -> str:
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate(prompt=debate_analyst_prompt),
                    SystemMessage(content=context),
                    HumanMessage(content=message),
                ]
            )
            formatted = prompt.format_prompt(
                language=self.settings.language,
                role=role,
                role_instruction=role_instruction,
            )
            response = await self.model.ainvoke(formatted.to_messages())
            return str(response.content)

        analyses = await asyncio.gather(
            *(
                analyst(role, instruction)
                for role, instruction in DEBATE_PERSPECTIVES
            )
        )

        combined = "\n\n".join(
            f"### {role}\n{content}"
            for (role, _), content in zip(DEBATE_PERSPECTIVES, analyses)
        )

        synthesis_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate(prompt=debate_synthesis_prompt),
                SystemMessage(content=f"三位分析師的獨立分析：\n\n{combined}"),
                HumanMessage(content=message),
            ]
        )

        self.token_service.calculate_max_tokens(
            self.model,
            synthesis_prompt.format_prompt(language=self.settings.language).to_string(),
        )

        chain: Runnable = synthesis_prompt | self.model

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream({"language": self.settings.language}):
                if isinstance(chunk, str):
                    yield chunk
                elif hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        return FastAPIStreamingResponse(
            generate(),
            media_type="text/event-stream",
        )

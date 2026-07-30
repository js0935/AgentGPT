"""
Agent API 路由 — AI Agent 任務生命週期端點
==========================================

此模組定義了 Agent 的核心 API 端點，涵蓋完整的任務生命週期：

1. `/start`     — 根據目標產生初始任務列表
2. `/analyze`   — 分析任務並選擇合適工具
3. `/execute`   — 執行任務（串流回傳 LLM 回應）
4. `/create`    — 根據執行結果產生後續任務
5. `/summarize` — 彙總所有執行結果
6. `/chat`      — 對已完成的執行結果進行對話
7. `/tools`     — 列出所有可用的外部工具

所有端點皆使用 FastAPI Depends 進行依賴注入與驗證。
"""

from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from pydantic import BaseModel

from reworkd_platform.schemas.agent import (
    AgentChat,
    AgentRun,
    AgentSummarize,
    AgentTaskAnalyze,
    AgentTaskCreate,
    AgentTaskExecute,
    NewTasksResponse,
)
from reworkd_platform.web.api.agent.agent_service.agent_service import AgentService
from reworkd_platform.web.api.agent.agent_service.agent_service_provider import (
    get_agent_service,
)
from reworkd_platform.web.api.agent.analysis import Analysis
from reworkd_platform.web.api.agent.dependancies import (
    agent_analyze_validator,
    agent_chat_validator,
    agent_create_validator,
    agent_execute_validator,
    agent_start_validator,
    agent_summarize_validator,
)
from reworkd_platform.web.api.agent.tools.tools import get_external_tools, get_tool_name

router = APIRouter()


@router.post("/start")
async def start_tasks(
    req_body: AgentRun = Depends(agent_start_validator),
    agent_service: AgentService = Depends(get_agent_service(agent_start_validator)),
) -> NewTasksResponse:
    """根據使用者目標，讓 AI 產生初始任務列表。"""
    new_tasks = await agent_service.start_goal_agent(goal=req_body.goal)
    return NewTasksResponse(newTasks=new_tasks, run_id=req_body.run_id)


@router.post("/analyze")
async def analyze_tasks(
    req_body: AgentTaskAnalyze = Depends(agent_analyze_validator),
    agent_service: AgentService = Depends(get_agent_service(agent_analyze_validator)),
) -> Analysis:
    """分析特定任務，決定要使用哪些工具來執行。"""
    return await agent_service.analyze_task_agent(
        goal=req_body.goal,
        task=req_body.task or "",
        tool_names=req_body.tool_names or [],
    )


@router.post("/execute")
async def execute_tasks(
    req_body: AgentTaskExecute = Depends(agent_execute_validator),
    agent_service: AgentService = Depends(
        get_agent_service(validator=agent_execute_validator, streaming=True),
    ),
) -> FastAPIStreamingResponse:
    """
    執行指定任務，以 Server-Sent Events (SSE) 串流回傳 LLM 回應。

    使用 FastAPI 原生的 StreamingResponse，取代舊版的 lanarky。
    """
    return await agent_service.execute_task_agent(
        goal=req_body.goal or "",
        task=req_body.task or "",
        analysis=req_body.analysis,
    )


@router.post("/create")
async def create_tasks(
    req_body: AgentTaskCreate = Depends(agent_create_validator),
    agent_service: AgentService = Depends(get_agent_service(agent_create_validator)),
) -> NewTasksResponse:
    """根據執行結果與已完成任務，讓 AI 產生下一批子任務。"""
    new_tasks = await agent_service.create_tasks_agent(
        goal=req_body.goal,
        tasks=req_body.tasks or [],
        last_task=req_body.last_task or "",
        result=req_body.result or "",
        completed_tasks=req_body.completed_tasks or [],
    )
    return NewTasksResponse(newTasks=new_tasks, run_id=req_body.run_id)


@router.post("/summarize")
async def summarize(
    req_body: AgentSummarize = Depends(agent_summarize_validator),
    agent_service: AgentService = Depends(
        get_agent_service(
            validator=agent_summarize_validator,
            streaming=True,
            llm_model="meta/llama-3.1-8b-instruct",
        ),
    ),
) -> FastAPIStreamingResponse:
    """彙總所有任務的執行結果，產出一份總結報告。"""
    return await agent_service.summarize_task_agent(
        goal=req_body.goal or "",
        results=req_body.results,
    )


@router.post("/chat")
async def chat(
    req_body: AgentChat = Depends(agent_chat_validator),
    agent_service: AgentService = Depends(
        get_agent_service(
            validator=agent_chat_validator,
            streaming=True,
            llm_model="meta/llama-3.1-8b-instruct",
        ),
    ),
) -> FastAPIStreamingResponse:
    """針對已完成的執行結果進行對話式追問。"""
    return await agent_service.chat(
        message=req_body.message,
        results=req_body.results,
    )


class ToolModel(BaseModel):
    """可供 Agent 使用的外部工具描述。"""

    name: str
    description: str
    color: str
    image_url: Optional[str]


class ToolsResponse(BaseModel):
    """工具列表回應。"""

    tools: List[ToolModel]


@router.get("/tools")
async def get_user_tools() -> ToolsResponse:
    """列出所有目前可用的外部工具（如 Google 搜尋、Wikipedia 等）。"""
    tools = get_external_tools()
    formatted_tools = [
        ToolModel(
            name=get_tool_name(tool),
            description=tool.public_description,
            color="TODO: Change to image of tool",
            image_url=tool.image_url,
        )
        for tool in tools
        if tool.available()
    ]

    return ToolsResponse(tools=formatted_tools)

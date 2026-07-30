"""Agent 資料模型 — 定義 agent 執行、任務分析、模型設定等 Pydantic 結構。"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from reworkd_platform.web.api.agent.analysis import Analysis

LLM_Model = Literal[
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.1-70b-instruct",
    "mistralai/mistral-nemotron",
    "nvidia/nemotron-mini-4b-instruct",
]
Loop_Step = Literal[
    "start",
    "analyze",
    "execute",
    "create",
    "summarize",
    "chat",
]
LLM_MODEL_MAX_TOKENS: Dict[LLM_Model, int] = {
    "meta/llama-3.1-8b-instruct": 128000,
    "meta/llama-3.1-70b-instruct": 128000,
    "mistralai/mistral-nemotron": 128000,
    "nvidia/nemotron-mini-4b-instruct": 4096,
}


class ModelSettings(BaseModel):
    model: LLM_Model = Field(default="meta/llama-3.1-8b-instruct")
    custom_api_key: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=500, ge=0)
    language: str = Field(default="English")

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: float, info: Any) -> float:
        model = info.data.get("model")
        if model and v > (max_tokens := LLM_MODEL_MAX_TOKENS.get(model, 4000)):
            raise ValueError(f"Model {model} only supports {max_tokens} tokens")
        return v


class AgentRunCreate(BaseModel):
    goal: str
    model_settings: ModelSettings = Field(default=ModelSettings())


class AgentRun(AgentRunCreate):
    run_id: str


class AgentTaskAnalyze(AgentRun):
    task: str
    tool_names: List[str] = Field(default=[])
    model_settings: ModelSettings = Field(default=ModelSettings())


class AgentTaskExecute(AgentRun):
    task: str
    analysis: Analysis


class AgentTaskCreate(AgentRun):
    tasks: List[str] = Field(default=[])
    last_task: Optional[str] = Field(default=None)
    result: Optional[str] = Field(default=None)
    completed_tasks: List[str] = Field(default=[])


class AgentSummarize(AgentRun):
    results: List[str] = Field(default=[])


class AgentChat(AgentRun):
    message: str
    results: List[str] = Field(default=[])


class NewTasksResponse(BaseModel):
    run_id: str
    new_tasks: List[str] = Field(alias="newTasks")

    model_config = {"populate_by_name": True}


class RunCount(BaseModel):
    count: int
    first_run: Optional[datetime]
    last_run: Optional[datetime]

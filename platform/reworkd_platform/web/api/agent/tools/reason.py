from typing import Any, AsyncGenerator

from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from langchain_core.runnables import Runnable

from reworkd_platform.web.api.agent.tools.tool import Tool


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


class Reason(Tool):
    description = (
        "Reason about task via existing information or understanding. "
        "Make decisions / selections from options."
    )

    async def call(
        self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any
    ) -> FastAPIStreamingResponse:
        from reworkd_platform.web.api.agent.prompts import execute_task_prompt

        chain: Runnable = execute_task_prompt | self.model

        return FastAPIStreamingResponse(
            _stream_chain(
                chain, {"goal": goal, "language": self.language, "task": task}
            ),
            media_type="text/event-stream",
        )

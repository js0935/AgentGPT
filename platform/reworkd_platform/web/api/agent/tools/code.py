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


class Code(Tool):
    description = "Should only be used to write code, refactor code, fix code bugs, and explain programming concepts."
    public_description = "Write and review code."

    async def call(
        self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any
    ) -> FastAPIStreamingResponse:
        from reworkd_platform.web.api.agent.prompts import code_prompt

        chain: Runnable = code_prompt | self.model

        return FastAPIStreamingResponse(
            _stream_chain(
                chain, {"goal": goal, "language": self.language, "task": task}
            ),
            media_type="text/event-stream",
        )

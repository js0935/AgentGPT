from typing import Any, AsyncGenerator

from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.runnables import Runnable

from reworkd_platform.web.api.agent.stream_mock import stream_string
from reworkd_platform.web.api.agent.tools.tool import Tool


async def _stream_chain(
    chain: Runnable,
    inputs: dict,
) -> AsyncGenerator[str, None]:
    """Stream an LCEL chain's output chunk by chunk."""
    from reworkd_platform.web.api.agent.prompts import summarize_prompt

    # For Wikipedia, we just stream the result directly
    async for chunk in chain.astream(inputs):
        if isinstance(chunk, str):
            yield chunk
        elif hasattr(chunk, "content") and chunk.content:
            yield chunk.content


class Wikipedia(Tool):
    description = (
        "Search Wikipedia for information about historical people, companies, events, "
        "places or research. This should be used over search for broad overviews of "
        "specific nouns."
    )
    public_description = "Search Wikipedia for historical information."
    arg_description = "A simple query string of just the noun in question."
    image_url = "/tools/wikipedia.png"

    async def call(
        self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any
    ) -> FastAPIStreamingResponse:
        wikipedia_client = WikipediaAPIWrapper()
        wikipedia_search = wikipedia_client.run(input_str)
        return stream_string(wikipedia_search)

import pytest

from reworkd_platform.schemas import ModelSettings
from reworkd_platform.web.api.errors import OpenAIError


@pytest.mark.asyncio
async def test_call_model_with_handling_handles_errors():
    """Verify that call_model_with_handling properly wraps OpenAI errors."""
    from reworkd_platform.web.api.agent.helpers import call_model_with_handling
    from unittest.mock import AsyncMock

    mock_model = AsyncMock()
    mock_prompt = AsyncMock()
    # Simulate an API error
    mock_model.ainvoke.side_effect = Exception("401 Authentication error")

    with pytest.raises(OpenAIError) as exc_info:
        await call_model_with_handling(
            mock_model, mock_prompt, {"goal": "test"}, ModelSettings()
        )

    assert "Authentication error" in str(exc_info.value)

from logging import Logger
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.main import log_endpoint_start_and_end


class TestLogEndpointStartAndEnd:
    @patch.object(Logger, "info")
    @pytest.mark.asyncio
    async def test_logs_start_and_end_of_request(self, mock_logger_info: MagicMock) -> None:
        mock_call_next = AsyncMock(return_value="response")
        request = MagicMock(method="GET", url=MagicMock(path="/test"))

        response = await log_endpoint_start_and_end(request, mock_call_next)
        mock_logger_info.assert_any_call("[START] %s: %s", "GET", "/test")
        assert "[END] GET: /test finished in" in mock_logger_info.call_args_list[1][0][0]
        mock_call_next.assert_called_once_with(request)
        assert response == "response"

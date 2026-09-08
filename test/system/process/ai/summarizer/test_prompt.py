import asyncio
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

from airembr.system.config.llm_config import llm_config
from airembr.system.process.ai.summarizer.model.summary_output import SummaryOutput
from airembr.system.process.ai.summarizer.prompt import get_summary


class TestGetSummary(unittest.TestCase):

    def setUp(self):
        self._orig_token = llm_config.llm_token
        self._orig_provider = llm_config.llm_provider
        self._orig_model = llm_config.llm_model

    def tearDown(self):
        llm_config.llm_token = self._orig_token
        llm_config.llm_provider = self._orig_provider
        llm_config.llm_model = self._orig_model

    def test_returns_none_when_token_missing(self):
        llm_config.llm_token = None
        llm_config.llm_provider = 'openrouter'
        llm_config.llm_model = 'google/gemini-2.5-flash-lite'

        result = asyncio.run(get_summary("some text"))

        self.assertIsNone(result)

    def test_returns_none_when_provider_missing(self):
        llm_config.llm_token = 'sk-or-v1-fake'
        llm_config.llm_provider = None
        llm_config.llm_model = 'google/gemini-2.5-flash-lite'

        result = asyncio.run(get_summary("some text"))

        self.assertIsNone(result)

    def test_returns_none_for_unsupported_provider(self):
        llm_config.llm_token = 'sk-or-v1-fake'
        llm_config.llm_provider = 'openai'
        llm_config.llm_model = 'gpt-5-nano'

        result = asyncio.run(get_summary("some text"))

        self.assertIsNone(result)

    @patch("pydantic_ai.Agent.run", new_callable=AsyncMock)
    def test_get_summary_returns_agent_output(self, mock_run):
        llm_config.llm_token = 'sk-or-v1-fake'
        llm_config.llm_provider = 'openrouter'
        llm_config.llm_model = 'google/gemini-2.5-flash-lite'

        expected_output = SummaryOutput(summaries=["fact one", "fact two"], topics=["billing"])
        mock_run.return_value = MagicMock(output=expected_output)

        result = asyncio.run(get_summary("conversation text"))

        mock_run.assert_awaited_once()
        self.assertIs(result, expected_output)
        self.assertEqual(result.summaries, ["fact one", "fact two"])
        self.assertEqual(result.topics, ["billing"])


if __name__ == '__main__':
    unittest.main()

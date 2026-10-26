"""Errors of the AI calls of `modules/phones` and `modules/rag` left after the retries: the endpoint returns 503.

The clients and the retries: docs/ai/RAG.md#errors-and-retries.
"""

import httpx
import openai
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

AI_ERRORS = (openai.OpenAIError, httpx.HTTPError, ValidationError, OutputParserException)

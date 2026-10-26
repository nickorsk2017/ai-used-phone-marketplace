"""LangChain clients and the structured LLM call shared by the modules. The settings belong to the calling module."""

from collections.abc import Callable

from langchain_core.embeddings import Embeddings
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, SecretStr, ValidationError

# Network and provider errors: the built-in retry of the client, docs/ai/RAG.md#errors-and-retries.
CLIENT_MAX_RETRIES = 2

# One repeated call on an invalid LLM response: docs/ai/RAG.md#errors-and-retries.
LLM_VALIDATION_ATTEMPTS = 2
INVALID_LLM_OUTPUT = (ValidationError, OutputParserException)


def chat_model(api_key: str, model: str) -> BaseChatModel:
    return ChatOpenAI(model=model, api_key=SecretStr(api_key), max_retries=CLIENT_MAX_RETRIES)


def embeddings(api_key: str, model: str) -> Embeddings:
    return OpenAIEmbeddings(model=model, api_key=SecretStr(api_key), max_retries=CLIENT_MAX_RETRIES)


async def llm_call[Output](
    chat_model: BaseChatModel,
    schema: type[BaseModel],
    system: str,
    user: str,
    convert: Callable[[BaseModel], Output],
) -> Output:
    """Structured LLM call. Network errors are retried by the client, invalid output is repeated here once."""
    structured = chat_model.with_structured_output(schema)

    messages = [SystemMessage(system), HumanMessage(user)]
    for attempt in range(1, LLM_VALIDATION_ATTEMPTS + 1):
        try:
            return convert(await structured.ainvoke(messages))
        except INVALID_LLM_OUTPUT:
            if attempt == LLM_VALIDATION_ATTEMPTS:
                raise
    raise AssertionError("unreachable: the last attempt returns or raises")

"""LLM calls of `modules/phones`. The chat models are created from the settings of the module.

They return Pydantic schemas, never ORM objects.
"""

from functools import lru_cache

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from core.llm import chat_model, llm_call
from modules.phones.config import get_settings
from modules.phones.prompts.description import DESCRIPTION_SYSTEM, model_message
from modules.phones.prompts.guardrail import GUARDRAIL_SYSTEM, listing_message
from modules.phones.schemas import GeneratedDescription, GuardrailVerdict, PhoneCreate, PhoneDescription
from modules.phones.services.guardrails import has_violations


@lru_cache
def get_description_model() -> BaseChatModel:
    settings = get_settings()
    return chat_model(settings.openai_api_key, settings.description_model)


@lru_cache
def get_guardrail_model() -> BaseChatModel:
    settings = get_settings()
    return chat_model(settings.openai_api_key, settings.guardrail_model)


def _to_description(output: BaseModel) -> PhoneDescription | None:
    generated = GeneratedDescription.model_validate(output, from_attributes=True)
    if not generated.model_found:
        return None
    return PhoneDescription.model_validate(generated.model_dump(exclude={"model_found"}))


async def generate_description(model_name: str) -> PhoneDescription | None:
    """Description and model data by the model name. `None` when the model does not exist."""
    return await llm_call(
        get_description_model(),
        GeneratedDescription,
        DESCRIPTION_SYSTEM,
        model_message(model_name),
        _to_description,
    )


def _to_allowed(output: BaseModel) -> bool:
    return GuardrailVerdict.model_validate(output, from_attributes=True).allowed


async def check_listing(data: PhoneCreate) -> bool:
    """Guardrail 1: Backend Regex, then the LLM Guardrail for clean text only.

    `False` blocks the listing. Provider errors are raised: the caller does not save the listing (fail closed).
    """
    if has_violations(data.model_name, data.description, data.condition_note):
        return False
    message = listing_message(data.model_code, data.model_name, data.description, data.condition_note)
    return await llm_call(get_guardrail_model(), GuardrailVerdict, GUARDRAIL_SYSTEM, message, _to_allowed)

"""`modules/phones` service: description generation, Guardrail 1, listings. LLM clients are stubs."""

import uuid

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from conftest import AiStubs, StubChatModel
from modules.phones import services as phones_service
from modules.phones.prompts.description import MODEL_DELIMITER
from modules.phones.prompts.guardrail import LISTING_DELIMITER
from modules.phones.schemas import GeneratedDescription, GuardrailVerdict, PhoneCreate, PhoneDescription

FOUND = GeneratedDescription(
    model_found=True,
    model_code="A2483",
    model_name="iPhone 13 Pro",
    os="ios",
    camera_megapixels=12,
    battery_capacity=3095,
    display_size=6.1,
    description="iPhone 13 Pro with a 6.1-inch ProMotion display and A15 Bionic chip.",
)
NOT_FOUND = GeneratedDescription(model_found=False)
INVALID = GeneratedDescription(model_found=True, model_code="A2483")

LISTING = PhoneCreate(
    model_code="A2483",
    model_name="iPhone 13 Pro",
    os="ios",
    camera_megapixels=12,
    battery_capacity=3095,
    display_size=6.1,
    description="iPhone 13 Pro with a 6.1-inch display.",
    condition="average",
    condition_note="Small scratches on the frame",
    price=450,
)


async def describe(ai_stubs: AiStubs, chat_model: StubChatModel, model_name: str) -> PhoneDescription | None:
    ai_stubs.description = chat_model
    return await phones_service.generate_description(model_name)


async def check(ai_stubs: AiStubs, chat_model: StubChatModel, data: PhoneCreate) -> bool:
    ai_stubs.guardrail = chat_model
    return await phones_service.check_listing(data)


async def test_description_found(ai_stubs: AiStubs) -> None:
    chat_model = StubChatModel(FOUND)
    description = await describe(ai_stubs, chat_model, "iphone 13 pro")
    assert description is not None
    assert description.model_code == "A2483"
    assert description.os == "ios"
    assert MODEL_DELIMITER in chat_model.messages[-1].content


async def test_description_not_found(ai_stubs: AiStubs) -> None:
    assert await describe(ai_stubs, StubChatModel(NOT_FOUND), "iPhone 25") is None


async def test_invalid_description_is_repeated_once(ai_stubs: AiStubs) -> None:
    chat_model = StubChatModel(INVALID, FOUND)
    assert await describe(ai_stubs, chat_model, "iPhone 13 Pro") is not None
    assert chat_model.calls == 2


async def test_invalid_description_twice_raises(ai_stubs: AiStubs) -> None:
    chat_model = StubChatModel(INVALID, INVALID, FOUND)
    with pytest.raises(ValidationError):
        await describe(ai_stubs, chat_model, "iPhone 13 Pro")
    assert chat_model.calls == 2


async def test_regex_blocks_before_the_llm(ai_stubs: AiStubs) -> None:
    chat_model = StubChatModel(GuardrailVerdict(allowed=True))
    data = LISTING.model_copy(update={"condition_note": "Call +1 415 555 2671"})
    assert await check(ai_stubs, chat_model, data) is False
    assert chat_model.calls == 0


@pytest.mark.parametrize(
    ("verdict", "allowed"),
    [
        (GuardrailVerdict(allowed=True), True),
        (GuardrailVerdict(allowed=False, category="toxic"), False),
        (GuardrailVerdict(allowed=False, category="fraud"), False),
        (GuardrailVerdict(allowed=False, category="prompt_injection"), False),
    ],
)
async def test_llm_guardrail(verdict: GuardrailVerdict, allowed: bool, ai_stubs: AiStubs) -> None:
    chat_model = StubChatModel(verdict)
    assert await check(ai_stubs, chat_model, LISTING) is allowed
    content = chat_model.messages[-1].content
    assert content.startswith(LISTING_DELIMITER)
    assert LISTING.condition_note in content


async def test_llm_guardrail_error_is_raised(ai_stubs: AiStubs) -> None:
    with pytest.raises(RuntimeError):
        await check(ai_stubs, StubChatModel(RuntimeError("provider down")), LISTING)


async def test_create_and_list_newest_first(session: AsyncSession) -> None:
    owner, other = uuid.uuid4(), uuid.uuid4()
    first = await phones_service.create_phone(session, owner, LISTING)
    await phones_service.create_phone(session, other, LISTING)
    assert first.id.version == 4
    assert first.display_size == 6.1
    assert [phone.id for phone in await phones_service.list_user_phones(session, owner)] == [first.id]


def test_create_schema_rejects_client_fields() -> None:
    with pytest.raises(ValidationError):
        PhoneCreate.model_validate({**LISTING.model_dump(), "user_id": str(uuid.uuid4())})


@pytest.mark.parametrize("field", ["price", "camera_megapixels", "battery_capacity", "display_size"])
def test_create_schema_requires_positive_numbers(field: str) -> None:
    with pytest.raises(ValidationError):
        PhoneCreate.model_validate({**LISTING.model_dump(), field: 0})


def test_model_code_is_converted_to_uppercase() -> None:
    assert PhoneCreate.model_validate({**LISTING.model_dump(), "model_code": " sm-s911u "}).model_code == "SM-S911U"


@pytest.mark.parametrize("model_code", ["A", "A2483 PRO", "A_2483", "http://x.com", "A" * 33])
def test_model_code_format(model_code: str) -> None:
    with pytest.raises(ValidationError):
        PhoneCreate.model_validate({**LISTING.model_dump(), "model_code": model_code})


async def test_regex_checks_the_model_code(ai_stubs: AiStubs) -> None:
    chat_model = StubChatModel(GuardrailVerdict(allowed=True))
    data = LISTING.model_copy(update={"model_code": "4155552671"})
    assert await check(ai_stubs, chat_model, data) is False
    assert chat_model.calls == 0


async def test_llm_guardrail_message_contains_the_model_code(ai_stubs: AiStubs) -> None:
    chat_model = StubChatModel(GuardrailVerdict(allowed=True))
    await check(ai_stubs, chat_model, LISTING)
    assert "Model code: A2483" in chat_model.messages[-1].content


async def test_get_phone_and_owner(session: AsyncSession) -> None:
    owner = uuid.uuid4()
    phone = await phones_service.create_phone(session, owner, LISTING)
    assert await phones_service.get_phone(session, phone.id) == phone
    assert await phones_service.get_phone_owner_id(session, phone.id) == owner
    unknown = uuid.uuid4()
    assert await phones_service.get_phone(session, unknown) is None
    assert await phones_service.get_phone_owner_id(session, unknown) is None

"""Root runs of `modules/phones` in LangSmith: docs/ai/EVALUATION.md#tracing. Runs are captured, never sent."""

import pytest
from langsmith import tracing_context

from conftest import StubChatModel, TraceCapture
from modules.phones import services as phones_service
from modules.phones.schemas import GeneratedDescription, GuardrailVerdict, PhoneCreate
from modules.phones.services import ai as phones_ai

DESCRIPTION = GeneratedDescription(
    model_found=True,
    model_code="A2172",
    model_name="iPhone 12",
    os="ios",
    camera_megapixels=12,
    battery_capacity=2815,
    display_size=6.1,
    description="iPhone 12 was released in 2020.",
)


async def test_description_is_the_root_run_phones_description(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(phones_ai, "get_description_model", lambda: StubChatModel(DESCRIPTION))
    capture = TraceCapture()
    with tracing_context(enabled=True, client=capture):
        await phones_service.generate_description("iPhone 12")
    run = capture.run("phones.description")
    assert run["tags"] == ["phones"]
    assert run.get("parent_run_id") is None


async def test_guardrail_is_the_root_run_phones_guardrail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(phones_ai, "get_guardrail_model", lambda: StubChatModel(GuardrailVerdict(allowed=True)))
    capture = TraceCapture()
    phone = PhoneCreate(
        **DESCRIPTION.model_dump(exclude={"model_found"}), condition="average", condition_note="Scratches", price=175
    )
    with tracing_context(enabled=True, client=capture):
        assert await phones_service.check_listing(phone) is True
    assert capture.run("phones.guardrail")["tags"] == ["phones"]


async def test_no_runs_when_tracing_is_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(phones_ai, "get_description_model", lambda: StubChatModel(DESCRIPTION))
    capture = TraceCapture()
    with tracing_context(enabled=False, client=capture):
        await phones_service.generate_description("iPhone 12")
    assert capture.captured == {}

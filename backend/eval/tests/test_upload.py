"""Upload of the cases: docs/ai/EVALUATION.md#datasets. The repository replaces changed examples only."""

import uuid
from dataclasses import dataclass, field
from types import SimpleNamespace

import conftest  # noqa: F401  # test environment: no traces, stub keys
from eval.schemas import EvalDataset, Example
from eval.upload import dataset_name, upload


@dataclass
class FakeClient:
    """In-memory LangSmith datasets: `has_dataset`, `create_dataset`, `list_examples`, `delete/create_examples`."""

    datasets: dict[str, list] = field(default_factory=dict)
    deleted: list = field(default_factory=list)
    created: int = 0

    def has_dataset(self, *, dataset_name: str) -> bool:
        return dataset_name in self.datasets

    def create_dataset(self, name: str, description: str) -> None:
        self.datasets[name] = []

    def list_examples(self, *, dataset_name: str) -> list:
        return list(self.datasets[dataset_name])

    def delete_examples(self, ids: list) -> None:
        self.deleted.extend(ids)
        for name, examples in self.datasets.items():
            self.datasets[name] = [example for example in examples if example.id not in ids]

    def create_examples(self, *, dataset_name: str, examples: list[dict]) -> None:
        self.created += len(examples)
        self.datasets[dataset_name].extend(
            SimpleNamespace(id=uuid.uuid4(), inputs=e["inputs"], outputs=e["outputs"]) for e in examples
        )


async def target(inputs: dict) -> dict:
    return inputs


def dataset(*prompts: str) -> EvalDataset:
    examples = [Example(inputs={"prompt": prompt}, outputs={"clarification": True}) for prompt in prompts]
    return EvalDataset(name="rag.clarification", examples=examples, target=target, metrics=[])


def test_dataset_name_has_the_project_prefix() -> None:
    assert dataset_name("sme", dataset("a")) == "sme.rag.clarification"


def test_new_dataset_is_created_with_the_cases() -> None:
    client = FakeClient()
    assert upload(client, "sme", dataset("a", "b")) == "sme.rag.clarification"
    assert [example.inputs["prompt"] for example in client.datasets["sme.rag.clarification"]] == ["a", "b"]


def test_unchanged_cases_are_not_uploaded_again() -> None:
    client = FakeClient()
    upload(client, "sme", dataset("a", "b"))
    upload(client, "sme", dataset("b", "a"))
    assert client.created == 2
    assert client.deleted == []


def test_changed_cases_replace_the_examples() -> None:
    client = FakeClient()
    upload(client, "sme", dataset("a", "b"))
    upload(client, "sme", dataset("a", "c"))
    assert sorted(example.inputs["prompt"] for example in client.datasets["sme.rag.clarification"]) == ["a", "c"]
    assert len(client.deleted) == 2

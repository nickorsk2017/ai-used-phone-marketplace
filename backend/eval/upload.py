"""Upload of the cases to LangSmith: docs/ai/EVALUATION.md#datasets.

The repository is the source of truth. A changed set of cases replaces the examples of the dataset; the dataset
and its experiments are kept.
"""

import json

from langsmith import Client

from eval.schemas import EvalDataset, Example


def dataset_name(project: str, dataset: EvalDataset) -> str:
    return f"{project}.{dataset.name}"


def _canonical(examples: list[Example]) -> list[str]:
    return sorted(json.dumps({"inputs": e.inputs, "outputs": e.outputs}, sort_keys=True) for e in examples)


def upload(client: Client, project: str, dataset: EvalDataset) -> str:
    """Create the dataset or replace its examples when the cases changed. Returns the LangSmith dataset name."""
    name = dataset_name(project, dataset)
    if not client.has_dataset(dataset_name=name):
        client.create_dataset(name, description=f"docs/ai/EVALUATION.md#datasets: {dataset.name}")
    stored = list(client.list_examples(dataset_name=name))
    current = [Example(inputs=example.inputs, outputs=example.outputs or {}) for example in stored]
    if _canonical(current) == _canonical(dataset.examples):
        return name
    if stored:
        client.delete_examples([example.id for example in stored])
    client.create_examples(
        dataset_name=name,
        examples=[{"inputs": example.inputs, "outputs": example.outputs} for example in dataset.examples],
    )
    return name

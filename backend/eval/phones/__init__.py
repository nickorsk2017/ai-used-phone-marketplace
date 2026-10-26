"""Evaluated steps of `modules/phones`, in the run order of `make eval`."""

from eval.phones import description, hallucinated_models
from eval.schemas import EvalDataset

DATASETS: list[EvalDataset] = [description.DATASET, hallucinated_models.DATASET]

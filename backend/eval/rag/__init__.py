"""Evaluated steps of `modules/rag`, in the run order of `make eval`."""

from eval.rag import clarification, parse, search
from eval.schemas import EvalDataset

DATASETS: list[EvalDataset] = [parse.DATASET, clarification.DATASET, search.DATASET]

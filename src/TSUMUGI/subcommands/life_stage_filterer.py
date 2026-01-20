from collections.abc import Generator
from pathlib import Path

from TSUMUGI import io_handler


def _filter_annotations_by_life_stage(
    pairwise_similarity_annotations: list[dict[str, str | dict[str, dict] | dict[str | int]]],
    life_stage: str = "",
    keep: bool = False,
    drop: bool = False,
) -> Generator[frozenset[str], dict[str, dict, int]]:
    for pairwise_similarity_annotation in pairwise_similarity_annotations:
        phenotype_shared_annotations = pairwise_similarity_annotation["phenotype_shared_annotations"]

        if len(phenotype_shared_annotations) == 0:
            continue

        phenotype_shared_annotations_filtered = {}
        for term_name, annotation in phenotype_shared_annotations.items():
            if annotation["life_stage"] == life_stage and keep:
                phenotype_shared_annotations_filtered[term_name] = annotation
            if annotation["life_stage"] != life_stage and drop:
                phenotype_shared_annotations_filtered[term_name] = annotation

        if len(phenotype_shared_annotations_filtered) == 0:
            continue

        pairwise_similarity_annotation["phenotype_shared_annotations"] = phenotype_shared_annotations_filtered

        yield pairwise_similarity_annotation


def filter_annotations_by_life_stage(
    path_pairwise_similarity_annotations: str | Path,
    life_stage: str,
    keep: bool = False,
    drop: bool = False,
) -> None:
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in _filter_annotations_by_life_stage(
        pairwise_similarity_annotations=pairwise_similarity_annotations,
        life_stage=life_stage,
        keep=keep,
        drop=drop,
    ):
        # output to stdout as JSONL
        io_handler.write_jsonl_to_stdout(record)

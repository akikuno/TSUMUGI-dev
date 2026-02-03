from collections.abc import Generator, Iterator
from pathlib import Path

from TSUMUGI import io_handler


def _filter_annotations_by_life_stage(
    pairwise_similarity_annotations: Iterator[dict[str, str | int | list[dict[str, str]]]],
    life_stage: str = "",
    keep: bool = False,
    drop: bool = False,
) -> Generator[dict[str, str | int | list[dict[str, str]]], None, None]:
    for pairwise_similarity_annotation in pairwise_similarity_annotations:
        phenotype_shared_annotations = pairwise_similarity_annotation["phenotype_shared_annotations"]

        if len(phenotype_shared_annotations) == 0:
            continue

        phenotype_shared_annotations_filtered = []
        for annotation in phenotype_shared_annotations:
            if annotation["life_stage"] == life_stage and keep:
                phenotype_shared_annotations_filtered.append(annotation)
            if annotation["life_stage"] != life_stage and drop:
                phenotype_shared_annotations_filtered.append(annotation)

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

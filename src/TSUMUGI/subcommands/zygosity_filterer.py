from collections.abc import Generator, Iterator
from pathlib import Path

from TSUMUGI import io_handler


def _filter_annotations_by_zygosity(
    pairwise_similarity_annotations: Iterator[dict[str, str | int | list[dict[str, str]]]],
    zygosity: str = "Homo",
    keep: bool = False,
    drop: bool = False,
) -> Generator[dict[str, str | int | list[dict[str, str]]], None, None]:
    for pairwise_similarity_annotation in pairwise_similarity_annotations:
        phenotype_shared_annotations = pairwise_similarity_annotation["phenotype_shared_annotations"]

        if len(phenotype_shared_annotations) == 0:
            continue

        phenotype_shared_annotations_filtered = []
        for annotation in phenotype_shared_annotations:
            if annotation["zygosity"] == zygosity and keep:
                phenotype_shared_annotations_filtered.append(annotation)
            if annotation["zygosity"] != zygosity and drop:
                phenotype_shared_annotations_filtered.append(annotation)

        if len(phenotype_shared_annotations_filtered) == 0:
            continue

        pairwise_similarity_annotation["phenotype_shared_annotations"] = phenotype_shared_annotations_filtered

        yield pairwise_similarity_annotation


def filter_annotations_by_zygosity(
    path_pairwise_similarity_annotations: str | Path,
    zygosity: str,
    keep: bool = False,
    drop: bool = False,
) -> None:
    pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
    for record in _filter_annotations_by_zygosity(
        pairwise_similarity_annotations=pairwise_similarity_annotations,
        zygosity=zygosity,
        keep=keep,
        drop=drop,
    ):
        # output to stdout as JSONL
        io_handler.write_jsonl_to_stdout(record)

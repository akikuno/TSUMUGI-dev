from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

import numpy as np

from TSUMUGI import io_handler, ontology_handler

# Levels of biological organisation, ordered from the cell to the whole organism.
PHENOTYPE_LEVELS = ("cell", "structure", "function", "organism", "other")
ORGANISM_ROOT_NAMES = (
    "mortality/aging",
    "behavior/neurological phenotype",
    "abnormal postnatal growth/weight/body size",
    "abnormal prenatal growth/weight/body size",
    "abnormal fertility/fecundity",
)
CELL_ROOT_NAME = "cellular phenotype"
HOMEOSTASIS_ROOT_NAME = "homeostasis/metabolism phenotype"


def classify_mp_term_levels(ontology_terms: dict[str, dict]) -> dict[str, str]:
    """Assign each MP term to one level of biological organisation.

    Priority: organism (survival, behavior, body growth, fertility) > cell (cellular phenotype) >
    structure (an ancestor named "... morphology") > function (an ancestor named "... physiology" or
    homeostasis/metabolism) > other.
    """
    parent_term_map, _ = ontology_handler.build_term_hierarchy(ontology_terms)
    names = {term_id: term.get("name", "") for term_id, term in ontology_terms.items()}
    ids_by_name = {name: term_id for term_id, name in names.items()}
    organism_roots = {ids_by_name[name] for name in ORGANISM_ROOT_NAMES if name in ids_by_name}
    cell_root = ids_by_name.get(CELL_ROOT_NAME)
    homeostasis_root = ids_by_name.get(HOMEOSTASIS_ROOT_NAME)

    levels: dict[str, str] = {}
    for term_id in ontology_terms:
        lineage = ontology_handler.find_all_ancestor_terms(term_id, parent_term_map) | {term_id}
        lineage_names = [names.get(ancestor, "") for ancestor in lineage]
        if lineage & organism_roots:
            levels[term_id] = "organism"
        elif cell_root in lineage:
            levels[term_id] = "cell"
        elif any(name.endswith("morphology") for name in lineage_names):
            levels[term_id] = "structure"
        elif homeostasis_root in lineage or any(name.endswith("physiology") for name in lineage_names):
            levels[term_id] = "function"
        else:
            levels[term_id] = "other"
    return levels


def read_gene_sets(path_gene_sets: str | Path) -> dict[str, list[str]]:
    """Read gene sets in GMT format (name, description, gene symbols; tab-separated)."""
    gene_sets: dict[str, list[str]] = {}
    with open(path_gene_sets, encoding="utf-8") as f:
        for line in f:
            fields = [field.strip() for field in line.rstrip("\n").split("\t")]
            if len(fields) < 3 or not fields[0]:
                continue
            gene_sets[fields[0]] = sorted({gene for gene in fields[2:] if gene})
    if not gene_sets:
        raise ValueError(f"No gene set was found in {path_gene_sets}. Expected GMT: name<TAB>description<TAB>genes.")
    return gene_sets


def _collect_similarities(
    pairwise_similarity_annotations,
    member_index: dict[str, int],
    query_genes: set[str] | None,
) -> tuple[dict[str, np.ndarray], set[str], dict[tuple[str, str], list[dict]]]:
    """Collect similarity scores between query genes and gene-set members in one pass."""
    rows: dict[str, np.ndarray] = {}
    observed_genes: set[str] = set()
    shared_annotations: dict[tuple[str, str], list[dict]] = {}
    keep_shared_annotations = query_genes is not None

    for record in pairwise_similarity_annotations:
        gene1, gene2 = record["gene1_symbol"], record["gene2_symbol"]
        observed_genes.add(gene1)
        observed_genes.add(gene2)
        score = float(record.get("phenotype_similarity_score", 0))
        for query, member in ((gene1, gene2), (gene2, gene1)):
            if member not in member_index or (query_genes is not None and query not in query_genes):
                continue
            if query not in rows:
                rows[query] = np.zeros(len(member_index), dtype=np.float32)
            rows[query][member_index[member]] = score
            if keep_shared_annotations and score > 0:
                shared_annotations[(query, member)] = record.get("phenotype_shared_annotations", [])
    return rows, observed_genes, shared_annotations


def _summarize_shared_phenotypes(
    query: str,
    members: list[str],
    shared_annotations: dict[tuple[str, str], list[dict]],
    term_levels: dict[str, str],
) -> list[dict[str, str | int]]:
    """Count the members sharing each phenotype with the query and order phenotypes from cell to organism."""
    supporting_members: Counter = Counter()
    term_names: dict[str, str] = {}
    for member in members:
        for annotation in shared_annotations.get((query, member), []):
            term_id = annotation.get("mp_term_id") or annotation.get("mp_term_name")
            term_names[term_id] = annotation.get("mp_term_name", term_id)
            supporting_members[term_id] += 1
    summary = [
        {
            "mp_term_id": term_id,
            "mp_term_name": term_names[term_id],
            "level": term_levels.get(term_id, "other"),
            "supporting_members": count,
        }
        for term_id, count in supporting_members.items()
    ]
    summary.sort(
        key=lambda item: (PHENOTYPE_LEVELS.index(item["level"]), -item["supporting_members"], item["mp_term_name"])
    )
    return summary


def rank_gene_sets(
    pairwise_similarity_annotations,
    gene_sets: dict[str, list[str]],
    query_genes: set[str] | None = None,
    term_levels: dict[str, str] | None = None,
    top_members: int = 3,
    max_sets: int = 5,
):
    """Yield, for each query gene, the gene sets whose members have the most similar phenotypes.

    The assignment score of a gene for a gene set is the mean of the `top_members` largest phenotype
    similarity scores between the gene and the members of the set (the gene itself is excluded).
    Gene sets with fewer than `top_members` other members in the pairwise data are not candidates.
    """
    member_index = {gene: i for i, gene in enumerate(sorted({gene for genes in gene_sets.values() for gene in genes}))}
    rows, observed_genes, shared_annotations = _collect_similarities(
        pairwise_similarity_annotations, member_index, query_genes
    )

    observed_members = {name: [gene for gene in genes if gene in observed_genes] for name, genes in gene_sets.items()}
    member_positions = {
        name: np.array([member_index[gene] for gene in genes], dtype=np.int64)
        for name, genes in observed_members.items()
    }
    member_sets = {name: set(genes) for name, genes in observed_members.items()}

    targets = sorted(query_genes) if query_genes is not None else sorted(observed_genes)
    missing = [gene for gene in targets if gene not in observed_genes]
    if missing:
        logging.warning(f"{len(missing)} query genes are absent from the pairwise annotations: {missing[:10]}")

    for query in targets:
        if query not in observed_genes:
            continue
        row = rows.get(query)
        if row is None:
            row = np.zeros(len(member_index), dtype=np.float32)
        candidates = []
        for name, positions in member_positions.items():
            is_member = query in member_sets[name]
            if len(positions) - int(is_member) < top_members:
                continue
            # A gene has no pair record with itself, so its own entry is 0 and never inflates the score.
            values = row[positions]
            top_values = np.sort(values)[-top_members:]
            candidates.append((float(top_values.mean()), name, is_member))
        candidates.sort(key=lambda item: (-item[0], item[1]))

        for rank, (score, name, is_member) in enumerate(candidates[:max_sets], start=1):
            if score <= 0:
                break
            members = [gene for gene in observed_members[name] if gene != query]
            nearest = sorted(members, key=lambda gene: (-float(row[member_index[gene]]), gene))[:top_members]
            record = {
                "gene_symbol": query,
                "gene_set": name,
                "rank": rank,
                "candidate_gene_sets": len(candidates),
                "assignment_score": round(score, 6),
                "gene_set_size": len(members),
                "is_member": is_member,
                "nearest_members": [
                    {"gene_symbol": gene, "phenotype_similarity_score": round(float(row[member_index[gene]]), 6)}
                    for gene in nearest
                ],
            }
            if query_genes is not None:
                record["shared_phenotypes"] = _summarize_shared_phenotypes(
                    query, members, shared_annotations, term_levels or {}
                )
            yield record


def assign_genes_to_gene_sets(
    path_pairwise_similarity_annotations: str | Path | None,
    path_gene_sets: str | Path,
    path_genes: str | Path | None = None,
    path_obo: str | Path | None = None,
    top_members: int = 3,
    max_sets: int = 5,
) -> None:
    """Rank user-provided gene sets for each gene by phenotype similarity and write JSONL to STDOUT."""
    gene_sets = read_gene_sets(path_gene_sets)
    query_genes = None
    if path_genes is not None:
        query_genes = {line.strip() for line in Path(path_genes).read_text(encoding="utf-8").splitlines()}
        query_genes.discard("")
        if not query_genes:
            raise ValueError(f"Gene list is empty: {path_genes}")
    term_levels = classify_mp_term_levels(io_handler.parse_obo_file(path_obo)) if path_obo else {}

    records = rank_gene_sets(
        io_handler.read_jsonl(path_pairwise_similarity_annotations),
        gene_sets,
        query_genes=query_genes,
        term_levels=term_levels,
        top_members=top_members,
        max_sets=max_sets,
    )
    for record in records:
        io_handler.write_jsonl_to_stdout(record)

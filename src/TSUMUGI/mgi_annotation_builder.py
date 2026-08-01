from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

GENE_PHENO_COLUMNS = (
    "allelic_composition",
    "allele_symbols",
    "allele_ids",
    "background_raw",
    "mp_id",
    "pubmed_ids",
    "marker_ids",
    "genotype_id",
)

PHENOTYPIC_ALLELE_COLUMNS = (
    "allele_id",
    "allele_symbol",
    "allele_name",
    "allele_type",
    "allele_attribute",
    "original_reference_pubmed_ids",
    "marker_id",
    "gene_symbol",
    "refseq_id",
    "ensembl_gene_id",
    "high_level_mp_ids",
    "synonyms",
    "marker_name",
)

ALLOWED_ALLELE_TYPES = {
    "Targeted",
    "Endonuclease-mediated",
    "Gene trapped",
}
REQUIRED_NULL_ATTRIBUTE = "Null/knockout"
PRIMARY_GENOTYPE_STATES = {
    "homozygous",
    "compound_heterozygous",
    "hemizygous",
}
NORMAL_PHENOTYPE_ROOT = "MP:0002873"
ROOT_MP_TERM_ID = "MP:0000001"

EMBRYO_ASSAYS = {
    "E9.5",
    "E10.5",
    "E12.5",
    "Embryo LacZ",
    "E14.5",
    "E14.5-E15.5",
    "E18.5",
}
EMBRYO_PATTERN = re.compile("|".join(map(re.escape, sorted(EMBRYO_ASSAYS))))

SEX_COLUMNS = {
    "Genotype ID",
    "Sex",
    "MP ID",
    "MP Term",
    "Allelic Composition",
    "Background Strain",
    "Sex-specific Normal Y/N",
    "Citation (PubMed/MGI)",
}

STRAIN_FAMILY_PATTERNS = (
    (
        "C57BL/6",
        re.compile(
            r"(?:C57BL/6|(?<![A-Z0-9])B6(?:J|N)?(?=[.(\-*/\s]|$))",
            re.IGNORECASE,
        ),
    ),
    ("C57BL/10", re.compile(r"C57BL/10", re.IGNORECASE)),
    ("129", re.compile(r"(?<![A-Z0-9])129(?:[A-Z0-9/]*)", re.IGNORECASE)),
    ("BALB/c", re.compile(r"BALB(?:/c)?", re.IGNORECASE)),
    ("C3H", re.compile(r"(?<![A-Z0-9])C3H(?:[A-Z0-9/]*)", re.IGNORECASE)),
    ("CBA", re.compile(r"(?<![A-Z0-9])CBA(?:[A-Z0-9/]*)", re.IGNORECASE)),
    ("DBA", re.compile(r"(?<![A-Z0-9])DBA(?:/[12])?", re.IGNORECASE)),
    ("FVB", re.compile(r"(?<![A-Z0-9])FVB(?:/N)?", re.IGNORECASE)),
    ("NOD", re.compile(r"(?<![A-Z0-9])NOD(?:[A-Z0-9/]*)", re.IGNORECASE)),
    ("SJL", re.compile(r"(?<![A-Z0-9])SJL(?:[A-Z0-9/]*)", re.IGNORECASE)),
    ("AKR", re.compile(r"(?<![A-Z0-9])AKR(?:[A-Z0-9/]*)", re.IGNORECASE)),
    ("A/J", re.compile(r"(?<![A-Z0-9])A/J(?![A-Z0-9])", re.IGNORECASE)),
    ("CAST/Ei", re.compile(r"CAST/Ei", re.IGNORECASE)),
    ("PWK", re.compile(r"(?<![A-Z0-9])PWK(?:/PhJ)?", re.IGNORECASE)),
    ("CD-1", re.compile(r"(?:CD-?1|Crl:CD1)", re.IGNORECASE)),
    ("ICR", re.compile(r"(?<![A-Z0-9])ICR(?![A-Z0-9])", re.IGNORECASE)),
    ("Swiss", re.compile(r"(?:Black\s+Swiss|Swiss)", re.IGNORECASE)),
    ("NMRI", re.compile(r"(?<![A-Z0-9])NMRI(?![A-Z0-9])", re.IGNORECASE)),
    ("MF1", re.compile(r"(?<![A-Z0-9])MF1(?![A-Z0-9])", re.IGNORECASE)),
)


def split_tokens(value: object) -> list[str]:
    """Split a pipe-delimited MGI field into stable non-empty tokens."""
    if value is None:
        return []
    return [token.strip() for token in str(value).split("|") if token.strip()]


def join_unique(values: Iterable[object], separator: str = "|") -> str:
    """Join distinct non-empty values in lexical order."""
    return separator.join(sorted({str(value).strip() for value in values if str(value).strip()}))


def normalize_background(value: object) -> str:
    """Normalize whitespace without changing the reported background meaning."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def normalize_strain(value: object) -> tuple[str | None, str]:
    """Extract stable coarse strain names from an MGI background description."""
    background = normalize_background(value)
    lower = background.lower()
    if not background or lower in {"not specified", "unknown", "not applicable"}:
        return None, "missing_or_unknown"
    if "either:" in lower:
        return None, "ambiguous_either"

    names = {
        family
        for family, pattern in STRAIN_FAMILY_PATTERNS
        if pattern.search(background)
    }
    if not names:
        return None, "unrecognized"
    reason = "multiple_recognized" if len(names) > 1 else "single_recognized"
    return ";".join(sorted(names)), reason


def load_ontology_index(path: str | Path) -> dict[str, Any]:
    """Load active, alternate, obsolete, and normal-branch MP identifiers."""
    terms: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    version = ""

    def flush() -> None:
        nonlocal current
        if current and current.get("id"):
            current.setdefault("name", "")
            current.setdefault("alt_ids", [])
            current.setdefault("parents", [])
            current.setdefault("is_obsolete", False)
            terms[current["id"]] = current
        current = None

    with Path(path).open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if line.startswith("data-version:"):
                version = line.split(":", 1)[1].strip()
            if line == "[Term]":
                flush()
                current = {"alt_ids": [], "parents": [], "is_obsolete": False}
                continue
            if line.startswith("[") and line != "[Term]":
                flush()
                continue
            if current is None:
                continue
            if line.startswith("id: "):
                current["id"] = line[4:].strip()
            elif line.startswith("name: "):
                current["name"] = line[6:].strip()
            elif line.startswith("alt_id: "):
                current["alt_ids"].append(line[8:].strip())
            elif line.startswith("is_a: "):
                current["parents"].append(line[6:].split(" ! ", 1)[0].strip())
            elif line == "is_obsolete: true":
                current["is_obsolete"] = True
        flush()

    active_terms = {
        term_id: term
        for term_id, term in terms.items()
        if term_id.startswith("MP:") and not term["is_obsolete"]
    }
    alt_to_primary: dict[str, str] = {}
    for term_id, term in active_terms.items():
        for alt_id in term["alt_ids"]:
            previous = alt_to_primary.get(alt_id)
            if previous is not None and previous != term_id:
                raise ValueError(f"MP alt ID maps to multiple primary IDs: {alt_id}")
            alt_to_primary[alt_id] = term_id

    children: dict[str, set[str]] = defaultdict(set)
    for term_id, term in active_terms.items():
        for parent_id in term["parents"]:
            children[parent_id].add(term_id)

    normal_ids: set[str] = set()
    stack = [NORMAL_PHENOTYPE_ROOT]
    while stack:
        term_id = stack.pop()
        if term_id in normal_ids:
            continue
        normal_ids.add(term_id)
        stack.extend(children.get(term_id, set()))

    return {
        "terms": terms,
        "active_terms": active_terms,
        "alt_to_primary": alt_to_primary,
        "normal_ids": normal_ids,
        "version": version or "not_embedded",
    }


def ontology_terms_for_tsumugi(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Convert the audit ontology structure to TSUMUGI's hierarchy schema."""
    return {
        term_id: {
            "id": term_id,
            "name": term["name"],
            "is_a": list(term.get("parents", [])),
        }
        for term_id, term in index["active_terms"].items()
    }


def classify_mp_id(mp_id: str, ontology_index: dict[str, Any]) -> dict[str, str]:
    """Resolve an MP identifier and classify it as abnormal, normal, or unusable."""
    active = ontology_index["active_terms"]
    alt_to_primary = ontology_index["alt_to_primary"]
    if mp_id in active:
        canonical_id = mp_id
        status = "primary"
    elif mp_id in alt_to_primary:
        canonical_id = alt_to_primary[mp_id]
        status = "alt_id_mapped"
    elif mp_id in ontology_index["terms"]:
        canonical_id = mp_id
        status = "obsolete"
    else:
        canonical_id = mp_id
        status = "unresolved"

    if status in {"primary", "alt_id_mapped"}:
        semantic = "normal" if canonical_id in ontology_index["normal_ids"] else "abnormal"
        name = active[canonical_id]["name"]
    else:
        semantic = "unresolved"
        name = ontology_index["terms"].get(canonical_id, {}).get("name", "")

    return {
        "source_mp_id": mp_id,
        "canonical_mp_id": canonical_id,
        "mp_term_name": name,
        "ontology_status": status,
        "semantic_class": semantic,
    }


def _find_active_ancestors(term_id: str, ontology_index: dict[str, Any]) -> set[str]:
    active_terms = ontology_index["active_terms"]
    ancestors: set[str] = set()
    stack = list(active_terms.get(term_id, {}).get("parents", []))
    while stack:
        parent_id = stack.pop()
        if parent_id in ancestors or parent_id not in active_terms:
            continue
        ancestors.add(parent_id)
        stack.extend(active_terms[parent_id].get("parents", []))
    return ancestors


def _select_impc_row_terms(record: dict[str, Any], ontology_index: dict[str, Any]) -> tuple[str, ...]:
    direct_id = str(record.get("mp_term_id") or "").strip()
    if direct_id:
        classified = classify_mp_id(direct_id, ontology_index)
        if classified["ontology_status"] in {"primary", "alt_id_mapped"}:
            return (classified["canonical_mp_id"],)
        return ()

    candidates = set()
    for source_id in str(record.get("intermediate_mp_term_id") or "").split(","):
        source_id = source_id.strip()
        if not source_id:
            continue
        classified = classify_mp_id(source_id, ontology_index)
        if classified["ontology_status"] in {"primary", "alt_id_mapped"}:
            candidates.add(classified["canonical_mp_id"])
    candidates.discard(ROOT_MP_TERM_ID)
    ancestor_cache = {
        term_id: _find_active_ancestors(term_id, ontology_index)
        for term_id in candidates
    }
    return tuple(
        sorted(
            term_id
            for term_id in candidates
            if not any(
                term_id in ancestor_cache[other_term_id]
                for other_term_id in candidates - {term_id}
            )
        )
    )


def _impc_life_stage(record: dict[str, Any]) -> str:
    procedure_name = str(record.get("procedure_name") or "")
    pipeline_name = str(record.get("pipeline_name") or "")
    if EMBRYO_PATTERN.search(procedure_name):
        return "Embryo"
    if "interval" in pipeline_name.lower():
        return "Interval"
    if "late" in pipeline_name.lower():
        return "Late"
    return "Early"


def collect_impc_life_stage_evidence(
    records: Iterable[dict[str, Any]],
    ontology_index: dict[str, Any],
    groups: dict[str, dict[str, Any]],
) -> Iterator[dict[str, Any]]:
    """Collect life-stage evidence from every raw IMPC row while streaming it onward."""
    for record in records:
        stage = _impc_life_stage(record)
        is_direct = bool(str(record.get("mp_term_id") or "").strip())
        for term_id in _select_impc_row_terms(record, ontology_index):
            group = groups.setdefault(
                term_id,
                {
                    "mp_term_names": set(),
                    "life_stages": set(),
                    "gene_ids": set(),
                    "row_count": 0,
                    "significant_row_count": 0,
                    "non_significant_row_count": 0,
                    "early_row_count": 0,
                    "direct_row_count": 0,
                    "intermediate_row_count": 0,
                    "procedure_ids": set(),
                    "pipeline_ids": set(),
                    "centers": set(),
                },
            )
            group["mp_term_names"].add(
                str(ontology_index["active_terms"][term_id].get("name", ""))
            )
            group["life_stages"].add(stage)
            group["gene_ids"].add(
                str(record.get("marker_accession_id") or record.get("marker_symbol") or "")
            )
            group["row_count"] += 1
            if is_direct:
                group["significant_row_count"] += 1
                group["direct_row_count"] += 1
            else:
                group["non_significant_row_count"] += 1
                group["intermediate_row_count"] += 1
            if stage == "Early":
                group["early_row_count"] += 1
            if record.get("procedure_stable_id"):
                group["procedure_ids"].add(str(record["procedure_stable_id"]))
            if record.get("pipeline_stable_id"):
                group["pipeline_ids"].add(str(record["pipeline_stable_id"]))
            if record.get("phenotyping_center"):
                group["centers"].add(str(record["phenotyping_center"]))
        yield record


def summarize_impc_life_stage_evidence(
    groups: dict[str, dict[str, Any]],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Infer a stage only when all raw IMPC evidence rows agree."""
    inference: dict[str, str] = {}
    audit: list[dict[str, Any]] = []
    for term_id in sorted(groups):
        group = groups[term_id]
        stages = sorted(group["life_stages"])
        inferred = stages[0] if len(stages) == 1 else None
        if inferred is not None:
            inference[term_id] = inferred
        audit.append(
            {
                "canonical_mp_id": term_id,
                "mp_term_name": join_unique(group["mp_term_names"]),
                "impc_life_stages": ";".join(stages),
                "inferred_life_stage": inferred,
                "inference_status": "unique_stage" if inferred is not None else "multiple_stages",
                "impc_row_count": group["row_count"],
                "impc_significant_row_count": group["significant_row_count"],
                "impc_non_significant_row_count": group["non_significant_row_count"],
                "impc_direct_mp_row_count": group.get("direct_row_count", 0),
                "impc_intermediate_mp_row_count": group.get("intermediate_row_count", 0),
                "impc_gene_count": len(group.get("gene_ids", set()) - {""}),
                "impc_early_row_count": group["early_row_count"],
                "impc_procedure_count": len(group.get("procedure_ids", set())),
                "impc_pipeline_count": len(group.get("pipeline_ids", set())),
                "impc_center_count": len(group.get("centers", set())),
            }
        )
    return inference, audit


def load_phenotypic_alleles(path: str | Path) -> tuple[dict[str, dict[str, str]], dict[str, int]]:
    """Read the 13-column MGI phenotypic allele report."""
    allele_map: dict[str, dict[str, str]] = {}
    comment_rows = 0
    data_rows = 0
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for line in handle:
            if line.startswith("#"):
                comment_rows += 1
                continue
            row = next(csv.reader([line], delimiter="\t"))
            if not row:
                continue
            if len(row) != len(PHENOTYPIC_ALLELE_COLUMNS):
                raise ValueError(
                    f"{path} expected {len(PHENOTYPIC_ALLELE_COLUMNS)} columns, found {len(row)}"
                )
            record = dict(zip(PHENOTYPIC_ALLELE_COLUMNS, row, strict=True))
            allele_id = record["allele_id"]
            if allele_id in allele_map:
                raise ValueError(f"Duplicate allele ID in {path}: {allele_id}")
            allele_map[allele_id] = record
            data_rows += 1
    return allele_map, {
        "comment_rows": comment_rows,
        "data_rows": data_rows,
        "unique_alleles": len(allele_map),
    }


def load_gene_pheno_genotypes(path: str | Path) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    """Read MGI gene-phenotype rows and group MP annotations by genotype."""
    genotypes: dict[str, dict[str, Any]] = {}
    raw_rows = 0
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if not row:
                continue
            if len(row) != len(GENE_PHENO_COLUMNS):
                raise ValueError(f"{path} expected {len(GENE_PHENO_COLUMNS)} columns, found {len(row)}")
            record = dict(zip(GENE_PHENO_COLUMNS, row, strict=True))
            raw_rows += 1
            genotype_id = record["genotype_id"]
            signature = {
                "allelic_composition": record["allelic_composition"],
                "allele_symbols": join_unique(split_tokens(record["allele_symbols"])),
                "allele_ids": join_unique(split_tokens(record["allele_ids"])),
                "background_raw": record["background_raw"],
                "marker_ids": join_unique(split_tokens(record["marker_ids"])),
            }
            genotype = genotypes.get(genotype_id)
            if genotype is None:
                genotype = {
                    **signature,
                    "genotype_id": genotype_id,
                    "annotations": defaultdict(set),
                    "input_conflict_fields": set(),
                }
                genotypes[genotype_id] = genotype
            else:
                for field, value in signature.items():
                    if genotype[field] != value:
                        genotype["input_conflict_fields"].add(field)
            genotype["annotations"][record["mp_id"]].update(split_tokens(record["pubmed_ids"]))

    return genotypes, {
        "raw_rows": raw_rows,
        "unique_genotypes": len(genotypes),
        "unique_genotype_mp": sum(len(genotype["annotations"]) for genotype in genotypes.values()),
    }


def classify_genotype_state(allelic_composition: str, allele_ids: list[str]) -> str:
    """Classify MGI genotype dosage without using background information."""
    composition = str(allelic_composition)
    if "<+>" in composition:
        return "heterozygous"
    if re.search(r"(?:/Y$|^Y/|/Y(?:\s|,|$))", composition):
        return "hemizygous"
    if "?" in composition:
        return "unresolved"
    if len(set(allele_ids)) >= 2:
        return "compound_heterozygous"
    if len(set(allele_ids)) == 1 and "/" in composition:
        return "homozygous"
    return "unresolved"


def build_life_stage_inference(
    impc_records: Iterable[dict[str, Any]],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Infer one life stage per canonical MP ID from all IMPC annotation rows."""
    groups: dict[str, dict[str, Any]] = {}
    for record in impc_records:
        term_id = str(record.get("mp_term_id") or "")
        stage = record.get("life_stage")
        if not term_id or not stage:
            continue
        group = groups.setdefault(
            term_id,
            {
                "mp_term_names": set(),
                "life_stages": set(),
                "gene_ids": set(),
                "row_count": 0,
                "significant_row_count": 0,
                "non_significant_row_count": 0,
                "early_row_count": 0,
                "direct_row_count": 0,
                "intermediate_row_count": 0,
                "procedure_ids": set(),
                "pipeline_ids": set(),
                "centers": set(),
            },
        )
        group["mp_term_names"].add(str(record.get("mp_term_name") or ""))
        group["life_stages"].add(str(stage))
        group["gene_ids"].add(
            str(record.get("marker_accession_id") or record.get("marker_symbol") or "")
        )
        group["row_count"] += 1
        if record.get("significant") is True:
            group["significant_row_count"] += 1
            group["direct_row_count"] += 1
        else:
            group["non_significant_row_count"] += 1
            group["intermediate_row_count"] += 1
        if stage == "Early":
            group["early_row_count"] += 1

    return summarize_impc_life_stage_evidence(groups)


def load_sex_annotations(
    path: str | Path,
    ontology_index: dict[str, Any],
) -> tuple[dict[tuple[str, str], str], dict[str, int]]:
    """Read abnormal sex-specific MGI annotations and collapse F/M to one label."""
    evidence: dict[tuple[str, str], set[str]] = defaultdict(set)
    diagnostics = Counter()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or set(reader.fieldnames) != SEX_COLUMNS:
            raise ValueError(f"Unexpected MGI_Pheno_Sex.rpt columns: {reader.fieldnames}")
        for record in reader:
            diagnostics["raw_rows"] += 1
            if str(record["Sex-specific Normal Y/N"]).strip().upper() != "N":
                diagnostics["sex_specific_normal_rows"] += 1
                continue
            mp = classify_mp_id(str(record["MP ID"]).strip(), ontology_index)
            if mp["semantic_class"] != "abnormal" or mp["ontology_status"] not in {
                "primary",
                "alt_id_mapped",
            }:
                diagnostics["unusable_mp_rows"] += 1
                continue
            sex = str(record["Sex"]).strip().upper()
            if sex not in {"F", "M"}:
                diagnostics["unexpected_sex_rows"] += 1
                continue
            key = (str(record["Genotype ID"]).strip(), mp["canonical_mp_id"])
            evidence[key].add(sex)
            diagnostics["abnormal_rows"] += 1

    result: dict[tuple[str, str], str] = {}
    for key, sexes in evidence.items():
        if sexes == {"F", "M"}:
            result[key] = "Both"
        elif sexes == {"F"}:
            result[key] = "Female"
        elif sexes == {"M"}:
            result[key] = "Male"
    diagnostics["collapsed_genotype_mp"] = len(result)
    return result, dict(diagnostics)


def _evaluate_genotype(
    genotype: dict[str, Any],
    allele_map: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Apply the all-background primary LOF eligibility rules to one genotype."""
    result: dict[str, Any] = {
        "accepted": False,
        "reason": "",
        "marker_id": "",
        "gene_symbol": "",
        "genotype_state": "unresolved",
        "allele_records": [],
        "allele_ids": [],
    }
    if genotype["input_conflict_fields"]:
        result["reason"] = "inconsistent_genotype_metadata"
        return result

    marker_ids = split_tokens(genotype["marker_ids"])
    if len(set(marker_ids)) != 1:
        result["reason"] = "not_single_marker"
        return result
    result["marker_id"] = marker_ids[0]

    allele_ids = split_tokens(genotype["allele_ids"])
    if not allele_ids:
        result["reason"] = "allele_ids_absent"
        return result
    if any(allele_id not in allele_map for allele_id in allele_ids):
        result["reason"] = "allele_metadata_missing"
        return result

    allele_records = [allele_map[allele_id] for allele_id in sorted(set(allele_ids))]
    allele_marker_ids = {record["marker_id"] for record in allele_records}
    gene_symbols = {record["gene_symbol"] for record in allele_records if record["gene_symbol"]}
    if allele_marker_ids != {result["marker_id"]} or len(gene_symbols) != 1:
        result["reason"] = "allele_identity_mismatch"
        return result

    allele_types = {record["allele_type"] for record in allele_records}
    if not allele_types.issubset(ALLOWED_ALLELE_TYPES):
        result["reason"] = "allele_type_not_allowed"
        return result
    if any(REQUIRED_NULL_ATTRIBUTE not in split_tokens(record["allele_attribute"]) for record in allele_records):
        result["reason"] = "required_null_token_absent"
        return result

    genotype_state = classify_genotype_state(genotype["allelic_composition"], allele_ids)
    if genotype_state not in PRIMARY_GENOTYPE_STATES:
        result["reason"] = f"genotype_state:{genotype_state}"
        return result

    result.update(
        {
            "accepted": True,
            "reason": "accepted",
            "gene_symbol": next(iter(gene_symbols)),
            "genotype_state": genotype_state,
            "allele_records": allele_records,
            "allele_ids": allele_ids,
        }
    )
    return result


def extract_mgi_lof_annotations(
    *,
    gene_pheno_path: str | Path,
    phenotypic_allele_path: str | Path,
    pheno_sex_path: str | Path,
    ontology_index: dict[str, Any],
    life_stage_by_mp: dict[str, str],
) -> dict[str, Any]:
    """Build all-background primary LOF genewise records and audit rows."""
    allele_map, allele_diagnostics = load_phenotypic_alleles(phenotypic_allele_path)
    genotypes, genotype_diagnostics = load_gene_pheno_genotypes(gene_pheno_path)
    sex_by_genotype_mp, sex_diagnostics = load_sex_annotations(pheno_sex_path, ontology_index)

    records: list[dict[str, Any]] = []
    eligibility_audit: list[dict[str, Any]] = []
    excluded_mp_audit: list[dict[str, Any]] = []
    strain_groups: dict[str, dict[str, Any]] = {}
    stage_counts = Counter()

    zygosity_map = {
        "homozygous": "Homo",
        "compound_heterozygous": "CompoundHetero",
        "hemizygous": "Hemi",
    }

    for genotype_id in sorted(genotypes):
        genotype = genotypes[genotype_id]
        stage_counts["all_genotypes"] += 1
        evaluation = _evaluate_genotype(genotype, allele_map)
        allele_records = evaluation.get("allele_records", [])
        eligibility_audit.append(
            {
                "genotype_id": genotype_id,
                "marker_ids": genotype["marker_ids"],
                "allele_ids": genotype["allele_ids"],
                "allele_symbols": genotype["allele_symbols"],
                "allelic_composition": genotype["allelic_composition"],
                "allele_types": join_unique(record.get("allele_type", "") for record in allele_records),
                "allele_attributes": join_unique(
                    attribute
                    for record in allele_records
                    for attribute in split_tokens(record.get("allele_attribute", ""))
                ),
                "background_raw": genotype["background_raw"],
                "genotype_state": evaluation["genotype_state"],
                "accepted": evaluation["accepted"],
                "reason": evaluation["reason"],
            }
        )
        if not evaluation["accepted"]:
            stage_counts[f"excluded:{evaluation['reason']}"] += 1
            continue
        stage_counts["eligible_primary_lof_genotypes"] += 1

        strain, strain_reason = normalize_strain(genotype["background_raw"])
        strain_group = strain_groups.setdefault(
            genotype["background_raw"],
            {
                "background_raw": genotype["background_raw"],
                "strain": strain,
                "normalization_status": strain_reason,
                "genotype_ids": set(),
                "marker_ids": set(),
                "positive_mp_count": 0,
            },
        )
        strain_group["genotype_ids"].add(genotype_id)
        strain_group["marker_ids"].add(evaluation["marker_id"])

        positive_count = 0
        for source_mp_id, pubmed_ids in sorted(genotype["annotations"].items()):
            mp = classify_mp_id(source_mp_id, ontology_index)
            if mp["semantic_class"] != "abnormal" or mp["ontology_status"] not in {
                "primary",
                "alt_id_mapped",
            }:
                excluded_mp_audit.append(
                    {
                        "genotype_id": genotype_id,
                        "marker_id": evaluation["marker_id"],
                        "gene_symbol": evaluation["gene_symbol"],
                        "source_mp_id": source_mp_id,
                        "canonical_mp_id": mp["canonical_mp_id"],
                        "ontology_status": mp["ontology_status"],
                        "semantic_class": mp["semantic_class"],
                        "reason": "normal_phenotype"
                        if mp["semantic_class"] == "normal"
                        else "unresolved_or_obsolete_mp",
                    }
                )
                stage_counts[f"excluded_mp:{mp['semantic_class']}"] += 1
                continue

            allele_ids = sorted(set(evaluation["allele_ids"]))
            records.append(
                {
                    "marker_symbol": evaluation["gene_symbol"],
                    "marker_accession_id": evaluation["marker_id"],
                    "mp_term_id": mp["canonical_mp_id"],
                    "mp_term_name": mp["mp_term_name"],
                    "source_mp_id": source_mp_id,
                    "zygosity": zygosity_map[evaluation["genotype_state"]],
                    "life_stage": life_stage_by_mp.get(mp["canonical_mp_id"]),
                    "sexual_dimorphism": None,
                    "observed_sex": sex_by_genotype_mp.get((genotype_id, mp["canonical_mp_id"])),
                    "strain": strain,
                    "background_raw": genotype["background_raw"] or None,
                    "effect_size": None,
                    "significant": True,
                    "significance_basis": "mgi_curated_annotation",
                    "source": "mgi",
                    "disease_annotation": [],
                    "genotype_id": genotype_id,
                    "allelic_composition": genotype["allelic_composition"],
                    "genotype_state": evaluation["genotype_state"],
                    "allele_ids": allele_ids,
                    "allele_symbols": sorted({record["allele_symbol"] for record in allele_records}),
                    "allele_types": sorted({record["allele_type"] for record in allele_records}),
                    "pubmed_ids": sorted(set(pubmed_ids)) or None,
                }
            )
            positive_count += 1

        strain_group["positive_mp_count"] += positive_count
        if positive_count:
            stage_counts["eligible_genotypes_with_abnormal_mp"] += 1
        else:
            stage_counts["eligible_genotypes_without_abnormal_mp"] += 1

    records.sort(
        key=lambda record: (
            record["marker_accession_id"],
            record["genotype_id"],
            record["mp_term_id"],
        )
    )
    if len(records) != len(
        {
            (record["genotype_id"], record["mp_term_id"])
            for record in records
        }
    ):
        raise AssertionError("MGI output contains duplicate genotype-MP rows")

    strain_audit = []
    for background_raw in sorted(strain_groups):
        group = strain_groups[background_raw]
        strain_audit.append(
            {
                "background_raw": background_raw,
                "strain": group["strain"],
                "normalization_status": group["normalization_status"],
                "genotype_count": len(group["genotype_ids"]),
                "marker_count": len(group["marker_ids"]),
                "positive_genotype_mp_count": group["positive_mp_count"],
            }
        )

    return {
        "records": records,
        "eligibility_audit": eligibility_audit,
        "excluded_mp_audit": excluded_mp_audit,
        "strain_audit": strain_audit,
        "stage_counts": [
            {"metric": metric, "count": count}
            for metric, count in sorted(stage_counts.items())
        ],
        "source_diagnostics": {
            "phenotypic_allele": allele_diagnostics,
            "gene_pheno": genotype_diagnostics,
            "pheno_sex": sex_diagnostics,
        },
    }

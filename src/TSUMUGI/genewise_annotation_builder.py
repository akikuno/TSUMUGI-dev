from __future__ import annotations

from collections.abc import Iterator

from TSUMUGI import annotator, filterer, formatter

INTEGRATED_OUTPUT_COLUMNS = (
    "marker_symbol",
    "marker_accession_id",
    "mp_term_id",
    "mp_term_name",
    "source_mp_id",
    "zygosity",
    "life_stage",
    "sexual_dimorphism",
    "observed_sex",
    "strain",
    "background_raw",
    "effect_size",
    "significant",
    "significance_basis",
    "source",
    "disease_annotation",
    "genotype_id",
    "allelic_composition",
    "genotype_state",
    "allele_ids",
    "allele_symbols",
    "allele_types",
    "pubmed_ids",
)


def build_genewise_phenotype_annotations(
    records: Iterator[dict],
    ontology_terms: dict,
    disease_annotations_by_gene: dict,
    *,
    include_integration_fields: bool = False,
) -> Iterator[dict]:
    ###########################################################
    # Preprocess data
    ###########################################################

    # --------------------------------------------------------
    # Select columns, maintained mp term, and significant genes
    # --------------------------------------------------------

    # Floatinize columns
    float_columns = [
        "p_value",
        "effect_size",
        "female_ko_effect_p_value",
        "female_ko_parameter_estimate",
        "male_ko_effect_p_value",
        "male_ko_parameter_estimate",
    ]
    records_formatted = formatter.floatinize_columns(records, float_columns)

    # Format zygosity
    zygosity_converter = {"heterozygote": "Hetero", "homozygote": "Homo", "hemizygote": "Hemi"}
    records_formatted = formatter.format_zygosity(records_formatted, zygosity_converter)
    # Take absolute value of effect size
    effect_size_columns = ["effect_size", "female_ko_parameter_estimate", "male_ko_parameter_estimate"]
    records_formatted = formatter.abs_effect_size(records_formatted, effect_size_columns)

    # --------------------------------------------------------
    # Annotate life stage and sexual dimorphisms
    # --------------------------------------------------------

    embryo_assays = {
        "E9.5",
        "E10.5",
        "E12.5",
        "Embryo LacZ",  # E12.5
        "E14.5",
        "E14.5-E15.5",
        "E18.5",
    }
    # Life stage
    records_annotated = annotator.annotate_life_stage(records_formatted, embryo_assays)
    # Sexual dimorphism
    records_annotated = annotator.annotate_sexual_dimorphism(records_annotated, threshold=1e-4)
    # Annotate Significant (True/False)
    records_annotated = annotator.annotate_significant(records_annotated, ontology_terms)
    # Human Diseases
    records_annotated = annotator.annotate_diseases(records_annotated, disease_annotations_by_gene)

    if include_integration_fields:
        records_annotated = _annotate_impc_integration_fields(records_annotated)

    # --------------------------------------------------------
    # Filter records
    # --------------------------------------------------------
    records_filtered = records_annotated

    # Subset columns
    to_keep_columns = {
        "marker_symbol",
        "marker_accession_id",
        "mp_term_id",
        "mp_term_name",
        "zygosity",
        "life_stage",
        "sexual_dimorphism",
        "effect_size",
        "significant",
        "disease_annotation",
    }
    if include_integration_fields:
        to_keep_columns = INTEGRATED_OUTPUT_COLUMNS
    records_filtered = filterer.subset_columns(records_filtered, to_keep_columns)

    # Keep only records with mp_term_id in the ontology file (= not obsolete)
    records_filtered = (record for record in records_filtered if record["mp_term_id"] in ontology_terms)

    # Distinct records with max effect size
    unique_keys = [
        "marker_symbol",
        "mp_term_id",
        "zygosity",
        "life_stage",
        "sexual_dimorphism",
    ]
    if include_integration_fields:
        unique_keys.append("strain")
    records_filtered = filterer.distinct_records_with_max_effect(
        records_filtered,
        unique_keys,
        prefer_significant=True,
    )

    genewise_phenotype_annotations = records_filtered

    return genewise_phenotype_annotations


def _annotate_impc_integration_fields(records: Iterator[dict]) -> Iterator[dict]:
    """Add source-aware fields without changing the default IMPC schema."""
    for record in records:
        record["source"] = "impc"
        record["significance_basis"] = "impc_statistical_test"
        record["source_mp_id"] = record.get("mp_term_id") or None
        record["strain"] = record.get("strain_name") or None
        record["background_raw"] = None
        record["observed_sex"] = None
        record["genotype_id"] = None
        record["allelic_composition"] = None
        record["genotype_state"] = None
        record["allele_ids"] = None
        record["allele_symbols"] = None
        record["allele_types"] = None
        record["pubmed_ids"] = None
        yield record

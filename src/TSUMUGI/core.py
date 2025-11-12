from __future__ import annotations

import logging
import pickle
import shutil
from collections.abc import Iterator
from datetime import date
from pathlib import Path

from TSUMUGI import (
    annotator,
    filterer,
    formatter,
    io_handler,
    network_constructor,
    report_generator,
    similarity_calculator,
    web_deployer,
)


def run_pipeline(args) -> None:
    ROOT_DIR = Path(args.output_dir)
    TEMPDIR = Path(ROOT_DIR / ".tempdir")

    records: Iterator[dict[str, str | float]] = io_handler.load_csv_as_dicts(Path(args.statistical_results))

    ontology_terms: dict[str, dict[str, str | list[str]]] = io_handler.parse_obo_file(Path(args.mp_obo))

    disease_annotations_by_gene: dict[str, list[dict[str, str]]] = io_handler.parse_impc_phenodigm(
        Path(args.impc_phenodigm)
    )

    ###########################################################
    # Preprocess data
    ###########################################################
    logging.info("Preprocessing statistical results...")

    # --------------------------------------------------------
    # Select columns, maintained mp term, and significant genes
    # --------------------------------------------------------

    # Floatinize columns
    float_columns = [
        "p_value",
        "effect_size",
        "female_ko_effect_p_value",  # sex differences
        "female_ko_parameter_estimate",  # sex differences
        "male_ko_effect_p_value",  # sex differences
        "male_ko_parameter_estimate",  # sex differences
    ]
    records_formatted = [formatter.floatinize_columns(record, float_columns) for record in records]

    # Format zygosity
    zygosity_converter = {"heterozygote": "Hetero", "homozygote": "Homo", "hemizygote": "Hemi"}
    records_formatted = formatter.format_zygosity(records_formatted, zygosity_converter)

    # Take absolute value of effect size
    effect_size_columns = ["effect_size", "female_ko_parameter_estimate", "male_ko_parameter_estimate"]
    records_formatted = [formatter.abs_effect_size(record, effect_size_columns) for record in records_formatted]

    # --------------------------------------------------------
    # Annotate life stage and sexual dimorphisms
    # --------------------------------------------------------
    logging.info("Annotating life stage and sexual dimorphisms...")

    records_annotated = records_formatted.copy()

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
    records_annotated = annotator.annotate_life_stage(records_annotated, embryo_assays)
    # Sexual dimorphism
    records_annotated = annotator.annotate_sexual_dimorphism(records_annotated, threshold=1e-4)
    # Human Diseases
    records_annotated = annotator.annotate_diseases(records_annotated, disease_annotations_by_gene)
    # Annotate non-significant terms
    records_annotated = annotator.annotate_non_significant_terms(records_annotated)

    # --------------------------------------------------------
    # Filter records
    # --------------------------------------------------------
    records_filtered = records_annotated.copy()

    # Keep only records with mp_term_id in the ontology file (= not obsolete)
    records_filtered = [record for record in records_filtered if record["mp_term_id"] in ontology_terms]

    # Distinct records with max effect size
    unique_keys = [
        "marker_symbol",
        "mp_term_id",
        "zygosity",
        "life_stage",
        "sexual_dimorphism",
    ]
    records_filtered = filterer.distinct_records_with_max_effect(records_filtered, unique_keys)

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
    records_filtered = filterer.subset_columns(records_filtered, to_keep_columns)

    genewise_phenotype_annotations = records_filtered.copy()
    genewise_phenotype_significants = [record for record in genewise_phenotype_annotations if record["significant"]]

    # --------------------------------------------------------
    # Cache results
    # --------------------------------------------------------
    output_dir = Path(TEMPDIR / "preprocessed")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "genewise_phenotype_annotations.pkl", "wb") as f:
        pickle.dump(genewise_phenotype_annotations, f)
    with open(output_dir / "genewise_phenotype_significants.pkl", "wb") as f:
        pickle.dump(genewise_phenotype_significants, f)

    del records_formatted
    del records_annotated
    del records_filtered

    ###########################################################
    # Calculate phenotype similarity
    ###########################################################

    all_term_ids = {r["mp_term_id"] for r in genewise_phenotype_significants}

    logging.info(f"Calculating pairwise similarity for {len(all_term_ids)} terms...")

    term_pair_similarity_map: dict[frozenset[str], dict[str, float]] = (
        similarity_calculator.calculate_all_pairwise_similarities(ontology_terms, all_term_ids, threads=args.threads)
    )
    # 30 min

    # ----------------------------------------
    # Calculate phenotype similarity for genes
    # ----------------------------------------

    logging.info(f"Annotate phenotype ancestors for {len(genewise_phenotype_significants)} records...")
    phenotype_ancestors: dict[frozenset[str], dict[str, dict[str, str]]] = (
        similarity_calculator.annotate_phenotype_ancestors(
            genewise_phenotype_significants,
            term_pair_similarity_map,
            ontology_terms,
            ic_threshold=5,
            threads=1,  # Set to 1 because passing large objects to the initializer causes the process to hang; this will be improved in the future.
        )
    )
    # 10 min

    logging.info(f"Calculating phenodigm similarity for {len(genewise_phenotype_significants)} records...")
    phenodigm_scores: dict[frozenset[str], int] = similarity_calculator.calculate_phenodigm_score(
        genewise_phenotype_significants,
        term_pair_similarity_map,
        threads=1,  # Set to 1 because passing large objects to the initializer causes the process to hang; this will be improved in the future.
    )
    # 30 min

    num_shared_phenotypes = similarity_calculator.calculate_num_shared_phenotypes(genewise_phenotype_significants)
    jaccard_indices = similarity_calculator.calculate_jaccard_indices(genewise_phenotype_significants)

    # ----------------------------------------
    # Summarize the phenotype similarity results
    # ----------------------------------------

    pairwise_similarity_annotations: dict[frozenset[str], dict[str, dict[str, str] | int]] = (
        similarity_calculator.summarize_similarity_annotations(ontology_terms, phenotype_ancestors, phenodigm_scores)
    )

    # --------------------------------------------------------
    # Cache results
    # --------------------------------------------------------
    output_dir = Path(TEMPDIR / "phenotype_similarity")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "term_pair_similarity_map.pkl", "wb") as f:
        pickle.dump(term_pair_similarity_map, f)

    with open(output_dir / "pairwise_similarity_annotations.pkl", "wb") as f:
        pickle.dump(pairwise_similarity_annotations, f)

    with open(output_dir / "phenotype_ancestors.pkl", "wb") as f:
        pickle.dump(phenotype_ancestors, f)

    with open(output_dir / "phenodigm_scores.pkl", "wb") as f:
        pickle.dump(phenodigm_scores, f)

    with open(output_dir / "num_shared_phenotypes.pkl", "wb") as f:
        pickle.dump(num_shared_phenotypes, f)

    with open(output_dir / "jaccard_indices.pkl", "wb") as f:
        pickle.dump(jaccard_indices, f)

    del term_pair_similarity_map
    del phenotype_ancestors
    del phenodigm_scores
    del num_shared_phenotypes
    del jaccard_indices

    ###########################################################
    # Generate network
    ###########################################################
    MIN_NUM_PHENOTYPES = 3

    pairwise_similarity_annotations_with_shared_phenotype = {
        k: v
        for k, v in pairwise_similarity_annotations.items()
        if len(v["phenotype_shared_annotations"]) >= MIN_NUM_PHENOTYPES
    }

    logging.info("Building phenotype network JSON files...")

    output_dir = Path(TEMPDIR / "network" / "phenotype")
    output_dir.mkdir(parents=True, exist_ok=True)
    network_constructor.build_phenotype_network_json(
        genewise_phenotype_significants,
        pairwise_similarity_annotations_with_shared_phenotype,
        disease_annotations_by_gene,
        output_dir,
    )

    logging.info("Building gene network JSON files...")
    output_dir = Path(TEMPDIR / "network" / "genesymbol")
    output_dir.mkdir(parents=True, exist_ok=True)

    network_constructor.build_gene_network_json(
        genewise_phenotype_significants,
        pairwise_similarity_annotations_with_shared_phenotype,
        disease_annotations_by_gene,
        output_dir,
    )

    del pairwise_similarity_annotations_with_shared_phenotype
    del disease_annotations_by_gene

    ###########################################################
    # Output reports to public directory
    ###########################################################
    logging.info("Generating reports...")
    Path(ROOT_DIR / "README.md").write_text(
        f"TSUMUGI version: {args.version}\n Running Date: {date.today().isoformat()}"
    )
    # records all
    report_generator.write_records_jsonl_gz(
        genewise_phenotype_annotations, Path(ROOT_DIR / "genewise_phenotype_annotations.jsonl.gz")
    )

    # pair similarity annotations
    report_generator.write_pairwise_similarity_annotations(
        pairwise_similarity_annotations, Path(ROOT_DIR / "pairwise_similarity_annotations.jsonl.gz")
    )
    del genewise_phenotype_annotations
    del pairwise_similarity_annotations

    ###########################################################
    # Output data for web application
    ###########################################################

    output_dir = Path(TEMPDIR, "webapp")  # data for webapp
    output_dir.mkdir(parents=True, exist_ok=True)

    # available mp terms
    report_generator.write_available_mp_terms_txt(TEMPDIR, Path(output_dir / "available_mp_terms.txt"))
    report_generator.write_available_mp_terms_json(TEMPDIR, Path(output_dir / "available_mp_terms.json"))

    # binary phenotypes
    report_generator.write_binary_phenotypes_txt(
        genewise_phenotype_significants, TEMPDIR, Path(output_dir / "binary_phenotypes.txt")
    )

    # available gene symbols
    report_generator.write_available_gene_symbols_txt(TEMPDIR, Path(output_dir / "available_gene_symbols.txt"))

    # marker symbol to accession id
    report_generator.write_marker_symbol_accession_id_json(
        genewise_phenotype_significants, TEMPDIR, Path(output_dir / "marker_symbol_accession_id.json")
    )

    ###########################################################
    # Deploy to web application
    ###########################################################

    logging.info("Building gene network JSON files...")
    is_test = args.is_test

    output_dir = Path(ROOT_DIR, "TSUMUGI-testwebapp") if is_test else Path(ROOT_DIR, "TSUMUGI-webapp")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    targetted_phenotypes = web_deployer.select_targetted_phenotypes(TEMPDIR, is_test=is_test)
    targetted_genes = web_deployer.select_targetted_genes(TEMPDIR, is_test=is_test)

    web_deployer.prepare_files(targetted_phenotypes, targetted_genes, TEMPDIR, output_dir)

    web_deployer.generate_phenotype_pages(genewise_phenotype_significants, targetted_phenotypes, TEMPDIR, output_dir)
    web_deployer.generate_gene_pages(genewise_phenotype_significants, targetted_genes, output_dir)
    web_deployer.generate_genelist_page(output_dir)

    # Remove template directory for web app
    shutil.rmtree(output_dir / "template")

    logging.info(f"Finished!🎊 Results are saved in {Path(ROOT_DIR).resolve()}")

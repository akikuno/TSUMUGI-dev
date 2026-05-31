from __future__ import annotations

import logging
import pickle
import shutil
from collections import defaultdict
from collections.abc import Iterator
from datetime import date
from pathlib import Path

from TSUMUGI import (
    gene_phenotype_module_builder,
    genewise_annotation_builder,
    io_handler,
    network_constructor,
    pairwise_similarity_builder,
    report_generator,
    web_deployer,
)

WEB_MIN_SHARED_ANNOTATIONS = 3
WEB_MIN_PHENOTYPE_SIMILARITY_SCORE = 1


def _filter_pairwise_similarity_annotations_for_web(
    pairwise_similarity_annotations: Iterator[dict[str, object]],
    min_shared_annotations: int,
    min_phenotype_similarity_score: int,
) -> list[dict[str, object]]:
    """Filter pairwise annotations before building web network JSON files."""
    selected_records: list[dict[str, object]] = []
    for record in pairwise_similarity_annotations:
        shared_annotations = record.get("phenotype_shared_annotations", [])
        phenotype_similarity_score = int(record.get("phenotype_similarity_score", 0))
        if (
            len(shared_annotations) >= min_shared_annotations
            and phenotype_similarity_score >= min_phenotype_similarity_score
        ):
            selected_records.append(record)
    return selected_records


def run_pipeline(args) -> None:
    ROOT_DIR = Path(args.output_dir)
    TEMPDIR = Path(ROOT_DIR / ".tempdir")

    records: Iterator[dict[str, str | float]] = io_handler.load_csv_as_dicts(Path(args.statistical_results))

    ontology_terms: dict[str, dict[str, str | list[str]]] = io_handler.parse_obo_file(Path(args.mp_obo))

    disease_annotations_by_gene: dict[str, list[dict[str, str]]] = io_handler.parse_impc_phenodigm(
        Path(args.impc_phenodigm)
    )

    Path(ROOT_DIR / "README.md").write_text(
        f"TSUMUGI version: {args.version}\n Running Date: {date.today().isoformat()}"
    )

    if args.debug_web is False:
        ###########################################################
        # Build gene-wise phenotype annotations
        ###########################################################

        logging.info("Preprocessing statistical results...")

        genewise_phenotype_annotations = genewise_annotation_builder.build_genewise_phenotype_annotations(
            records, ontology_terms, disease_annotations_by_gene
        )

        path_genewise_phenotype_annotations = ROOT_DIR / "genewise_phenotype_annotations.jsonl.gz"
        io_handler.write_jsonl(genewise_phenotype_annotations, path_genewise_phenotype_annotations)

        genewise_phenotype_significants = [
            record for record in io_handler.read_jsonl(path_genewise_phenotype_annotations) if record["significant"]
        ]

        # --------------------------------------------------------
        # Cache results
        # --------------------------------------------------------
        if args.debug:
            output_dir = Path(TEMPDIR / "preprocessed")
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(output_dir / "genewise_phenotype_annotations.pkl", "wb") as f:
                pickle.dump(list(io_handler.read_jsonl(path_genewise_phenotype_annotations)), f)
            with open(output_dir / "genewise_phenotype_significants.pkl", "wb") as f:
                pickle.dump(genewise_phenotype_significants, f)

        ###########################################################
        # Calculate phenotype similarity
        ###########################################################

        pairwise_similarity_annotations = pairwise_similarity_builder.build_pairwise_similarity(
            genewise_phenotype_significants,
            ontology_terms,
            args=args,
        )

        path_pairwise_similarity_annotations = ROOT_DIR / "pairwise_similarity_annotations.jsonl.gz"
        io_handler.write_jsonl(
            pairwise_similarity_annotations,
            path_pairwise_similarity_annotations,
            compresslevel=9,
        )

        ###########################################################
        # Generate network
        ###########################################################
        logging.info("Generating phenotype and gene networks...")

        pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)

        pairwise_similarity_annotations_with_shared_phenotype = _filter_pairwise_similarity_annotations_for_web(
            pairwise_similarity_annotations,
            min_shared_annotations=WEB_MIN_SHARED_ANNOTATIONS,
            min_phenotype_similarity_score=WEB_MIN_PHENOTYPE_SIMILARITY_SCORE,
        )
        logging.info(
            "Selected %d pairwise records for web networks with shared_annotations >= %d and "
            "phenotype_similarity_score >= %d",
            len(pairwise_similarity_annotations_with_shared_phenotype),
            WEB_MIN_SHARED_ANNOTATIONS,
            WEB_MIN_PHENOTYPE_SIMILARITY_SCORE,
        )

        logging.info("Building phenotype network JSON files...")

        # Detect binary phenotypes (effect_size in {0,1}); include both spaced and underscored names
        binary_phenotypes = set()
        phenotype_effects = defaultdict(set)
        for rec in genewise_phenotype_significants:
            phenotype_effects[rec["mp_term_name"]].add(rec.get("effect_size", 0))
        for mp_term_name, effects in phenotype_effects.items():
            if effects and all(es in (0, 1) for es in effects):
                binary_phenotypes.add(mp_term_name)

        output_dir = Path(TEMPDIR / "network" / "phenotype")
        output_dir.mkdir(parents=True, exist_ok=True)
        network_constructor.build_phenotype_network_json(
            genewise_phenotype_significants,
            pairwise_similarity_annotations_with_shared_phenotype,
            disease_annotations_by_gene,
            output_dir,
            binary_phenotypes=binary_phenotypes,
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

        logging.info("Building gene phenotype module JSON files...")
        gene_phenotype_module_builder.build_gene_phenotype_module_json(
            pairwise_similarity_annotations_with_shared_phenotype,
            ontology_terms,
            Path(TEMPDIR / "network" / "genesymbol"),
            Path(TEMPDIR / "network" / "genesymbol_modules"),
            Path(ROOT_DIR / "gene_phenotype_module_summary.csv"),
        )

        del pairwise_similarity_annotations_with_shared_phenotype
        del disease_annotations_by_gene

    ###########################################################
    # Output data for web application
    ###########################################################

    if args.debug_web:
        if not Path(TEMPDIR / "preprocessed" / "genewise_phenotype_significants.pkl").is_file():
            raise FileNotFoundError(f"genewise_phenotype_significants.pkl not found in {TEMPDIR}")

        with open(TEMPDIR / "preprocessed" / "genewise_phenotype_significants.pkl", "rb") as f:
            genewise_phenotype_significants = pickle.load(f)

        gene_network_dir = Path(TEMPDIR / "network" / "genesymbol")
        gene_module_dir = Path(TEMPDIR / "network" / "genesymbol_modules")
        path_pairwise_similarity_annotations = ROOT_DIR / "pairwise_similarity_annotations.jsonl.gz"
        has_gene_modules = gene_module_dir.exists() and any(gene_module_dir.glob("*.json.gz"))
        if gene_network_dir.exists() and path_pairwise_similarity_annotations.exists() and not has_gene_modules:
            logging.info("Building gene phenotype module JSON files for debug web...")
            pairwise_similarity_annotations = io_handler.read_jsonl(path_pairwise_similarity_annotations)
            pairwise_similarity_annotations_with_shared_phenotype = _filter_pairwise_similarity_annotations_for_web(
                pairwise_similarity_annotations,
                min_shared_annotations=WEB_MIN_SHARED_ANNOTATIONS,
                min_phenotype_similarity_score=WEB_MIN_PHENOTYPE_SIMILARITY_SCORE,
            )
            gene_phenotype_module_builder.build_gene_phenotype_module_json(
                pairwise_similarity_annotations_with_shared_phenotype,
                ontology_terms,
                gene_network_dir,
                gene_module_dir,
                Path(ROOT_DIR / "gene_phenotype_module_summary.csv"),
            )

    output_dir = Path(TEMPDIR, "webapp")
    output_dir.mkdir(parents=True, exist_ok=True)

    # available mp terms
    report_generator.write_available_mp_terms_txt(TEMPDIR, Path(output_dir / "available_mp_terms.txt"))
    available_mp_terms_json = Path(output_dir / "available_mp_terms.json")
    report_generator.write_available_mp_terms_json(TEMPDIR, available_mp_terms_json)
    report_generator.write_mp_term_id_lookup(
        genewise_phenotype_significants, available_mp_terms_json, Path(output_dir / "mp_term_id_lookup.json")
    )

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

    logging.info("Building web application...")

    output_dir = Path(ROOT_DIR, "TSUMUGI-webapp")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    targetted_phenotypes = web_deployer.select_targetted_phenotypes(TEMPDIR)
    targetted_genes = web_deployer.select_targetted_genes(TEMPDIR)

    web_deployer.prepare_files(targetted_phenotypes, targetted_genes, TEMPDIR, output_dir, args.version)

    if args.debug is True or args.debug_web is True:
        logging.debug(f"DEBUG: retain temporary directory: {Path(TEMPDIR).resolve()}")
    else:
        shutil.rmtree(TEMPDIR, ignore_errors=True)

    logging.info(f"Finished!🎊 Results are saved in {Path(ROOT_DIR).resolve()}")

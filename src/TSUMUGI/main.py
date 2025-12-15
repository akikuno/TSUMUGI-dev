from __future__ import annotations

import logging
import sys
from pathlib import Path

from TSUMUGI import argparser, core, validator
from TSUMUGI.subcommands import (
    count_filterer,
    genes_filterer,
    graphml_builder,
    life_stage_filterer,
    mp_filterer,
    score_filterer,
    sex_filterer,
    webapp_builder,
    zygosity_filterer,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    args = argparser.parse_args()

    logging.info(f"TSUMUGI version: {args.version}")

    ###########################################################
    # Load and validate data
    ###########################################################

    if getattr(args, "statistical_results", None):
        validator.validate_statistical_results(args.statistical_results)

    if getattr(args, "mp_obo", None):
        validator.validate_obo_file(args.mp_obo)

    if getattr(args, "impc_phenodigm", None):
        validator.validate_phenodigm_file(args.impc_phenodigm)

    if getattr(args, "mp_obo", None) and (getattr(args, "exclude", None) or getattr(args, "include", None)):
        mp_term_id = args.exclude or args.include
        validator.validate_mp_term_id(mp_term_id, args.mp_obo)

    ###########################################################
    # Run commands
    ###########################################################

    if args.cmd == "run":
        logging.info("Running TSUMUGI pipeline")
        core.run_pipeline(args)

    # ===========================================================
    # Subcommands for filtering pairwise similarity annotations
    # ===========================================================

    # -----------------------------------------------------
    # MP term inclusion/exclusion
    # -----------------------------------------------------
    if args.cmd == "mp":
        if args.include:
            if args.pairwise:
                logging.info(f"Including gene pairs with phenotypes related to MP term: {args.include}")
                mp_filterer.include_specific_phenotype(
                    path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                    path_genewise_phenotype_annotations=None,
                    path_obo=args.mp_obo,
                    mp_term_id=args.include,
                    life_stage=args.life_stage,
                    sex=args.sex,
                    zygosity=args.zygosity,
                    is_pairwise=True,
                )
            else:
                logging.info(f"Including genes with phenotypes related to MP term: {args.include}")
                mp_filterer.include_specific_phenotype(
                    path_pairwise_similarity_annotations=None,
                    path_genewise_phenotype_annotations=args.path_genewise,
                    path_obo=args.mp_obo,
                    mp_term_id=args.include,
                    life_stage=args.life_stage,
                    sex=args.sex,
                    zygosity=args.zygosity,
                    is_pairwise=False,
                )
        if args.exclude:
            if args.pairwise:
                logging.info(f"Excluding gene pairs with phenotypes related to MP term: {args.exclude}")
                mp_filterer.exclude_specific_phenotype(
                    path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                    path_genewise_phenotype_annotations=args.path_genewise,
                    path_obo=args.mp_obo,
                    mp_term_id=args.exclude,
                    life_stage=args.life_stage,
                    sex=args.sex,
                    zygosity=args.zygosity,
                    is_pairwise=True,
                )
            else:
                logging.info(f"Excluding genes with phenotypes related to MP term: {args.exclude}")
                mp_filterer.exclude_specific_phenotype(
                    path_pairwise_similarity_annotations=None,
                    path_genewise_phenotype_annotations=args.path_genewise,
                    path_obo=args.mp_obo,
                    mp_term_id=args.exclude,
                    life_stage=args.life_stage,
                    sex=args.sex,
                    zygosity=args.zygosity,
                    is_pairwise=False,
                )

    # -----------------------------------------------------
    # Number of phenotypes per gene/pair
    # -----------------------------------------------------
    if args.cmd == "count":
        logging.info("Filtering gene pairs based on number of phenotypes per gene")
        if args.genewise:
            count_filterer.filter_by_number_of_phenotypes_per_gene(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                path_genewise_phenotype_annotations=args.path_genewise,
                min_phenotypes=args.min,
                max_phenotypes=args.max,
            )
        elif args.pairwise:
            count_filterer.filter_by_number_of_phenotypes_per_pair(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                min_phenotypes=args.min,
                max_phenotypes=args.max,
            )

    # -----------------------------------------------------
    # Score of phenotype similarity per gene/pair
    # -----------------------------------------------------
    if args.cmd == "score":
        logging.info("Filtering gene pairs based on the score of phenotype similarity per gene")
        score_filterer.filter_by_score_of_phenotypes_per_pair(
            path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
            min_phenotypes=args.min,
            max_phenotypes=args.max,
        )

    # -----------------------------------------------------
    # gene lists filterer
    # -----------------------------------------------------
    if args.cmd == "genes":
        if args.genewise:
            if args.keep:
                if Path(args.keep).is_file():
                    gene_list = set(Path(args.keep).read_text().splitlines())
                else:
                    gene_list = set(args.keep.split(","))

                if len(gene_list) == 0:
                    raise ValueError("Gene list is empty. Please provide at least one gene symbol.")

                logging.info(f"Keeping phenotype annotations matching {len(gene_list)} genes")
                genes_filterer.filter_annotations_by_genes(
                    path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                    gene_list=gene_list,
                    keep=True,
                )
            elif args.drop:
                if Path(args.drop).is_file():
                    gene_list = set(Path(args.drop).read_text().splitlines())
                else:
                    gene_list = set(args.drop.split(","))
                if len(gene_list) == 0:
                    raise ValueError("Gene list is empty. Please provide at least one gene symbol.")

                logging.info(f"Dropping phenotype annotations matching {len(gene_list)} genes")
                genes_filterer.filter_annotations_by_genes(
                    path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                    gene_list=gene_list,
                    drop=True,
                )
        else:
            if args.keep:
                gene_pairs = set()
                for record in Path(args.keep).read_text().splitlines():
                    # TSV
                    if "\t" in record:
                        gene1, gene2 = record.split("\t")
                    # CSV
                    elif "," in record:
                        gene1, gene2 = record.split(",")
                    gene_pairs.add(frozenset([gene1, gene2]))

                if len(gene_pairs) == 0:
                    raise ValueError(f"Gene list is empty. Please provide at least one gene pair in {args.keep}.")

                logging.info(f"Keeping phenotype annotations matching {len(gene_pairs)} gene pairs")
                genes_filterer.filter_annotations_by_gene_pairs(
                    path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                    gene_pairs=gene_pairs,
                    keep=True,
                )
            elif args.drop:
                gene_pairs = set()
                for record in Path(args.drop).read_text().splitlines():
                    # TSV
                    if "\t" in record:
                        gene1, gene2 = record.split("\t")
                    # CSV
                    elif "," in record:
                        gene1, gene2 = record.split(",")
                    gene_pairs.add(frozenset([gene1, gene2]))

                if len(gene_pairs) == 0:
                    raise ValueError(f"Gene list is empty. Please provide at least one gene pair in {args.drop}.")

                logging.info(f"Dropping phenotype annotations matching {len(gene_pairs)} gene pairs")
                genes_filterer.filter_annotations_by_gene_pairs(
                    path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                    gene_pairs=gene_pairs,
                    drop=True,
                )

    # -----------------------------------------------------
    # Life stage filterer
    # -----------------------------------------------------
    if args.cmd == "life-stage":
        if args.keep:
            logging.info(f"Keeping phenotype annotations matching life stage: {args.keep}")
            life_stage_filterer.filter_annotations_by_life_stage(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                life_stage=args.keep,
                keep=True,
            )
        elif args.drop:
            logging.info(f"Dropping phenotype annotations matching life stage: {args.drop}")
            life_stage_filterer.filter_annotations_by_life_stage(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                life_stage=args.drop,
                drop=True,
            )

    # -----------------------------------------------------
    # Sex filterer
    # -----------------------------------------------------
    if args.cmd == "sex":
        if args.keep:
            logging.info(f"Keeping phenotype annotations matching sex: {args.keep}")
            sex_filterer.filter_annotations_by_sex(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                sex=args.keep,
                keep=True,
            )
        elif args.drop:
            logging.info(f"Dropping phenotype annotations matching sex: {args.drop}")
            sex_filterer.filter_annotations_by_sex(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                sex=args.drop,
                drop=True,
            )

    # -----------------------------------------------------
    # Zygosity filterer
    # -----------------------------------------------------
    if args.cmd == "zygosity":
        if args.keep:
            logging.info(f"Keeping phenotype annotations matching zygosity: {args.keep}")
            zygosity_filterer.filter_annotations_by_zygosity(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                zygosity=args.keep,
                keep=True,
            )
        elif args.drop:
            logging.info(f"Dropping phenotype annotations matching zygosity: {args.drop}")
            zygosity_filterer.filter_annotations_by_zygosity(
                path_pairwise_similarity_annotations=args.path_pairwise or sys.stdin,
                zygosity=args.drop,
                drop=True,
            )

    # -----------------------------------------------------
    # Build GraphML
    # -----------------------------------------------------
    if args.cmd == "build-graphml":
        logging.info("Building GraphML from pairwise similarity annotations")

        graphml_builder.write_graphml_to_stdout(
            pairwise_path=args.path_pairwise or sys.stdin,
            genewise_path=args.path_genewise,
        )
    # -----------------------------------------------------
    # Build Webapp
    # -----------------------------------------------------
    if args.cmd == "build-webapp":
        logging.info("Building webapp network from pairwise similarity annotations")

        webapp_builder.build_and_save_webapp_network(
            genewise_path=args.path_genewise,
            pairwise_path=args.path_pairwise or sys.stdin,
            output_dir=args.output_dir,
        )


if __name__ == "__main__":
    main()

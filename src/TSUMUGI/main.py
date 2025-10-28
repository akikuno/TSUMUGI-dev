from __future__ import annotations

import logging
import sys

from TSUMUGI import argparser, core, mp_filterer, n_phenos_filterer, validator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    args = argparser.parse_args()

    ###########################################################
    # Load and validate data
    ###########################################################

    if getattr(args, "statistical_results", None):
        validator.validate_statistical_results(args.statistical_results)

    if getattr(args, "obo", None):
        validator.validate_obo_file(args.obo)

    if getattr(args, "impc_phenodigm", None):
        validator.validate_phenodigm_file(args.impc_phenodigm)

    if getattr(args, "obo", None) and (getattr(args, "exclude", None) or getattr(args, "include", None)):
        mp_term_id = args.exclude or args.include
        validator.validate_mp_term_id(mp_term_id, args.obo)

    ###########################################################
    # Run commands
    ###########################################################

    if args.cmd == "run":
        logging.info("Running TSUMUGI pipeline")
        core.run_pipeline(args)

    elif args.cmd == "mp":
        if args.include:
            logging.info(f"Including gene pairs with phenotypes related to MP term: {args.include}")
            mp_filterer.include_specific_phenotype(
                path_pairwise_similarity_annotations=args.infile or sys.stdin,
                path_obo=args.obo,
                term_id=args.include,
                life_stage=args.life_stage,
                sex=args.sex,
                zygosity=args.zygosity,
            )
        elif args.exclude:
            logging.info(f"Excluding gene pairs with phenotypes related to MP term: {args.exclude}")
            mp_filterer.exclude_specific_phenotype(
                path_pairwise_similarity_annotations=args.infile or sys.stdin,
                path_genewise_phenotype_annotations=args.path_genewise,
                path_obo=args.obo,
                mp_term_id=args.exclude,
                life_stage=args.life_stage,
                sex=args.sex,
                zygosity=args.zygosity,
            )

    elif args.cmd == "n-phenos":
        logging.info("Filtering gene pairs based on number of phenotypes per gene")
        if args.genewise:
            n_phenos_filterer.filter_by_number_of_phenotypes_per_gene(
                path_pairwise_similarity_annotations=args.infile or sys.stdin,
                path_genewise_phenotype_annotations=args.path_genewise,
                min_phenotypes=args.min,
                max_phenotypes=args.max,
            )
        elif args.pairwise:
            n_phenos_filterer.filter_by_number_of_phenotypes_per_pair(
                path_pairwise_similarity_annotations=args.infile or sys.stdin,
                min_phenotypes=args.min,
                max_phenotypes=args.max,
            )


if __name__ == "__main__":
    main()

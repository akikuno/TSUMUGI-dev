from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version as pkg_version
from importlib.resources import files
from pathlib import Path


def _get_version() -> str:
    """
    Get TSUMUGI version defined in pyproject.toml.
    The argument must match [project.name] (distribution name).
    """
    try:
        return pkg_version("tsumugi")
    except PackageNotFoundError:
        return "not-available"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run TSUMUGI pipeline and subcommands",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # tsumugi -v / --version
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
        help="Show TSUMUGI version and exit.",
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # =========================================================
    # run: Run TSUMUGI pipeline
    # =========================================================
    run = subparsers.add_parser(
        "run",
        help="Run TSUMUGI pipeline",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    run.add_argument(
        "-o",
        "--output_dir",
        type=str,
        required=True,
        help=(
            "Output directory for TSUMUGI results.\n"
            "All generated files (intermediate and final results) will be saved here.\n"
        ),
    )

    run.add_argument(
        "-s",
        "--statistical_results",
        type=str,
        required=True,
        help=(
            "Path to IMPC statistical_results_ALL.csv file.\n"
            "This file contains statistical test results (effect sizes, p-values, etc.) "
            "for all IMPC phenotyping experiments.\n"
            "If not available, download 'statistical-results-ALL.csv.gz' manually from:\n"
            "https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/TSUMUGI-results/"
        ),
    )

    run.add_argument(
        "-m",
        "--mp_obo",
        type=str,
        required=False,
        help=(
            "Path to Mammalian Phenotype ontology file (mp.obo).\n"
            "Used to map and infer hierarchical relationships among MP terms.\n"
            "If not available, download 'mp.obo' manually from:\n"
            "https://obofoundry.org/ontology/mp.html"
        ),
    )

    run.add_argument(
        "-i",
        "--impc_phenodigm",
        type=str,
        required=False,
        help=(
            "Path to IMPC Phenodigm annotation file (impc_phenodigm.csv).\n"
            "This file links mouse phenotypes to human diseases based on Phenodigm similarity.\n"
            "If not available, download manually from:\n"
            "https://diseasemodels.research.its.qmul.ac.uk/\n"
        ),
    )

    run.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help=("Number of threads to use for TSUMUGI pipeline.\nIf not specified, defaults to 1.\n"),
    )

    # Debug options (hidden) to retain temporary files
    run.add_argument(
        "--debug",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    # Web specific debug options (hidden) to
    # skip preprocessing and retain temporary files
    run.add_argument(
        "--debug_web",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    # =========================================================
    # mp: Filter gene pairs by a specific MP term and its descendants
    # =========================================================
    mp_parser = subparsers.add_parser(
        "mp",
        help="Filter gene pairs by a specific MP term and its descendants",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # --- Group A: MP include/exclude ---
    group_mp_filter = mp_parser.add_mutually_exclusive_group(required=True)
    group_mp_filter.add_argument(
        "-i",
        "--include",
        dest="include",
        metavar="MP_ID",
        help=("Include gene pairs that share the specified MP term (descendants included).\nExample: -i MP:0001146"),
    )
    group_mp_filter.add_argument(
        "-e",
        "--exclude",
        dest="exclude",
        metavar="MP_ID",
        help=(
            "Exclude gene pairs that (when measured) lack the specified MP term "
            "(descendants included).\n"
            "Example: -e MP:0001146"
        ),
    )
    # --- Group B: granularity (genewise / pairwise) ---
    group_level = mp_parser.add_mutually_exclusive_group(required=False)
    group_level.add_argument(
        "-g", "--genewise", action="store_true", help="Filter by number of phenotypes per KO mouse"
    )
    group_level.add_argument(
        "-p", "--pairwise", action="store_true", help="Filter by number of shared phenotypes between KO pairs"
    )

    mp_parser.add_argument(
        "-m",
        "--mp_obo",
        type=str,
        required=False,
        help=(
            "Path to Mammalian Phenotype ontology file (mp.obo).\n"
            "Used to map and infer hierarchical relationships among MP terms.\n"
            "If not available, download 'mp.obo' manually from:\n"
            "https://obofoundry.org/ontology/mp.html"
        ),
    )

    mp_parser.add_argument(
        "-a",
        "--genewise_annotations",
        dest="path_genewise",
        type=str,
        required=False,
        help=(
            "Path to the 'genewise_phenotype_annotations' file (JSONL or JSONL.gz).\n"
            "Required when using '-e/--exclude' to determine genes that were measured\n"
            "and showed no phenotype for the target MP term.\n"
        ),
    )

    mp_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    # Annotations
    mp_parser.add_argument(
        "--life_stage",
        type=str,
        required=False,
        help=("Filter by life stage. 'Embryo', 'Early', 'Interval', and 'Late'."),
    )
    mp_parser.add_argument(
        "--sex",
        type=str,
        required=False,
        help=("Filter by sexual dimorphism. 'Male' or 'Female'."),
    )
    mp_parser.add_argument(
        "--zygosity", type=str, required=False, help=("Filter by zygosity.  'Homo', 'Hetero' or 'Hemi'.")
    )

    # =========================================================
    # count (Filter by the number of phenotypes)
    # =========================================================

    count_parser = subparsers.add_parser(
        "count",
        help="Filter genes or gene pairs by the number of phenotypes",
        description="Filter genes based on the number of detected phenotypes per KO or shared between KO pairs.",
    )

    group_count = count_parser.add_mutually_exclusive_group(required=True)
    group_count.add_argument(
        "-g", "--genewise", action="store_true", help="Filter by number of phenotypes per KO mouse"
    )
    group_count.add_argument(
        "-p", "--pairwise", action="store_true", help="Filter by number of shared phenotypes between KO pairs"
    )

    count_parser.add_argument("--min", type=int, help="Minimum number threshold")
    count_parser.add_argument("--max", type=int, help="Maximum number threshold")

    count_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    count_parser.add_argument(
        "-a",
        "--genewise_annotations",
        dest="path_genewise",
        type=str,
        required=False,
        help=(
            "Path to the 'genewise_phenotype_annotations' file (JSONL or JSONL.gz).\n"
            "Required when using '-g/--genewise' to determine genes that were measured.\n"
        ),
    )

    # =========================================================
    # score (Filter by the similarity score of gene pairs)
    # =========================================================

    score_parser = subparsers.add_parser(
        "score",
        help="Filter genes or gene pairs by the similarity score",
        description="Filter genes based on the similarity score per KO or shared between KO pairs.",
    )

    score_parser.add_argument("--min", type=int, help="Minimum number threshold")
    score_parser.add_argument("--max", type=int, help="Maximum number threshold")

    score_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    # =========================================================
    # genes (Filter by gene symbols or gene pairs)
    # =========================================================

    genes_parser = subparsers.add_parser(
        "genes",
        help="Filter gene pairs by gene symbols or gene pairs of phenotype annotations",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group_genes = genes_parser.add_mutually_exclusive_group(required=True)
    group_genes.add_argument(
        "-k",
        "--keep",
        metavar="GENE_SYMBOL",
        help="Keep ONLY annotations with the specified gene symbols (comma-separated or path of text file)",
    )
    group_genes.add_argument(
        "-d",
        "--drop",
        metavar="GENE_SYMBOL",
        help="Drop annotations with the specified gene symbols (comma-separated or path of text file)",
    )

    group_level = genes_parser.add_mutually_exclusive_group(required=False)
    group_level.add_argument("-g", "--genewise", action="store_true", help="Filter by user-provided gene symbols")
    group_level.add_argument("-p", "--pairwise", action="store_true", help="Filter by user-provided  gene pairs")

    genes_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    # =========================================================
    # life-stage (Filter by life stage)
    # =========================================================

    LIFE_STAGES = ("Embryo", "Early", "Interval", "Late")

    life_stage_parser = subparsers.add_parser(
        "life-stage",
        help="Filter gene pairs by life stage of phenotype annotations",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group_life_stage = life_stage_parser.add_mutually_exclusive_group(required=True)
    group_life_stage.add_argument(
        "-k",
        "--keep",
        choices=LIFE_STAGES,
        metavar="LIFE_STAGE",
        help="Keep ONLY annotations with the specified life stage",
    )
    group_life_stage.add_argument(
        "-d",
        "--drop",
        choices=LIFE_STAGES,
        metavar="LIFE_STAGE",
        help="Drop annotations with the specified life stage",
    )

    life_stage_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    # =========================================================
    # sex (Filter by sexual dimorphism)
    # =========================================================

    SEXES = ("Male", "Female", "None")

    sex_parser = subparsers.add_parser(
        "sex",
        help="Filter gene pairs by sexual dimorphism of phenotype annotations",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group_sex = sex_parser.add_mutually_exclusive_group(required=True)
    group_sex.add_argument(
        "-k",
        "--keep",
        choices=SEXES,
        metavar="SEX",
        help="Keep ONLY annotations with the specified sexual dimorphism",
    )
    group_sex.add_argument(
        "-d",
        "--drop",
        choices=SEXES,
        metavar="SEX",
        help="Drop annotations with the specified sexual dimorphism",
    )

    sex_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    # =========================================================
    # zygosity (Filter by zygosity)
    # =========================================================

    ZYGOSITIES = ("Homo", "Hetero", "Hemi")

    zygosity_parser = subparsers.add_parser(
        "zygosity",
        help="Filter gene pairs by zygosity of phenotype annotations",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group_zygosity = zygosity_parser.add_mutually_exclusive_group(required=True)
    group_zygosity.add_argument(
        "-k",
        "--keep",
        choices=ZYGOSITIES,
        metavar="ZYGOSITY",
        help="Keep ONLY annotations with the specified zygosity",
    )
    group_zygosity.add_argument(
        "-d",
        "--drop",
        choices=ZYGOSITIES,
        metavar="ZYGOSITY",
        help="Drop annotations with the specified zygosity",
    )

    zygosity_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    # =========================================================
    # build-graphml
    # =========================================================

    build_graphml_parser = subparsers.add_parser(
        "build-graphml",
        help="Build a GraphML file from gene pair similarity annotations",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    build_graphml_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    build_graphml_parser.add_argument(
        "-a",
        "--genewise_annotations",
        dest="path_genewise",
        type=str,
        required=True,
        help=("Path to the 'genewise_phenotype_annotations' file (JSONL or JSONL.gz).\n"),
    )

    # =========================================================
    # build-webapp
    # =========================================================

    build_webapp_parser = subparsers.add_parser(
        "build-webapp",
        help="Build a webapp from gene pair similarity annotations",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    build_webapp_parser.add_argument(
        "--in",
        dest="path_pairwise",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    build_webapp_parser.add_argument(
        "-a",
        "--genewise_annotations",
        dest="path_genewise",
        type=str,
        required=True,
        help=("Path to the 'genewise_phenotype_annotations' file (JSONL or JSONL.gz).\n"),
    )

    build_webapp_parser.add_argument(
        "-o",
        "--out",
        dest="output_dir",
        type=str,
        required=True,
    )
    #######################################################
    # Return parser
    #######################################################
    return parser


###############################################################################
# main
###############################################################################


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    ########################################################################
    # run
    ########################################################################
    if args.cmd == "run":
        # If args.mp_obo or args.impc_phendigm are not provided,
        # use the built-in files inside the TSUMUGI/data directory.
        if not args.mp_obo:
            args.mp_obo = str(files("TSUMUGI") / "data" / "mp.obo")

        if not args.impc_phenodigm:
            args.impc_phenodigm = str(files("TSUMUGI") / "data" / "impc_phenodigm.csv")

    ########################################################################
    # mp
    ########################################################################
    if args.cmd == "mp":
        # If args.mp_obo is not provided,
        # use the built-in files inside the TSUMUGI/data directory.
        if not args.mp_obo:
            args.mp_obo = str(files("TSUMUGI") / "data" / "mp.obo")

        if args.exclude and not args.path_genewise:
            parser.error(
                "mp: '-a/--path_genewise' is required when using '-e/--exclude'.\n"
                "Path to the 'genewise_phenotype_annotations' file (JSONL or JSONL.gz).\n"
            )

        # Default to pairwise if neither -g / --genewise nor -p / --pairwise is specified.
        if not args.genewise and not args.pairwise:
            args.pairwise = True
        else:
            args.pairwise = False

    ########################################################################
    # count / score
    ########################################################################
    # When using the count/score subcommand, at least one of --min or --max must be specified.
    if args.cmd == "count" and args.min is None and args.max is None:
        parser.error("count: At least one of '--min' or '--max' must be specified.")

    if args.cmd == "score" and args.min is None and args.max is None:
        parser.error("score: At least one of '--min' or '--max' must be specified.")

    # When using -g / --genewise with the count subcommand,
    # the --genewise_annotations option is required.
    if args.cmd == "count" and args.genewise and not args.path_genewise:
        parser.error(
            "count: '-a/--genewise_annotations' is required when using '-g/--genewise'.\n"
            "Provide the gene phenotype annotations JSONL(.gz) file to identify genes that were measured."
        )

    ########################################################################
    # genes
    ########################################################################
    if args.cmd == "genes":
        path_arg = args.keep or args.drop

        # Default to pairwise if neither -g / --genewise nor -p / --pairwise is specified.
        if not args.genewise and not args.pairwise:
            args.pairwise = True
        elif args.genewise:
            args.pairwise = False
        else:
            args.genewise = False

        # In pairwise mode, the gene list must be provided as a text file.
        if args.pairwise and not Path(path_arg).is_file():
            parser.error(
                "genes --pairwise: Please provide a valid path to a text file containing gene symbols or gene pairs."
            )

    ########################################################################
    # build-webapp
    ########################################################################
    # For build-webapp, check that output_dir is a directory (not a file)
    if args.cmd == "build-webapp" and Path(args.output_dir).suffix:
        parser.error(
            f"build-webapp: {args.output_dir} looks like a file name (has extension). Please specify a directory."
        )

    args.version = _get_version()

    return args

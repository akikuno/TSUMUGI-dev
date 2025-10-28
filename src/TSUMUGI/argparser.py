import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run TSUMUGI pipeline and subcommands",
        formatter_class=argparse.RawTextHelpFormatter,
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
        required=True,
        help=(
            "Path to Mammalian Phenotype ontology file (mp.obo).\n"
            "Used to map and infer hierarchical relationships among MP terms.\n"
            "If not available, download '/mp.obo' manually from:\n"
            "https://obofoundry.org/ontology/mp.html"
        ),
    )

    run.add_argument(
        "-i",
        "--impc_phenodigm",
        type=str,
        required=True,
        help=(
            "Path to IMPC Phenodigm annotation file (impc_phenodigm.csv).\n"
            "This file links mouse phenotypes to human diseases based on Phenodigm similarity.\n"
            "If not available, download manually from:\n"
            "https://diseasemodels.research.its.qmul.ac.uk/\n"
        ),
    )

    run.add_argument(
        "--is_test",
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

    group_mp = mp_parser.add_mutually_exclusive_group(required=True)
    group_mp.add_argument(
        "-i",
        "--include",
        dest="include",
        metavar="MP_ID",
        help=("Include gene pairs that share the specified MP term (descendants included).\nExample: -i MP:0001146"),
    )
    group_mp.add_argument(
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

    mp_parser.add_argument(
        "-o",
        "--obo",
        type=str,
        required=True,
        help=("Path to ontology file.\nExample: ./data/mp.obo"),
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
        dest="infile",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    mp_parser.add_argument(
        "--out",
        dest="outfile",
        type=str,
        required=False,
        help=("Path to output file (JSONL or JSONL.gz).\nIf omitted, data are written to STDOUT.\n"),
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
    # n-phenos (Filter by the number of phenotypes)
    # =========================================================

    nphenos_parser = subparsers.add_parser(
        "n-phenos",
        help="Filter by number of phenotypes",
        description="Filter genes by the number of phenotypes per KO or shared between KO pairs.",
    )

    group_nphenos = nphenos_parser.add_mutually_exclusive_group(required=True)
    group_nphenos.add_argument(
        "-g", "--genewise", action="store_true", help="Filter by number of phenotypes per KO mouse"
    )
    group_nphenos.add_argument(
        "-p", "--pairwise", action="store_true", help="Filter by number of shared phenotypes between KO pairs"
    )

    nphenos_parser.add_argument("--min", type=int, help="Minimum number threshold")
    nphenos_parser.add_argument("--max", type=int, help="Maximum number threshold")

    nphenos_parser.add_argument(
        "--in",
        dest="infile",
        type=str,
        required=False,
        help=(
            "Path to 'pairwise_similarity_annotations' file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
        ),
    )

    nphenos_parser.add_argument(
        "--out",
        dest="outfile",
        type=str,
        required=False,
        help=("Path to output file (JSONL or JSONL.gz).\nIf omitted, data are written to STDOUT.\n"),
    )

    nphenos_parser.add_argument(
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

    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # When using -e / --exclude with the mp subcommand,
    # the --path_genewise option is required.
    if args.cmd == "mp" and args.exclude and not args.path_genewise:
        parser.error(
            "mp: '-a/--path_genewise' is required when using '-e/--exclude'.\n"
            "Path to the 'genewise_phenotype_annotations' file (JSONL or JSONL.gz).\n"
            "and showed no phenotype for the target MP term.\n"
        )

    # When using the n-phenos subcommand, at least one of --min or --max must be specified.
    if args.cmd == "n-phenos":
        if args.min is None and args.max is None:
            parser.error("n-phenos: At least one of '--min' or '--max' must be specified.")

    # When using -g / --genewise with the n-phenos subcommand,
    # the --genewise_annotations option is required.
    if args.cmd == "n-phenos" and args.genewise and not args.path_genewise:
        parser.error(
            "n-phenos: '-a/--genewise_annotations' is required when using '-g/--genewise'.\n"
            "Provide the gene phenotype annotations JSONL(.gz) file to identify genes that were measured."
        )

    return args

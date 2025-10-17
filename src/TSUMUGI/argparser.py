import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run TSUMUGI pipeline and subcommands",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # =========================================================
    # run: 既存のパイプライン実行（従来の引数をそのまま移設）
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
            "Example: ./results/phenotype_network/"
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
            "Example: ./data/statistical-results-ALL.csv.gz\n"
            "If not available, download 'statistical-results-ALL.csv.gz' manually from:\n"
            "https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/results/"
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
            "Example: ./data/mp.obo\n"
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
            "Example: ./data/impc_phenodigm.csv\n"
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
    # mp: MP指定でペアをフィルタ（descendants固定）
    # =========================================================
    mp = subparsers.add_parser(
        "mp",
        help="Filter gene pairs by a specific MP term (descendants by default)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group = mp.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        dest="include",
        metavar="MP_ID",
        help=("Include gene pairs that share the specified MP term (descendants included).\nExample: -i MP:0001146"),
    )
    group.add_argument(
        "-e",
        dest="exclude",
        metavar="MP_ID",
        help=(
            "Exclude gene pairs that (when measured) lack the specified MP term "
            "(descendants included).\n"
            "Example: -e MP:0001146"
        ),
    )

    mp.add_argument(
        "-m",
        "--mp_obo",
        type=str,
        required=True,
        help=(
            "Path to Mammalian Phenotype ontology file (mp.obo).\n"
            "Used to expand descendants of the specified MP term.\n"
            "Example: ./data/mp.obo"
        ),
    )

    mp.add_argument(
        "-s",
        "--statistical_results",
        type=str,
        required=False,
        help=(
            "Path to IMPC statistical_results_ALL.csv file.\n"
            "Required when using '-e/--exclude' to determine genes that were measured\n"
            "and showed no phenotype for the target MP term.\n"
            "Example: ./data/statistical-results-ALL.csv.gz"
        ),
    )

    mp.add_argument(
        "--in",
        dest="infile",
        type=str,
        required=False,
        help=(
            "Path to input gene pair file (JSONL or JSONL.gz).\n"
            "If omitted, data are read from STDIN.\n"
            "Example: ./results/phenotype_similarity_per_gene_pair.jsonl.gz"
        ),
    )

    mp.add_argument(
        "--out",
        dest="outfile",
        type=str,
        required=False,
        help=(
            "Path to output file (JSONL or JSONL.gz).\n"
            "If omitted, data are written to STDOUT.\n"
            "Example: ./results/pairs.filtered.jsonl.gz"
        ),
    )

    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # 追加バリデーション：mpサブコマンドで -e/--exclude を使う場合は --statistical_results が必須
    if args.cmd == "mp" and args.exclude and not args.statistical_results:
        parser.error(
            "mp: '-s/--statistical_results' is required when using '-e/--exclude'.\n"
            "Provide IMPC 'statistical_results_ALL.csv.gz' to identify genes measured "
            "without the specified phenotype."
        )

    return args


# if __name__ == "__main__":
#     args = parse_args()
#     # ここから先は args.cmd に応じて処理を分岐:
#     # if args.cmd == "run": ...
#     # elif args.cmd == "mp": ...

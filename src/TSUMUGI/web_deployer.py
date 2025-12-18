from __future__ import annotations

import shutil
from importlib.resources import as_file, files
from pathlib import Path

###########################################################
# Select targetted phenotypes and gene symbols
###########################################################


def select_targetted_phenotypes(TEMPDIR: Path, is_test: bool = True) -> set[str]:
    if is_test:
        targetted_phenotypes = [
            "edema",
            "male infertility",
            "increased fasting circulating glucose level",
            "preweaning lethality, complete penetrance",
            "increased blood urea nitrogen level",
            "increased circulating glycerol level",
            "convulsive seizures",
        ]
    else:
        mp_terms_file = Path(TEMPDIR, "webapp", "available_mp_terms.txt")
        targetted_phenotypes = mp_terms_file.read_text().splitlines() if mp_terms_file.exists() else []

    return set(targetted_phenotypes)


def select_targetted_genes(TEMPDIR: Path, is_test: bool = True) -> set[str]:
    if is_test:
        targetted_genes = [
            "Rab10",
            "Ints8",
            "Trappc11",
            "Zfp39",
            "Kcnma1",
            "Plekha8",
            "Dstn",
            "Vrk1",
            "Sox4",
        ]
    else:
        gene_symbols_file = Path(TEMPDIR, "webapp", "available_gene_symbols.txt")
        targetted_genes = gene_symbols_file.read_text().splitlines() if gene_symbols_file.exists() else []

    return set(targetted_genes)


###########################################################
# Prepare files
###########################################################


def _prepare_directories(output_dir: str | Path) -> None:
    Path(output_dir / "data" / "phenotype").mkdir(parents=True, exist_ok=True)
    Path(output_dir / "data" / "genesymbol").mkdir(parents=True, exist_ok=True)


def _generate_index_html(output_dir: str | Path, TSUMUGI_VERSION: str) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    temp_file = files("TSUMUGI") / "web" / "template" / "template_index.html"

    with as_file(temp_file) as template_path:
        with template_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as dst:
            for line in src:
                if "REMOVE_THIS_LINE" in line:
                    continue
                line = line.replace("TSUMUGI_VERSION", TSUMUGI_VERSION)
                dst.write(line)


def _write_version_file(output_dir: str | Path, TSUMUGI_VERSION: str) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    version_file = output_dir / "version.txt"
    version_file.write_text(TSUMUGI_VERSION, encoding="utf-8")


def _copy_directories(output_dir: str | Path) -> None:
    # Copy css and js directories
    for asset in ["css", "js"]:
        dst_dir = output_dir / asset
        dst_dir.mkdir(parents=True, exist_ok=True)
        temp_file = files("TSUMUGI") / "web" / asset
        with as_file(temp_file) as src_dir:
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    for asset in ["css", "js"]:
        dst_dir = output_dir / "app" / asset
        dst_dir.mkdir(parents=True, exist_ok=True)
        temp_file = files("TSUMUGI") / "web" / "app" / asset
        with as_file(temp_file) as src_dir:
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    # Copy shared app entry files
    for filename in ["viewer.html", "viewer.js"]:
        dst_file = output_dir / "app" / filename
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = files("TSUMUGI") / "web" / "app" / filename
        shutil.copy(temp_file, dst_file)

    # Copy the image directory
    dst_dir = output_dir / "image"
    dst_dir.mkdir(parents=True, exist_ok=True)
    temp_file = files("TSUMUGI") / "web" / "image"
    with as_file(temp_file) as src_dir:
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)


def _copy_json_files(targetted_phenotypes, targetted_genes, TEMPDIR: Path, output_dir: str | Path) -> None:
    src_phenotype_dir = Path(TEMPDIR, "network", "phenotype")
    src_gene_dir = Path(TEMPDIR, "network", "genesymbol")

    dst_phenotype_dir = output_dir / "data" / "phenotype"
    dst_gene_dir = output_dir / "data" / "genesymbol"

    dst_phenotype_dir.mkdir(parents=True, exist_ok=True)
    dst_gene_dir.mkdir(parents=True, exist_ok=True)

    for pheno in targetted_phenotypes:
        pheno = pheno.replace(" ", "_")
        src_file = src_phenotype_dir / f"{pheno}.json.gz"
        if src_file.exists():
            shutil.copy(src_file, dst_phenotype_dir / src_file.name)

    for gene in targetted_genes:
        src_file = src_gene_dir / f"{gene}.json.gz"
        if src_file.exists():
            shutil.copy(src_file, dst_gene_dir / src_file.name)


def _copy_webapp_files(TEMPDIR: Path, output_dir: str | Path) -> None:
    data_dir = output_dir / "data"
    ROOT_DIR = Path(TEMPDIR).parent

    file_map = {
        Path(TEMPDIR, "webapp", "available_mp_terms.json"): data_dir / "available_mp_terms.json",
        Path(TEMPDIR, "webapp", "available_mp_terms.txt"): data_dir / "available_mp_terms.txt",
        Path(TEMPDIR, "webapp", "available_gene_symbols.txt"): data_dir / "available_gene_symbols.txt",
        Path(TEMPDIR, "webapp", "marker_symbol_accession_id.json"): data_dir / "marker_symbol_accession_id.json",
        Path(TEMPDIR, "webapp", "binary_phenotypes.txt"): data_dir / "binary_phenotypes.txt",
        Path(ROOT_DIR / "genewise_phenotype_annotations.jsonl.gz"): data_dir
        / "genewise_phenotype_annotations.jsonl.gz",
        Path(ROOT_DIR / "pairwise_similarity_annotations.jsonl.gz"): data_dir
        / "pairwise_similarity_annotations.jsonl.gz",
    }

    for src, dst in file_map.items():
        shutil.copy(src, dst)

    # Copy webapp launchers
    for file_name in ["open_webapp_mac.command", "open_webapp_windows.bat", "open_webapp_linux.sh", "serve_index.py"]:
        temp_file = files("TSUMUGI") / "web" / file_name
        shutil.copy(temp_file, output_dir / file_name)


def prepare_files(
    targetted_phenotypes, targetted_genes, TEMPDIR: Path, output_dir: str | Path, TSUMUGI_VERSION: str
) -> None:
    _prepare_directories(output_dir)
    _copy_directories(output_dir)
    _copy_json_files(targetted_phenotypes, targetted_genes, TEMPDIR, output_dir)
    _copy_webapp_files(TEMPDIR, output_dir)
    _generate_index_html(output_dir, TSUMUGI_VERSION)
    _write_version_file(Path(output_dir, "app"), TSUMUGI_VERSION)


###########################################################
# Generate HTML and JS for web application
###########################################################

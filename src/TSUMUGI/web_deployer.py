from __future__ import annotations

import shutil
from importlib.resources import as_file, files
from pathlib import Path

from tqdm import tqdm

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
    Path(output_dir / "app" / "phenotype").mkdir(parents=True, exist_ok=True)
    Path(output_dir / "app" / "genesymbol").mkdir(parents=True, exist_ok=True)
    Path(output_dir / "app" / "genelist").mkdir(parents=True, exist_ok=True)


def _generate_index_html(output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    temp_file = files("TSUMUGI") / "template" / "template_index.html"

    with as_file(temp_file) as template_path:
        with template_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as dst:
            for line in src:
                if "REMOVE_THIS_LINE" in line:
                    continue
                dst.write(line)


def _copy_directories(output_dir: str | Path) -> None:
    # Copy css and js directories
    for asset in ["css", "js"]:
        dst_dir = output_dir / asset
        dst_dir.mkdir(parents=True, exist_ok=True)
        temp_file = files("TSUMUGI") / asset
        with as_file(temp_file) as src_dir:
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    for asset in ["css", "js"]:
        dst_dir = output_dir / "app" / asset
        dst_dir.mkdir(parents=True, exist_ok=True)
        temp_file = files("TSUMUGI") / "app" / asset
        with as_file(temp_file) as src_dir:
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    # imageディレクトリをコピー
    dst_dir = output_dir / "image"
    dst_dir.mkdir(parents=True, exist_ok=True)
    temp_file = files("TSUMUGI") / "image"
    with as_file(temp_file) as src_dir:
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    # templateディレクトリをコピー
    dst_dir = output_dir / "template"
    dst_dir.mkdir(parents=True, exist_ok=True)
    temp_file = files("TSUMUGI") / "template"
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

    file_map = {
        Path(TEMPDIR, "webapp", "available_mp_terms.json"): data_dir / "available_mp_terms.json",
        Path(TEMPDIR, "webapp", "available_mp_terms.txt"): data_dir / "available_mp_terms.txt",
        Path(TEMPDIR, "webapp", "available_gene_symbols.txt"): data_dir / "available_gene_symbols.txt",
        Path(TEMPDIR, "webapp", "marker_symbol_accession_id.json"): data_dir / "marker_symbol_accession_id.json",
    }

    for src, dst in file_map.items():
        shutil.copy(src, dst)


def prepare_files(targetted_phenotypes, targetted_genes, TEMPDIR: Path, output_dir: str | Path) -> None:
    _prepare_directories(output_dir)
    _copy_directories(output_dir)
    _copy_json_files(targetted_phenotypes, targetted_genes, TEMPDIR, output_dir)
    _copy_webapp_files(TEMPDIR, output_dir)
    _generate_index_html(output_dir)


###########################################################
# Generate HTML and JS for web application
###########################################################


def _read_file(filepath: str | Path) -> str:
    with open(filepath, encoding="utf-8") as f:
        return f.read()


def _write_file(filepath: str | Path, content: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def _replace_placeholder(template, placeholder, insert_text):
    return template.replace(placeholder, insert_text)


def _inject_html(template_path, insert_path, placeholder, output_path):
    template = _read_file(template_path)
    insert = _read_file(insert_path)
    updated = _replace_placeholder(template, placeholder, insert)
    _write_file(output_path, updated)


def _generate_simple_html(template_path, output_path, replacements):
    content = _read_file(template_path)
    for key, value in replacements.items():
        content = content.replace(key, value)
    _write_file(output_path, content)


# ---------------------------------------------------------
# Phenotype
# ---------------------------------------------------------


def _generate_phenotype_html(
    mp_term_name_underscored: str, mp_term_name: str, impc_url_phenotype: str, mode: str, output_dir: str
) -> None:
    for part in ["body-container", "cy-container"]:
        template_path = f"{output_dir}/template/template-app-html/{part}.html"
        output_path = f"/tmp/{part}.html"

        if mode == "non-binary-phenotype":
            insert_path = f"{output_dir}/template/template-app-html/{part}-phenotype.html"
            _inject_html(template_path, insert_path, "XXX_PHENOTYPE_SEVERITY", output_path)
        else:
            _generate_simple_html(template_path, output_path, {"XXX_PHENOTYPE_SEVERITY": ""})
    # head.html
    _generate_simple_html(
        f"{output_dir}/template/template-app-html/head.html",
        "/tmp/head.html",
        {"XXX_TITLE": mp_term_name, "XXX_JS_FILE_NAME": mp_term_name_underscored},
    )
    # header.html
    header_insert = f"<a href='{impc_url_phenotype}' target='_blank'>{mp_term_name}</a>"
    _generate_simple_html(
        f"{output_dir}/template/template-app-html/header.html",
        "/tmp/header.html",
        {"XXX_TITLE": header_insert},
    )
    # template_app.html → 完成版HTML
    template = _read_file(f"{output_dir}/template/template-app-html/template_app.html")
    final_html = (
        template.replace("XXX_HEAD", _read_file("/tmp/head.html"))
        .replace("XXX_H1", _read_file("/tmp/header.html"))
        .replace("XXX_BODY_CONTAINER", _read_file("/tmp/body-container.html"))
        .replace("XXX_CY_CONTAINER", _read_file("/tmp/cy-container.html"))
    )
    _write_file(f"{output_dir}/app/phenotype/{mp_term_name_underscored}.html", final_html)


def _generate_phenotype_javascript(
    mp_term_name_underscored: str, mp_term_name: str, mode: str, output_dir: str
) -> None:
    template_app_path = "/tmp/template_app.js"

    if mode == "non-binary-phenotype":
        shutil.copy(
            f"{output_dir}/template/template-app-js/filterByNodeColorAndEdgeSize_phenotype.js",
            "/tmp/filterByNodeColorAndEdgeSize_phenotype.js",
        )
        template = _read_file(f"{output_dir}/template/template-app-js/template_app.js")
        node_min_max = _read_file(f"{output_dir}/template/template-app-js/nodeMinMax.js")
        init = _read_file(f"{output_dir}/template/template-app-js/node_color_initialization.js")
        update = _read_file(f"{output_dir}/template/template-app-js/node_color_update.js")
        template = (
            template.replace("XXX_NODE_MIN_MAX", node_min_max)
            .replace("XXX_NODE_COLOR_INITIALIZATION", init)
            .replace("XXX_NODE_COLOR_UPDATE", update)
        )
        _write_file(template_app_path, template)

    else:
        # Binary phenotype の処理
        lines = _read_file(
            f"{output_dir}/template/template-app-js/filterByNodeColorAndEdgeSize_phenotype.js"
        ).splitlines()
        filtered_lines = "\n".join(line for line in lines if "REMOVE_THIS_LINE_IF_BINARY_PHENOTYPE" not in line)
        _write_file("/tmp/filterByNodeColorAndEdgeSize_phenotype.js", filtered_lines)

        template = _read_file(f"{output_dir}/template/template-app-js/template_app.js")
        template = template.replace("XXX_NODE_COLOR_INITIALIZATION", "").replace("XXX_NODE_COLOR_UPDATE", "")
        _write_file(template_app_path, template)

    main_template = _read_file(template_app_path)
    insert = _read_file("/tmp/filterByNodeColorAndEdgeSize_phenotype.js")

    final_js = (
        main_template.replace("XXX_NODE_MIN_MAX", "")
        .replace("XXX_FILTER_BY_NODE_COLOR_AND_EDGE_SIZE", insert)
        .replace(
            "XXX_EDGE_MIN_MAX",
            "const edgeMin = Math.min(...edgeSizes); const edgeMax = Math.max(...edgeSizes);",
        )
        .replace("XXX_ELEMENTS", f"loadJSONGz('../../data/phenotype/{mp_term_name_underscored}.json.gz')")
        .replace("XXX_PHENOTYPE", mp_term_name)
        .replace("XXX_NAME", mp_term_name_underscored)
    )

    _write_file(f"{output_dir}/app/phenotype/{mp_term_name_underscored}.js", final_js)


def generate_phenotype_pages(records_significants, targetted_phenotypes, TEMPDIR: Path, output_dir) -> None:
    map_mp_term_name_to_impc_url_phenotype = {}
    for record in records_significants:
        mp_term_name = record["mp_term_name"]
        mp_term_id = record["mp_term_id"]
        impc_url_phenotype = f"https://www.mousephenotype.org/data/phenotypes/{mp_term_id}"
        map_mp_term_name_to_impc_url_phenotype[mp_term_name] = impc_url_phenotype

    path_file = Path(TEMPDIR, "webapp", "binary_phenotypes.txt")
    binary_phenotypes = set(path_file.read_text().splitlines())

    for mp_term_name in tqdm(targetted_phenotypes, desc="Processing phenotypes"):
        mp_term_name_underscored = mp_term_name.replace(" ", "_")
        impc_url = map_mp_term_name_to_impc_url_phenotype.get(mp_term_name, "")
        mode = "binary_phenotype" if mp_term_name_underscored in binary_phenotypes else "non-binary-phenotype"

        _generate_phenotype_html(mp_term_name_underscored, mp_term_name, impc_url, mode, output_dir)
        _generate_phenotype_javascript(mp_term_name_underscored, mp_term_name, mode, output_dir)


# ---------------------------------------------------------
# Gene
# ---------------------------------------------------------


def _generate_gene_html(gene_symbol, impc_url_gene, output_dir):
    for part in ["body-container", "cy-container"]:
        template_path = f"{output_dir}/template/template-app-html/{part}.html"
        output_path = f"/tmp/{part}.html"
        _generate_simple_html(template_path, output_path, {"XXX_PHENOTYPE_SEVERITY": ""})

    # head.html
    _generate_simple_html(
        f"{output_dir}/template/template-app-html/head.html",
        "/tmp/head.html",
        {"XXX_TITLE": gene_symbol, "XXX_JS_FILE_NAME": gene_symbol},
    )

    # header.html
    header_insert = f"<a href='{impc_url_gene}' target='_blank'>{gene_symbol}</a>"
    _generate_simple_html(
        f"{output_dir}/template/template-app-html/header.html",
        "/tmp/header.html",
        {"XXX_TITLE": header_insert},
    )

    # template_app.html
    template = _read_file(f"{output_dir}/template/template-app-html/template_app.html")
    final_html = (
        template.replace("XXX_HEAD", _read_file("/tmp/head.html"))
        .replace("XXX_H1", _read_file("/tmp/header.html"))
        .replace("XXX_BODY_CONTAINER", _read_file("/tmp/body-container.html"))
        .replace("XXX_CY_CONTAINER", _read_file("/tmp/cy-container.html"))
    )

    _write_file(f"{output_dir}/app/genesymbol/{gene_symbol}.html", final_html)


def _generate_gene_javascript(gene_symbol: str, output_dir: str | Path) -> None:
    template_lines = _read_file(f"{output_dir}/template/template-app-js/template_app.js").splitlines()
    filtered_lines = [
        line
        for line in template_lines
        if "XXX_NODE_COLOR_INITIALIZATION" not in line and "XXX_NODE_COLOR_UPDATE" not in line
    ]
    _write_file("/tmp/template_app.js", "\n".join(filtered_lines))

    template = _read_file("/tmp/template_app.js")
    insert_filterByNodeColorAndEdgeSize = _read_file(
        f"{output_dir}/template/template-app-js/filterByNodeColorAndEdgeSize_genesymbol.js"
    )
    insert_edgeMinMax = _read_file(f"{output_dir}/template/template-app-js/edgeMinMax_for_genesymbol.js")

    final_js = (
        template.replace(
            "XXX_FILTER_BY_NODE_COLOR_AND_EDGE_SIZE",
            insert_filterByNodeColorAndEdgeSize,
        )
        .replace("XXX_NODE_MIN_MAX", "")
        .replace("XXX_EDGE_MIN_MAX", insert_edgeMinMax)
        .replace("XXX_ELEMENTS", "loadJSONGz('../../data/genesymbol/XXX_NAME.json.gz')")
        .replace("XXX_PHENOTYPE", "")
        .replace("XXX_NAME", gene_symbol)
    )

    _write_file(f"{output_dir}/app/genesymbol/{gene_symbol}.js", final_js)


def generate_gene_pages(records_significants, targetted_gene_symbols, output_dir) -> None:
    map_marker_symbol_to_impc_url_gene = {}
    for record in records_significants:
        marker_symbol = record["marker_symbol"]
        marker_accession_id = record["marker_accession_id"]
        impc_url_gene = f"https://www.mousephenotype.org/data/genes/{marker_accession_id}"
        map_marker_symbol_to_impc_url_gene[marker_symbol] = impc_url_gene

    for gene_symbol in tqdm(targetted_gene_symbols, desc="Processing gene symbols"):
        impc_url_gene = map_marker_symbol_to_impc_url_gene.get(gene_symbol)
        _generate_gene_html(gene_symbol, impc_url_gene, output_dir)
        _generate_gene_javascript(gene_symbol, output_dir)


# ---------------------------------------------------------
# Gene List
# ---------------------------------------------------------


def _generate_genelist_html(output_dir: str | Path) -> None:
    for part in ["body-container", "cy-container"]:
        template_path = f"{output_dir}/template/template-app-html/{part}.html"
        output_path = f"/tmp/{part}.html"
        _generate_simple_html(template_path, output_path, {"XXX_PHENOTYPE_SEVERITY": ""})

    # head.html
    _generate_simple_html(
        f"{output_dir}/template/template-app-html/head.html",
        "/tmp/head.html",
        {"XXX_TITLE": "Gene List", "XXX_JS_FILE_NAME": "network_genelist"},
    )

    # header.html
    header_insert = "gene list"
    _generate_simple_html(
        f"{output_dir}/template/template-app-html/header.html",
        "/tmp/header.html",
        {"XXX_TITLE": header_insert},
    )

    # template_app.html
    template = _read_file(f"{output_dir}/template/template-app-html/template_app.html")
    final_html = (
        template.replace("XXX_HEAD", _read_file("/tmp/head.html"))
        .replace("XXX_H1", _read_file("/tmp/header.html"))
        .replace("XXX_BODY_CONTAINER", _read_file("/tmp/body-container.html"))
        .replace("XXX_CY_CONTAINER", _read_file("/tmp/cy-container.html"))
    )

    _write_file(f"{output_dir}/app/genelist/network_genelist.html", final_html)


def _generate_genelist_javascript(output_dir: str | Path) -> None:
    template_lines = _read_file(f"{output_dir}/template/template-app-js/template_app.js").splitlines()
    filtered_lines = [
        line
        for line in template_lines
        if "XXX_NODE_COLOR_INITIALIZATION" not in line and "XXX_NODE_COLOR_UPDATE" not in line
    ]
    _write_file("/tmp/template_app.js", "\n".join(filtered_lines))

    template = _read_file("/tmp/template_app.js")
    insert = _read_file(f"{output_dir}/template/template-app-js/filterByNodeColorAndEdgeSize_genelist.js")

    final_js = (
        template.replace("XXX_FILTER_BY_NODE_COLOR_AND_EDGE_SIZE", insert)
        .replace("XXX_NODE_MIN_MAX", "")
        .replace(
            "XXX_EDGE_MIN_MAX",
            "const edgeMin = Math.min(...edgeSizes); const edgeMax = Math.max(...edgeSizes);",
        )
        .replace("XXX_ELEMENTS", "JSON.parse(localStorage.getItem('elements'))")
        .replace("XXX_PHENOTYPE", "")
        .replace("XXX_NAME", "geneList")
    )

    _write_file(f"{output_dir}/app/genelist/network_genelist.js", final_js)


def generate_genelist_page(output_dir) -> None:
    _generate_genelist_html(output_dir)
    _generate_genelist_javascript(output_dir)

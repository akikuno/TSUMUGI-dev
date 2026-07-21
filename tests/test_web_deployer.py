from TSUMUGI import web_deployer


def test_copy_json_files_includes_gene_modules(tmp_path):
    tempdir = tmp_path / ".tempdir"
    output_dir = tmp_path / "TSUMUGI-webapp"
    phenotype_dir = tempdir / "network" / "phenotype"
    gene_dir = tempdir / "network" / "genesymbol"
    gene_module_dir = tempdir / "network" / "genesymbol_modules"
    phenotype_dir.mkdir(parents=True)
    gene_dir.mkdir(parents=True)
    gene_module_dir.mkdir(parents=True)

    (phenotype_dir / "target_phenotype.json.gz").write_text("phenotype", encoding="utf-8")
    (gene_dir / "GeneA.json.gz").write_text("gene", encoding="utf-8")
    (gene_module_dir / "GeneA.json.gz").write_text("module", encoding="utf-8")

    web_deployer._copy_json_files({"target phenotype"}, {"GeneA"}, tempdir, output_dir)

    assert (output_dir / "data" / "phenotype" / "target_phenotype.json.gz").read_text(encoding="utf-8") == "phenotype"
    assert (output_dir / "data" / "genesymbol" / "GeneA.json.gz").read_text(encoding="utf-8") == "gene"
    assert (output_dir / "data" / "genesymbol_modules" / "GeneA.json.gz").read_text(encoding="utf-8") == "module"

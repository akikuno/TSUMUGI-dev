import gzip
import json
from io import StringIO
from unittest.mock import patch

import pytest
from TSUMUGI.subcommands.mp_filterer import exclude_specific_phenotype, include_specific_phenotype


# --- Test Data Generation ---
@pytest.fixture
def test_obo_content():
    return """
[Term]
id: MP:0000001
name: mammalian phenotype
is_a: OBO:SUPER_TERM

[Term]
id: MP:0000002
name: vertebral transformation
is_a: MP:0000001

[Term]
id: MP:0000003
name: abnormal vertebral column morphology
is_a: MP:0000002

[Term]
id: MP:0000004
name: abnormal immune system physiology

[Term]
id: MP:0000005
name: obsolete term
is_obsolete: true
"""


@pytest.fixture
def test_genewise_phenotype_annotations_content():
    return [
        {
            "mp_term_name": "vertebral transformation",
            "mp_term_id": "MP:0000002",
            "significant": True,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneA",
        },
        {
            "mp_term_name": "mammalian phenotype",
            "mp_term_id": "MP:0000001",
            "significant": False,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneA",
        },
        {
            "mp_term_name": "abnormal immune system physiology",
            "mp_term_id": "MP:0000004",
            "significant": True,
            "zygosity": "Hetero",
            "life_stage": "Late",
            "sexual_dimorphism": "Female",
            "marker_symbol": "GeneA",
        },
        {
            "mp_term_name": "abnormal vertebral column morphology",
            "mp_term_id": "MP:0000003",
            "significant": True,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneB",
        },
        {
            "mp_term_name": "vertebral transformation",
            "mp_term_id": "MP:0000002",
            "significant": False,
            "zygosity": "Homo",
            "life_stage": "Late",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneB",
        },
        {
            "mp_term_name": "mammalian phenotype",
            "mp_term_id": "MP:0000001",
            "significant": True,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneC",
        },
        {
            "mp_term_name": "abnormal immune system physiology",
            "mp_term_id": "MP:0000004",
            "significant": False,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneC",
        },
        {
            "mp_term_name": "obsolete term",
            "mp_term_id": "MP:0000005",
            "significant": True,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneD",
        },  # Obsolete term
        {
            "mp_term_name": "vertebral transformation",
            "mp_term_id": "MP:0000002",
            "significant": False,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneD",
        },
        {
            "mp_term_name": "some other phenotype",
            "mp_term_id": "MP:0000004",
            "significant": False,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneE",
        },
        {
            "mp_term_name": "vertebral transformation",
            "mp_term_id": "MP:0000002",
            "significant": False,
            "zygosity": "Homo",
            "life_stage": "Early",
            "sexual_dimorphism": "Male",
            "marker_symbol": "GeneE",
        },  # Added for GeneE to be 'without phenotype'
    ]


@pytest.fixture
def test_pairwise_similarity_annotations_content():
    return [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "vertebral transformation",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                },
                {
                    "mp_term_name": "abnormal vertebral column morphology",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                },
            ],
            "phenotype_similarity_score": 42,
        },
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneC",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "mammalian phenotype",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                },
                {
                    "mp_term_name": "abnormal immune system physiology",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                },
            ],
            "phenotype_similarity_score": 54,
        },
        {
            "gene1_symbol": "GeneB",
            "gene2_symbol": "GeneC",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "vertebral transformation",
                    "zygosity": "Homo",
                    "life_stage": "Late",
                    "sexual_dimorphism": "Male",
                }
            ],
            "phenotype_similarity_score": 63,
        },
        {
            "gene1_symbol": "GeneC",
            "gene2_symbol": "GeneD",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "obsolete term",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                }
            ],  # Obsolete term
            "phenotype_similarity_score": 70,
        },
        {
            "gene1_symbol": "GeneD",
            "gene2_symbol": "GeneE",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "random phenotype",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                }
            ],
            "phenotype_similarity_score": 80,
        },  # This pair should be output
        {
            "gene1_symbol": "GeneX",
            "gene2_symbol": "GeneY",
            "phenotype_shared_annotations": [
                {
                    "mp_term_name": "some other phenotype",
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                }
            ],
            "phenotype_similarity_score": 10,
        },
    ]


@pytest.fixture
def setup_test_files(
    tmp_path,
    test_obo_content,
    test_genewise_phenotype_annotations_content,
    test_pairwise_similarity_annotations_content,
):
    """Set up temporary test files."""
    path_obo = tmp_path / "test.obo"
    path_obo.write_text(test_obo_content)

    path_genewise = tmp_path / "genewise_phenotype_annotations.jsonl.gz"
    with gzip.open(path_genewise, "wt", encoding="utf-8") as f:
        for record in test_genewise_phenotype_annotations_content:
            f.write(json.dumps(record) + "\n")

    path_pairwise = tmp_path / "pairwise_similarity_annotations.jsonl.gz"
    with gzip.open(path_pairwise, "wt", encoding="utf-8") as f:
        for record in test_pairwise_similarity_annotations_content:
            f.write(json.dumps(record) + "\n")

    return path_obo, path_genewise, path_pairwise


# --- Tests for exclude_specific_phenotype ---
@patch("sys.stdout", new_callable=StringIO)
def test_exclude_specific_phenotype_basic(mock_stdout, setup_test_files):
    """
    Test basic exclusion: exclude gene pairs where at least one gene has the
    target phenotype (MP:0000002 or its descendant/ancestor) significantly.
    GeneA has MP:0000002 significant. GeneB has MP:0000003 significant.
    GeneC has MP:0000001 significant.
    GeneD has MP:0000002 not significant.
    """
    path_obo, path_genewise, path_pairwise = setup_test_files
    # For MP:0000002, GeneA (MP:0000002, significant), GeneB (MP:0000003, significant)
    # GeneC (MP:0000001, significant) are considered to have the phenotype.
    # GeneD (MP:0000002, not significant) is considered not to have the phenotype.
    # So, GeneD should remain.
    exclude_specific_phenotype(
        path_pairwise_similarity_annotations=path_pairwise,
        path_genewise_phenotype_annotations=path_genewise,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n") if line.strip()]
    assert len(output) == 1
    assert output[0]["gene1_symbol"] == "GeneD"
    assert output[0]["gene2_symbol"] == "GeneE"


@patch("sys.stdout", new_callable=StringIO)
def test_exclude_specific_phenotype_with_conditions(mock_stdout, setup_test_files):
    """
    Test exclusion with life_stage, sex, and zygosity conditions.
    Exclude 'vertebral transformation' (MP:0000002) for Homo, Early, Male.
    GeneA (MP:0000002, significant, Homo, Early, Male) -> has phenotype
    GeneB (MP:0000003, significant, Homo, Early, Male) -> has phenotype
    GeneC (MP:0000001, significant, Homo, Early, Male) -> has phenotype
    GeneD (MP:0000002, not significant, Homo, Early, Male) -> no phenotype (due to not significant)
    """
    path_obo, path_genewise, path_pairwise = setup_test_files
    exclude_specific_phenotype(
        path_pairwise_similarity_annotations=path_pairwise,
        path_genewise_phenotype_annotations=path_genewise,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
        life_stage="Early",
        sex="Male",
        zygosity="Homo",
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n") if line.strip()]
    assert len(output) == 1
    assert output[0]["gene1_symbol"] == "GeneD"
    assert output[0]["gene2_symbol"] == "GeneE"


@patch("sys.stdout", new_callable=StringIO)
def test_exclude_specific_phenotype_produces_output(mock_stdout, setup_test_files):
    """
    Test that exclude_specific_phenotype produces output when both genes in a pair
    are considered to not have the target phenotype.
    GeneD (MP:0000002 not significant) -> no phenotype
    GeneE (MP:0000002 not significant) -> no phenotype
    Expected output: GeneD-GeneE pair
    """
    path_obo, path_genewise, path_pairwise = setup_test_files
    exclude_specific_phenotype(
        path_pairwise_similarity_annotations=path_pairwise,
        path_genewise_phenotype_annotations=path_genewise,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n") if line.strip()]
    assert len(output) == 1
    assert output[0]["gene1_symbol"] == "GeneD"
    assert output[0]["gene2_symbol"] == "GeneE"


# --- Tests for include_specific_phenotype ---
@patch("sys.stdout", new_callable=StringIO)
def test_include_specific_phenotype_basic(mock_stdout, setup_test_files):
    """
    Test basic inclusion: include gene pairs that share 'vertebral transformation' (MP:0000002)
    or its descendant 'abnormal vertebral column morphology' (MP:0000003).
    """
    path_obo, _, path_pairwise = setup_test_files
    include_specific_phenotype(
        path_pairwise_similarity_annotations=path_pairwise,
        path_genewise_phenotype_annotations=None,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n")]
    # Expected: GeneA-GeneB and GeneB-GeneC
    # GeneA-GeneB has "vertebral transformation" and "abnormal vertebral column morphology"
    # GeneA-GeneC has "mammalian phenotype" and "abnormal immune system physiology"
    # GeneB-GeneC has "vertebral transformation"
    # GeneC-GeneD has "obsolete term"
    assert len(output) == 2
    assert any(record["gene1_symbol"] == "GeneA" and record["gene2_symbol"] == "GeneB" for record in output)
    assert any(record["gene1_symbol"] == "GeneB" and record["gene2_symbol"] == "GeneC" for record in output)


def test_include_specific_phenotype_invalid_structure_raises(tmp_path, test_obo_content, monkeypatch):
    path_obo = tmp_path / "test.obo"
    path_obo.write_text(test_obo_content)

    invalid_pairwise = [
        {
            "gene1_symbol": "GeneA",
            "gene2_symbol": "GeneB",
            "phenotype_shared_annotations": {
                "vertebral transformation": {
                    "zygosity": "Homo",
                    "life_stage": "Early",
                    "sexual_dimorphism": "Male",
                }
            },
            "phenotype_similarity_score": 42,
        }
    ]

    monkeypatch.setattr("TSUMUGI.subcommands.mp_filterer.io_handler.read_jsonl", lambda path: invalid_pairwise)

    with pytest.raises(TypeError):
        include_specific_phenotype(
            path_pairwise_similarity_annotations="pairwise-path",
            path_genewise_phenotype_annotations=None,
            path_obo=path_obo,
            mp_term_id="MP:0000002",
        )


@patch("sys.stdout", new_callable=StringIO)
def test_include_specific_phenotype_with_conditions(mock_stdout, setup_test_files):
    """
    Test inclusion with life_stage, sex, and zygosity conditions.
    Include 'vertebral transformation' (MP:0000002) for Homo, Early, Male.
    """
    path_obo, _, path_pairwise = setup_test_files
    include_specific_phenotype(
        path_pairwise_similarity_annotations=path_pairwise,
        path_genewise_phenotype_annotations=None,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
        life_stage="Early",
        sex="Male",
        zygosity="Homo",
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n")]
    # Expected: GeneA-GeneB.
    # GeneA-GeneB: "vertebral transformation" (Homo, Early, Male), "abnormal vertebral column morphology" (Homo, Early, Male)
    # GeneB-GeneC: "vertebral transformation" (Homo, Late, Male) -> does not match life_stage
    assert len(output) == 1
    assert output[0]["gene1_symbol"] == "GeneA"
    assert output[0]["gene2_symbol"] == "GeneB"


@patch("sys.stdout", new_callable=StringIO)
def test_include_specific_phenotype_genewise_significant_only(mock_stdout, setup_test_files):
    """Ensure genewise inclusion keeps only significant annotations for descendant terms."""
    path_obo, path_genewise, _ = setup_test_files
    include_specific_phenotype(
        path_pairwise_similarity_annotations=None,
        path_genewise_phenotype_annotations=path_genewise,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
        is_pairwise=False,
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n") if line.strip()]
    assert {record["marker_symbol"] for record in output} == {"GeneA", "GeneB"}
    assert all(record["significant"] is True for record in output)


@patch("sys.stdout", new_callable=StringIO)
def test_include_specific_phenotype_genewise_filters_metadata(mock_stdout, setup_test_files):
    """
    Metadata filters should exclude non-significant descendant annotations (only Late entries are non-significant).
    """
    path_obo, path_genewise, _ = setup_test_files
    include_specific_phenotype(
        path_pairwise_similarity_annotations=None,
        path_genewise_phenotype_annotations=path_genewise,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
        life_stage="Late",
        sex="Male",
        zygosity="Homo",
        is_pairwise=False,
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n") if line.strip()]
    assert output == []


@patch("sys.stdout", new_callable=StringIO)
def test_exclude_specific_phenotype_genewise(mock_stdout, setup_test_files):
    """Genes confirmed without the target phenotype should be emitted with their annotations."""
    path_obo, path_genewise, _ = setup_test_files
    exclude_specific_phenotype(
        path_pairwise_similarity_annotations=None,
        path_genewise_phenotype_annotations=path_genewise,
        path_obo=path_obo,
        mp_term_id="MP:0000002",
        is_pairwise=False,
    )
    output = [json.loads(line) for line in mock_stdout.getvalue().strip().split("\n") if line.strip()]
    assert len(output) == 4
    assert {record["marker_symbol"] for record in output} == {"GeneD", "GeneE"}
    assert all(record["marker_symbol"] not in {"GeneA", "GeneB", "GeneC"} for record in output)

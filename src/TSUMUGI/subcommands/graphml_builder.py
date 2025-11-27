import io
import sys
from collections import defaultdict

import networkx as nx

from TSUMUGI import io_handler


def format_suffix(zygosity: str, life_stage: str, sexual_dimorphism: str) -> str:
    """Produce strings like (Homo, Early, Male); omit sexual_dimorphism when it equals 'None'."""
    parts = [zygosity, life_stage]
    if sexual_dimorphism and sexual_dimorphism != "None":
        parts.append(sexual_dimorphism)
    return f"({', '.join(parts)})"


def build_nodes(genewise_phenotype_annotations: list[dict]) -> dict:
    """
    Read genewise_phenotype_annotations.jsonl.gz and aggregate node attributes per marker_symbol.
    - node_id: marker_symbol
    - label: marker_symbol
    - effect_size: always 1
    - node_annotations:
        Phenotypes of GeneA KO mice
        - vertebral transformation (Homo, Early, Male)
        ...
        Associated Human Diseases
        - Male infertility (Homo, Early)
        ...
    """
    phenotypes_per_gene = defaultdict(list)
    diseases_per_gene = defaultdict(list)

    for record in genewise_phenotype_annotations:
        marker_symbol = record["marker_symbol"]
        mp_term_name = record["mp_term_name"]
        zygosity = record["zygosity"]
        life_stage = record["life_stage"]
        sexual_dimorphism = record.get("sexual_dimorphism", "None")
        disease_annotation = record.get("disease_annotation", [])

        suffix = format_suffix(zygosity, life_stage, sexual_dimorphism)

        # KO mouse phenotypes
        pheno_text = f"{mp_term_name} {suffix}"
        phenotypes_per_gene[marker_symbol].append(pheno_text)

        # Human diseases
        for d in disease_annotation:
            disease_text = f"{d} {suffix}"
            diseases_per_gene[marker_symbol].append(disease_text)

    nodes = {}
    for marker_symbol in phenotypes_per_gene.keys() | diseases_per_gene.keys():
        lines = []

        # Phenotypes section
        lines.append(f"Phenotypes of {marker_symbol} KO mice")
        for pheno in phenotypes_per_gene.get(marker_symbol, []):
            lines.append(f"- {pheno}")

        # Diseases section (if available)
        diseases = diseases_per_gene.get(marker_symbol, [])
        if diseases:
            lines.append("Associated Human Diseases")
            for dis in diseases:
                lines.append(f"- {dis}")

        node_annotations = "\n".join(lines)

        nodes[marker_symbol] = {
            "label": marker_symbol,
            "effect_size": 1.0,
            "node_annotations": node_annotations,
        }

    return nodes


def build_graph(pairwise_similarity_annotations: list[dict], nodes: dict) -> nx.Graph:
    """
    Build a Graph using pairwise_similarity_annotations and the supplied nodes.
    - Nodes: add the contents from nodes (and create empty nodes for unseen genes)
    - Edges: gene1_symbol, gene2_symbol
        - weight: phenotype_similarity_score
        - edge_annotations:
          Shared phenotypes of GeneA and GeneB KOs (Similarity: 59)
          - vertebral transformation (Homo, Early, Male)
          ...
    """
    G = nx.Graph()

    edge_id = 0  # Place outside the loop so multiple edges get sequential IDs
    geneset = set()
    # Add edges
    for record in pairwise_similarity_annotations:
        g1 = record["gene1_symbol"]
        g2 = record["gene2_symbol"]
        score = record["phenotype_similarity_score"]
        shared = record.get("phenotype_shared_annotations", {})

        # Add missing nodes (genes absent from the genewise data)
        if g1 not in G:
            G.add_node(g1, label=g1, effect_size=1.0, node_annotations="")
        if g2 not in G:
            G.add_node(g2, label=g2, effect_size=1.0, node_annotations="")

        # Format phenotype_shared_annotations
        edge_texts = []
        for mp_term_name, meta in shared.items():
            zygosity = meta.get("zygosity", "")
            life_stage = meta.get("life_stage", "")
            sexual_dimorphism = meta.get("sexual_dimorphism", "None")
            suffix = format_suffix(zygosity, life_stage, sexual_dimorphism)
            edge_texts.append(f"{mp_term_name} {suffix}")

        lines = []
        lines.append(f"Shared phenotypes of {g1} and {g2} KOs (Similarity: {score})")
        for txt in edge_texts:
            lines.append(f"- {txt}")

        edge_annotations = "\n".join(lines)

        G.add_edge(
            g1,
            g2,
            id=f"e{edge_id}",
            weight=score,
            edge_annotations=edge_annotations,
        )
        edge_id += 1
        geneset.add(g1)
        geneset.add(g2)

    # Add nodes
    for node_id, attrs in nodes.items():
        if node_id in geneset:
            G.add_node(node_id, **attrs)

    return G


def write_graphml_to_stdout(pairwise_path: str, genewise_path: str) -> None:
    """
    Write GraphML to stdout using pairwise_similarity_annotations.jsonl.gz
    and genewise_phenotype_annotations.jsonl.gz.
    """
    pairwise_similarity_annotations = io_handler.read_jsonl(pairwise_path)
    genewise_phenotype_annotations = io_handler.read_jsonl(genewise_path)

    nodes = build_nodes(genewise_phenotype_annotations)
    G = build_graph(pairwise_similarity_annotations, nodes)

    text_buffer = io.StringIO()
    nx.write_graphml(G, text_buffer, encoding="unicode")

    sys.stdout.write(text_buffer.getvalue())

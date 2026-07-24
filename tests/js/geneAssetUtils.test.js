import assert from "node:assert/strict";
import test from "node:test";

import {
    buildInducedGeneElements,
    normalizeGeneInput,
    selectGeneDisplayIds,
    validateGeneListRequestGenes,
} from "../../src/TSUMUGI/web/js/geneAssetUtils.js";

function node(gene) {
    return {
        data: {
            id: gene,
            label: gene,
            phenotype: [`phenotype (${gene})`],
            disease: "",
            node_color: 100,
        },
    };
}

function edge(source, target, score, sharedContexts) {
    return {
        data: {
            source,
            target,
            phenotype: [`shared phenotype (${source}, ${target})`],
            phenotype_similarity_score: score,
            shared_context_count: sharedContexts,
        },
    };
}

function asset(gene, directEdges) {
    return {
        schema_version: 2,
        gene,
        node: node(gene),
        direct_edges: directEdges,
    };
}

test("normalizeGeneInput trims blanks and removes exact duplicates", () => {
    assert.deepEqual(normalizeGeneInput(" Ghrh\n\nGhrhr\nGhrh\n"), ["Ghrh", "Ghrhr"]);
});

test("validateGeneListRequestGenes accepts 200 unique genes and rejects 201", () => {
    const genes = Array.from({ length: 201 }, (_, index) => `Gene${index}`);
    assert.equal(validateGeneListRequestGenes(genes.slice(0, 200)).length, 200);
    assert.throws(() => validateGeneListRequestGenes(genes), /limited to 200 genes/);
});

test("selectGeneDisplayIds ranks only direct target edges", () => {
    const geneA = asset("GeneA", [
        edge("GeneA", "GeneB", 80, 3),
        edge("GeneA", "GeneC", 90, 3),
        edge("GeneA", "GeneD", 100, 2),
    ]);

    assert.deepEqual(selectGeneDisplayIds(geneA, { maxNodes: 3 }), ["GeneA", "GeneC", "GeneB"]);
});

test("selectGeneDisplayIds uses the same code-point tie break as the Python builder", () => {
    const geneA = asset("GeneA", [
        edge("GeneA", "Gene2", 80, 3),
        edge("GeneA", "Gene10", 80, 3),
    ]);

    assert.deepEqual(selectGeneDisplayIds(geneA, { maxNodes: 3 }), ["GeneA", "Gene10", "Gene2"]);
});

test("buildInducedGeneElements includes the edge between selected neighbors", () => {
    const ab = edge("GeneA", "GeneB", 90, 3);
    const ac = edge("GeneA", "GeneC", 80, 3);
    const bc = edge("GeneB", "GeneC", 70, 3);
    const elements = buildInducedGeneElements(
        [
            asset("GeneA", [ab, ac]),
            asset("GeneB", [ab, bc]),
            asset("GeneC", [ac, bc]),
        ],
        ["GeneA", "GeneB", "GeneC"],
        { minSharedContexts: 3, targetGene: "GeneA" },
    );

    const edgePairs = elements
        .filter((element) => element.data.source)
        .map((element) => `${element.data.source}||${element.data.target}`);
    assert.deepEqual(edgePairs, ["GeneA||GeneB", "GeneA||GeneC", "GeneB||GeneC"]);
    assert.equal(elements.find((element) => element.data.id === "GeneA").data.node_color, 100);
    assert.equal(elements.find((element) => element.data.id === "GeneB").data.node_color, 1);
});

test("buildInducedGeneElements keeps single-context edges for Gene List", () => {
    const pair = edge("Ghrh", "Ghrhr", 83, 1);
    const elements = buildInducedGeneElements(
        [asset("Ghrh", [pair]), asset("Ghrhr", [pair])],
        ["Ghrh", "Ghrhr"],
        { minSharedContexts: 1 },
    );

    const result = elements.find((element) => element.data.source === "Ghrh");
    assert.equal(result.data.phenotype_similarity_score, 83);
    assert.equal(result.data.edge_size, 100);
});

test("buildInducedGeneElements rejects conflicting duplicate edge payloads", () => {
    assert.throws(
        () =>
            buildInducedGeneElements(
                [
                    asset("GeneA", [edge("GeneA", "GeneB", 80, 3)]),
                    asset("GeneB", [edge("GeneA", "GeneB", 79, 3)]),
                ],
                ["GeneA", "GeneB"],
            ),
        /Conflicting direct edge payload/,
    );
});

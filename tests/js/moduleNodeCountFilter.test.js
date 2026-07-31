import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
    collectModuleElementIds,
    createModuleDescriptor,
    createStableSimilarityModuleId,
    filterModulesByNodeCount,
    getModuleNodeCount,
    isFullNodeCountRange,
    isModuleWithinNodeCountRange,
} from "../../src/TSUMUGI/web/app/js/graph/moduleNodeCountFilter.js";

function moduleWithNodes(id, nodeIds, edgeIds = []) {
    return createModuleDescriptor({
        id,
        label: id,
        nodeIds,
        edgeIds,
    });
}

test("node count range includes both boundaries", () => {
    const module = moduleWithNodes("three", ["A", "B", "C"]);

    assert.equal(isModuleWithinNodeCountRange(module, 3, 3), true);
    assert.equal(isModuleWithinNodeCountRange(module, 1, 3), true);
    assert.equal(isModuleWithinNodeCountRange(module, 3, 5), true);
    assert.equal(isModuleWithinNodeCountRange(module, 4, 5), false);
});

test("node count filtering handles two, three, and four node modules", () => {
    const modules = [
        moduleWithNodes("two", ["A", "B"]),
        moduleWithNodes("three", ["A", "B", "C"]),
        moduleWithNodes("four", ["A", "B", "C", "D"]),
    ];

    assert.deepEqual(filterModulesByNodeCount(modules, 3, 4).map((module) => module.id), ["three", "four"]);
    assert.deepEqual(filterModulesByNodeCount(modules, 1, 3).map((module) => module.id), ["two", "three"]);
    assert.deepEqual(filterModulesByNodeCount(modules, 5, 8), []);
});

test("module node counts use unique node identifiers", () => {
    const module = moduleWithNodes("duplicate", ["B", "A", "A"]);

    assert.deepEqual(module.nodeIds, ["A", "B"]);
    assert.equal(getModuleNodeCount(module), 2);
});

test("overlapping modules produce a union of nodes and edges", () => {
    const union = collectModuleElementIds([
        moduleWithNodes("first", ["A", "B"], ["A||B"]),
        moduleWithNodes("second", ["B", "C"], ["B||C"]),
    ]);

    assert.deepEqual([...union.nodeIds].sort(), ["A", "B", "C"]);
    assert.deepEqual([...union.edgeIds].sort(), ["A||B", "B||C"]);
});

test("an empty module selection produces empty element sets", () => {
    const union = collectModuleElementIds([]);

    assert.equal(union.nodeIds.size, 0);
    assert.equal(union.edgeIds.size, 0);
});

test("similarity module identifiers are stable across input order", () => {
    assert.equal(
        createStableSimilarityModuleId(["GeneC", "GeneA", "GeneB"]),
        createStableSimilarityModuleId(["GeneB", "GeneC", "GeneA"]),
    );
    assert.equal(createStableSimilarityModuleId(["Gene A", "Gene/B"]), "similarity:Gene%20A|Gene%2FB");
});

test("full-range detection distinguishes narrowed ranges", () => {
    assert.equal(isFullNodeCountRange([1, 10], 1, 10), true);
    assert.equal(isFullNodeCountRange([10, 1], 1, 10), true);
    assert.equal(isFullNodeCountRange([2, 10], 1, 10), false);
    assert.equal(isFullNodeCountRange([1, 9], 1, 10), false);
});

test("network structure controls follow biological annotations in the left panel", () => {
    const viewerHtmlUrl = new URL("../../src/TSUMUGI/web/app/viewer.html", import.meta.url);
    const viewerHtml = readFileSync(viewerHtmlUrl, "utf8");
    const biologicalIndex = viewerHtml.indexOf("Biological annotations");
    const networkIndex = viewerHtml.indexOf('id="network-structure-controls"');
    const nodeCountSliderIndex = viewerHtml.indexOf('id="module-node-count-slider"');
    const cytoscapePanelIndex = viewerHtml.indexOf('class="cy-container"');
    const rightPanelIndex = viewerHtml.indexOf('class="right-control-panel-container"');

    assert.ok(biologicalIndex >= 0);
    assert.ok(networkIndex > biologicalIndex);
    assert.ok(nodeCountSliderIndex > networkIndex);
    assert.ok(cytoscapePanelIndex > nodeCountSliderIndex);
    assert.ok(rightPanelIndex > cytoscapePanelIndex);
    assert.equal(viewerHtml.lastIndexOf('id="module-node-count-slider"'), nodeCountSliderIndex);
});

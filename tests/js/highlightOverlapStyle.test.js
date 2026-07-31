import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const viewerUrl = new URL("../../src/TSUMUGI/web/app/viewer.js", import.meta.url);
const viewerSource = readFileSync(viewerUrl, "utf8");

function extractStyleRule(selector) {
    const start = viewerSource.indexOf(`selector: "${selector}"`);
    assert.notEqual(start, -1, `Missing Cytoscape selector: ${selector}`);

    const end = viewerSource.indexOf("\n        },", start);
    assert.notEqual(end, -1, `Could not find the end of the ${selector} rule`);
    return viewerSource.slice(start, end);
}

test("overlap style renders phenotype inside disease", () => {
    const diseaseIndex = viewerSource.indexOf('selector: ".disease-highlight"');
    const phenotypeIndex = viewerSource.indexOf('selector: ".phenotype-highlight"');
    const overlapIndex = viewerSource.indexOf('selector: "node.disease-highlight.phenotype-highlight"');
    const overlapRule = extractStyleRule("node.disease-highlight.phenotype-highlight");

    assert.notEqual(diseaseIndex, -1);
    assert.notEqual(phenotypeIndex, -1);
    assert.ok(overlapIndex > diseaseIndex);
    assert.ok(overlapIndex > phenotypeIndex);
    assert.match(overlapRule, /"border-width": 5/);
    assert.match(overlapRule, /"border-color": "#3FA7D6"/);
    assert.match(overlapRule, /"outline-width": 5/);
    assert.match(overlapRule, /"outline-color": "#fc4c00"/);
    assert.match(overlapRule, /"outline-offset": 3/);
    assert.match(overlapRule, /"bounds-expansion": 8/);
});

test("overlap style preserves the node body dimensions", () => {
    const overlapRule = extractStyleRule("node.disease-highlight.phenotype-highlight");

    assert.doesNotMatch(overlapRule, /"width":/);
    assert.doesNotMatch(overlapRule, /"height":/);
});

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
    hideAllGraphElements,
    resolveActiveFilterValues,
} from "../../src/TSUMUGI/web/app/js/graph/filters.js";

const viewerHtmlUrl = new URL("../../src/TSUMUGI/web/app/viewer.html", import.meta.url);
const viewerHtml = readFileSync(viewerHtmlUrl, "utf8");
const viewerJsUrl = new URL("../../src/TSUMUGI/web/app/viewer.js", import.meta.url);
const viewerJs = readFileSync(viewerJsUrl, "utf8");

function getFormHtml(formId) {
    const match = viewerHtml.match(new RegExp(`<form id="${formId}"[\\s\\S]*?<\\/form>`));
    assert.ok(match, `Could not find ${formId}`);
    return match[0];
}

function getInputTags(formHtml) {
    return [...formHtml.matchAll(/<input\b[^>]*>/g)].map((match) => match[0]);
}

test("sex filter uses one native radio group with All selected initially", () => {
    const inputTags = getInputTags(getFormHtml("sex-filter-form"));

    assert.equal(inputTags.length, 3);
    inputTags.forEach((tag) => {
        assert.match(tag, /type="radio"/);
        assert.match(tag, /name="sex-filter"/);
    });
    assert.deepEqual(
        inputTags.map((tag) => tag.match(/value="([^"]+)"/)?.[1]),
        ["All", "Female", "Male"],
    );
    assert.equal(inputTags.filter((tag) => /\schecked(?:\s|\/|>)/.test(tag)).length, 1);
    assert.match(inputTags[0], /\schecked(?:\s|\/|>)/);
});

test("genotype and life-stage filters remain multi-select checkboxes", () => {
    ["genotype-filter-form", "lifestage-filter-form"].forEach((formId) => {
        const inputTags = getInputTags(getFormHtml(formId));
        assert.ok(inputTags.length > 1);
        inputTags.forEach((tag) => assert.match(tag, /type="checkbox"/));
    });
});

test("active filter values preserve individual and multi-select choices", () => {
    const allSexes = ["Female", "Male"];
    const allGenotypes = ["Homo", "Hetero", "Hemi"];
    const allLifeStages = ["Embryo", "Early", "Interval", "Late"];

    assert.deepEqual(resolveActiveFilterValues(["All"], allSexes), allSexes);
    assert.deepEqual(resolveActiveFilterValues([], allSexes), allSexes);
    assert.deepEqual(resolveActiveFilterValues(["Female"], allSexes), ["Female"]);
    assert.deepEqual(resolveActiveFilterValues(["Male"], allSexes), ["Male"]);
    assert.deepEqual(resolveActiveFilterValues(["Homo", "Hetero"], allGenotypes), ["Homo", "Hetero"]);
    assert.deepEqual(resolveActiveFilterValues(["Early", "Late"], allLifeStages), ["Early", "Late"]);
});

test("empty gene network hides every graph element and clears base visibility", () => {
    const displays = new Map();
    const visibility = new Map();
    const elements = ["node-a", "node-b", "edge-a-b"].map((id) => ({
        id: () => id,
        style: (name, value) => {
            assert.equal(name, "display");
            displays.set(id, value);
        },
    }));
    let batchCalls = 0;
    const cy = {
        batch: (callback) => {
            batchCalls += 1;
            callback();
        },
        elements: () => elements,
    };

    hideAllGraphElements(cy, (element, isVisible) => {
        visibility.set(element.id(), isVisible);
    });

    assert.equal(batchCalls, 1);
    assert.deepEqual([...displays.values()], ["none", "none", "none"]);
    assert.deepEqual([...visibility.values()], [false, false, false]);
});

test("missing Gene Symbol target hides graph elements before showing the empty state", () => {
    const branchStart = viewerJs.indexOf("if (targetNode.length === 0)");
    const branchEnd = viewerJs.indexOf("const directlyConnectedNodes", branchStart);
    assert.ok(branchStart >= 0, "Could not find the missing target branch");
    assert.ok(branchEnd > branchStart, "Could not find the end of the missing target branch");

    const branch = viewerJs.slice(branchStart, branchEnd);
    const hideIndex = branch.indexOf("hideAllGraphElements");
    const messageIndex = branch.indexOf("updateNoNodesMessage(true)");
    const returnIndex = branch.indexOf("return");

    assert.ok(hideIndex >= 0);
    assert.ok(messageIndex > hideIndex);
    assert.ok(returnIndex > messageIndex);
});

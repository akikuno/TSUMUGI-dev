import assert from "node:assert/strict";
import test from "node:test";

import {
    getPhenotypeTermName,
    getPhenotypeTermNames,
    hasSelectedPhenotype,
    normalizePhenotypes,
} from "../../src/TSUMUGI/web/app/js/data/phenotypeAnnotations.js";

test("getPhenotypeTermName removes generated phenotype metadata", () => {
    assert.equal(
        getPhenotypeTermName("abnormal glucose homeostasis (Hetero, Early, Male)"),
        "abnormal glucose homeostasis",
    );
    assert.equal(
        getPhenotypeTermName("abnormal glucose homeostasis (Homo, Early)"),
        "abnormal glucose homeostasis",
    );
    assert.equal(
        getPhenotypeTermName("abnormal glucose homeostasis (Homo, Early, Female)"),
        "abnormal glucose homeostasis",
    );
    assert.equal(
        getPhenotypeTermName("abnormal glucose homeostasis (Hemi)"),
        "abnormal glucose homeostasis",
    );
});

test("getPhenotypeTermName preserves non-metadata parentheses", () => {
    assert.equal(getPhenotypeTermName("abnormal morphology (type II)"), "abnormal morphology (type II)");
    assert.equal(
        getPhenotypeTermName("abnormal morphology (type II) (Homo, Early)"),
        "abnormal morphology (type II)",
    );
    assert.equal(getPhenotypeTermName("abnormal morphology (Male)"), "abnormal morphology (Male)");
    assert.equal(
        getPhenotypeTermName("abnormal morphology (Homo, Early, Unknown)"),
        "abnormal morphology (Homo, Early, Unknown)",
    );
    assert.equal(getPhenotypeTermName("abnormal morphology"), "abnormal morphology");
});

test("getPhenotypeTermNames consolidates metadata variants", () => {
    const variants = [
        "abnormal glucose homeostasis (Hetero, Early, Male)",
        "abnormal glucose homeostasis (Homo, Early)",
        "abnormal glucose homeostasis (Homo, Early, Male)",
        "abnormal glucose homeostasis (Homo, Early, Female)",
    ];

    assert.deepEqual([...new Set(getPhenotypeTermNames(variants))], ["abnormal glucose homeostasis"]);
});

test("hasSelectedPhenotype matches every metadata variant of a selected term", () => {
    const selected = new Set(["abnormal glucose homeostasis"]);

    assert.equal(
        hasSelectedPhenotype(
            [
                "unrelated phenotype (Homo, Early)",
                "abnormal glucose homeostasis (Hetero, Early, Male)",
            ],
            selected,
        ),
        true,
    );
    assert.equal(hasSelectedPhenotype("abnormal glucose homeostasis (Homo, Early)", selected), true);
    assert.equal(hasSelectedPhenotype("unrelated phenotype (Homo, Early)", selected), false);
});

test("normalizePhenotypes handles arrays, scalar values, and missing values", () => {
    assert.deepEqual(normalizePhenotypes(["phenotype A", "", null, "phenotype B"]), [
        "phenotype A",
        "phenotype B",
    ]);
    assert.deepEqual(normalizePhenotypes("phenotype A"), ["phenotype A"]);
    assert.deepEqual(normalizePhenotypes(null), []);
});

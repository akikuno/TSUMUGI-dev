import { highlightDiseaseNodes } from "../js/highlighter.js";

// ========================================
// Helpers for restoring highlight states
// ========================================

function restoreHighlightStates(cy) {
    // Restore Human Disease highlighting if it was enabled
    const isDiseaseChecked = document.querySelector('#human-disease-filter-form input[type="checkbox"]:checked');
    if (isDiseaseChecked) {
        // Reapply highlighting by delegating to highlighter.js
        highlightDiseaseNodes(cy);
    }

    // Restore highlights from the gene search box
    const geneSearchInput = document.getElementById("gene-search");
    if (geneSearchInput && geneSearchInput.value.trim() !== "") {
        const searchTerm = geneSearchInput.value.trim().toLowerCase();
        const matchedNode = cy.nodes().filter((node) => node.data("label").toLowerCase() === searchTerm);

        if (matchedNode.length > 0) {
            matchedNode.addClass("gene-highlight");
        }
    }

    // Restore phenotype-based highlights
    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }

    // Refresh the phenotype list so it reflects the filtered genes
    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }
}

export function filterElementsByGenotypeAndSex(elements, cy, target_phenotype, filterElements) {
    const checkedSexs = Array.from(document.querySelectorAll('#sex-filter-form input[type="checkbox"]:checked')).map(
        (input) => input.value,
    );

    const checkedGenotypes = Array.from(
        document.querySelectorAll('#genotype-filter-form input[type="checkbox"]:checked'),
    ).map((input) => input.value);

    const checkedLifestages = Array.from(
        document.querySelectorAll('#lifestage-filter-form input[type="checkbox"]:checked'),
    ).map((input) => input.value);

    const allSexs = ["Female", "Male"];
    const allGenotypes = ["Homo", "Hetero", "Hemi"];
    const allLifestages = ["Embryo", "Early", "Interval", "Late"];

    let filteredElements = elements.map((item) => ({
        ...item,
        data: {
            ...item.data,
            _originalPhenotypes: item.data.phenotype || [], // Preserve the original phenotype list
            phenotype: item.data.phenotype || [],
        },
    }));

    // Apply sex filters
    if (checkedSexs.length !== allSexs.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedSexs.some((sex) => phenotype.includes(sex)),
                );
                return {
                    ...item,
                    data: { ...item.data, phenotype: filtered },
                };
            })
            .filter((item) => item.data.phenotype.length > 0);
    }

    // Apply genotype filters
    if (checkedGenotypes.length !== allGenotypes.length) {
        filteredElements = filteredElements
            .map((item) => {
                const original = item.data._originalPhenotypes;
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedGenotypes.some((gt) => phenotype.includes(gt)),
                );
                return {
                    ...item,
                    data: { ...item.data, phenotype: filtered },
                };
            })
            .filter((item) => item.data.phenotype.length > 0);
    }

    // Apply life-stage filters
    if (checkedLifestages.length !== allLifestages.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedLifestages.some((stage) => phenotype.includes(stage)),
                );
                return {
                    ...item,
                    data: { ...item.data, phenotype: filtered },
                };
            })
            .filter((item) => item.data.phenotype.length > 0);
    }

    // Keep only elements with at least two phenotypes
    filteredElements = filteredElements.filter((item) => item.data.phenotype && item.data.phenotype.length > 1);

    // Restore any phenotypes that match the target phenotype
    if (target_phenotype) {
        filteredElements = filteredElements.map((item) => {
            const original = item.data._originalPhenotypes;
            const restored = original.filter((phenotype) => phenotype.includes(target_phenotype));

            const merged = [...item.data.phenotype, ...restored];
            const unique = Array.from(new Set(merged));

            return {
                ...item,
                data: {
                    ...item.data,
                    phenotype: unique,
                },
            };
        });
    }

    // Remove elements that do not contain the target phenotype
    if (target_phenotype) {
        filteredElements = filteredElements.filter((item) =>
            item.data.phenotype.some((anno) => anno.includes(target_phenotype)),
        );
    }

    // Replace the Cytoscape elements and apply the filter-specific adjustments
    cy.elements().remove();
    cy.add(filteredElements);
    filterElements();

    restoreHighlightStates(cy);
}

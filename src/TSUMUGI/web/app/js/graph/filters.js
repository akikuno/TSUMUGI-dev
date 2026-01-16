import { highlightDiseaseNodes } from "./highlighter.js";

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

function getActiveFilterValues(formSelector, allValues) {
    const checkedInputs = Array.from(document.querySelectorAll(`${formSelector} input[type="checkbox"]:checked`));
    if (checkedInputs.length === 0) {
        return allValues;
    }

    const checkedValues = checkedInputs.map((input) => input.value);
    if (checkedValues.includes("All")) {
        return allValues;
    }

    return checkedValues;
}

/**
 * Apply genotype/sex/life-stage filters to phenotypes.
 */
export function filterElementsByGenotypeAndSex(elements, cy, targetPhenotype, filterElements) {
    const allSexes = ["Female", "Male"];
    const allGenotypes = ["Homo", "Hetero", "Hemi"];
    const allLifeStages = ["Embryo", "Early", "Interval", "Late"];

    const checkedSexes = getActiveFilterValues("#sex-filter-form", allSexes);
    const checkedGenotypes = getActiveFilterValues("#genotype-filter-form", allGenotypes);
    const checkedLifeStages = getActiveFilterValues("#lifestage-filter-form", allLifeStages);

    let filteredElements = elements.map((item) => {
        const basePhenotypes = Array.isArray(item.data.originalPhenotypes)
            ? item.data.originalPhenotypes
            : item.data.phenotype;
        const phenotypeList = Array.isArray(basePhenotypes)
            ? [...basePhenotypes]
            : basePhenotypes
                ? [basePhenotypes]
                : [];

        return {
            ...item,
            data: {
                ...item.data,
                originalPhenotypes: phenotypeList, // Preserve the original phenotype list
                phenotype: phenotypeList,
            },
        };
    });

    // Apply sex filters
    if (checkedSexes.length !== allSexes.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedSexes.some((sex) => phenotype.includes(sex)),
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
    if (checkedLifeStages.length !== allLifeStages.length) {
        filteredElements = filteredElements
            .map((item) => {
                const filtered = item.data.phenotype.filter((phenotype) =>
                    checkedLifeStages.some((stage) => phenotype.includes(stage)),
                );
                return {
                    ...item,
                    data: { ...item.data, phenotype: filtered },
                };
            })
            .filter((item) => item.data.phenotype.length > 0);
    }

    // Keep elements with at least one phenotype to avoid dropping valid single-annotation nodes
    filteredElements = filteredElements.filter((item) => item.data.phenotype && item.data.phenotype.length > 0);

    // Remove nodes that do not contain the target phenotype (edges are filtered later)
    if (targetPhenotype) {
        filteredElements = filteredElements.filter((item) => {
            if (item.data && item.data.source) {
                return true;
            }
            return item.data.phenotype.some((anno) => anno.includes(targetPhenotype));
        });
    }

    // Remove edges that are disconnected from the remaining nodes
    const nodeIds = new Set(
        filteredElements.filter((item) => item.data && item.data.id).map((item) => item.data.id),
    );
    filteredElements = filteredElements.filter((item) => {
        if (!item.data || !item.data.source) {
            return true;
        }
        return nodeIds.has(item.data.source) && nodeIds.has(item.data.target);
    });

    // Replace the Cytoscape elements and apply the filter-specific adjustments
    cy.elements().remove();
    cy.add(filteredElements);
    filterElements();

    restoreHighlightStates(cy);
}

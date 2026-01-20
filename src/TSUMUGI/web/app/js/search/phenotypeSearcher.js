// ############################################################
// Phenotype Search and Highlight Functions
// ############################################################

// Hold the available and selected phenotype lists
let allPhenotypes = [];
let selectedPhenotypes = new Set();
let cytoscapeInstance = null;

/**
 * Initialize the phenotype search feature.
 * @param {Object} params - Initialization parameters
 * @param {Object} params.cy - Cytoscape instance
 * @param {Array} params.elements - Network elements
 */
export function setupPhenotypeSearch({ cy, elements }) {
    cytoscapeInstance = cy;
    initializePhenotypeSearch(cy);
    setupPhenotypeSearchInput();

    // Expose helper for the inline onclick handlers
    window.removeSelectedPhenotype = removeSelectedPhenotype;

    // Make updatePhenotypeHighlight available to other modules
    window.updatePhenotypeHighlight = () => updatePhenotypeHighlight(cy);

    // Allow other modules to refresh the phenotype list after filtering
    window.refreshPhenotypeList = () => refreshPhenotypeList();
}

/**
 * Build the phenotype list from the currently visible genes.
 * @param {Object} cy - Cytoscape instance
 */
function initializePhenotypeSearch(cy) {
    const phenotypeSet = new Set();

    // Extract phenotypes only from visible nodes
    cy.nodes().forEach((node) => {
        // Skip nodes that are hidden
        if (node.style("display") !== "none" && !node.hidden()) {
            const nodeData = node.data();
            if (nodeData.phenotype) {
                const phenotypes = Array.isArray(nodeData.phenotype) ? nodeData.phenotype : [nodeData.phenotype];
                phenotypes.forEach((phenotype) => {
                    if (phenotype && phenotype.trim() !== "") {
                        phenotypeSet.add(phenotype.trim());
                    }
                });
            }
        }
    });

    allPhenotypes = Array.from(phenotypeSet).sort();
}

/**
 * Wire up event handlers for the phenotype search input.
 */
function setupPhenotypeSearchInput() {
    const searchInput = document.getElementById("phenotype-search");
    const suggestionsList = document.getElementById("phenotype-suggestions");

    if (!searchInput || !suggestionsList) {
        console.warn("Phenotype search elements not found in DOM");
        return;
    }

    searchInput.addEventListener("input", function () {
        const searchTerm = this.value.toLowerCase().trim();

        if (searchTerm.length === 0) {
            suggestionsList.hidden = true;
            return;
        }

        // Filter out phenotypes that are already selected
        const filteredPhenotypes = allPhenotypes.filter(
            (phenotype) => phenotype.toLowerCase().includes(searchTerm) && !selectedPhenotypes.has(phenotype),
        );

        displayPhenotypeSuggestions(filteredPhenotypes);
    });

    // Display suggestions when the field is clicked
    searchInput.addEventListener("click", function () {
        const searchTerm = this.value.toLowerCase().trim();

        if (searchTerm.length === 0) {
            // If empty, show all phenotypes except the selected ones
            const availablePhenotypes = allPhenotypes.filter((phenotype) => !selectedPhenotypes.has(phenotype));
            displayPhenotypeSuggestions(availablePhenotypes);
        } else {
            // Otherwise, show matching phenotypes
            const filteredPhenotypes = allPhenotypes.filter(
                (phenotype) => phenotype.toLowerCase().includes(searchTerm) && !selectedPhenotypes.has(phenotype),
            );
            displayPhenotypeSuggestions(filteredPhenotypes);
        }
    });

    // Also display suggestions when the field gains focus
    searchInput.addEventListener("focus", function () {
        const searchTerm = this.value.toLowerCase().trim();

        if (searchTerm.length === 0) {
            // If empty, show all phenotypes except the selected ones
            const availablePhenotypes = allPhenotypes.filter((phenotype) => !selectedPhenotypes.has(phenotype));
            displayPhenotypeSuggestions(availablePhenotypes);
        }
    });

    // Hide the suggestions when clicking outside the input
    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !suggestionsList.contains(event.target)) {
            suggestionsList.hidden = true;
        }
    });
}

/**
 * Render the phenotype suggestions list.
 * @param {Array} phenotypes - Phenotypes to display
 */
function displayPhenotypeSuggestions(phenotypes) {
    const suggestionsList = document.getElementById("phenotype-suggestions");
    suggestionsList.innerHTML = "";

    if (phenotypes.length === 0) {
        suggestionsList.hidden = true;
        return;
    }

    // Use the full list (scroll is possible in the UI)
    const displayPhenotypes = phenotypes;

    displayPhenotypes.forEach((phenotype) => {
        const li = document.createElement("li");
        li.textContent = phenotype;
        li.addEventListener("click", function () {
            addSelectedPhenotype(phenotype);
            document.getElementById("phenotype-search").value = "";
            suggestionsList.hidden = true;
        });
        suggestionsList.appendChild(li);
    });

    suggestionsList.hidden = false;
}

/**
 * Add a phenotype to the selection list.
 * @param {string} phenotype - Phenotype to add
 */
function addSelectedPhenotype(phenotype) {
    if (selectedPhenotypes.has(phenotype)) return;

    selectedPhenotypes.add(phenotype);
    displaySelectedPhenotypes();

    // Invoke the globally exposed updatePhenotypeHighlight helper
    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

/**
 * Remove a selected phenotype (called from inline handlers).
 * @param {string} phenotype - Phenotype to remove
 */
function removeSelectedPhenotype(phenotype) {
    selectedPhenotypes.delete(phenotype);
    displaySelectedPhenotypes();

    // Invoke the globally exposed updatePhenotypeHighlight helper
    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

/**
 * Render the currently selected phenotypes as tags.
 */
function displaySelectedPhenotypes() {
    const container = document.getElementById("selected-phenotypes");
    if (!container) return;

    container.innerHTML = "";

    selectedPhenotypes.forEach((phenotype) => {
        const tag = document.createElement("div");
        tag.className = "selected-phenotype-tag";
        tag.innerHTML = `
            <span class="phenotype-text">${phenotype}</span>
            <button class="remove-btn" onclick="removeSelectedPhenotype('${phenotype.replace(/'/g, "\\'")}')">&times;</button>
        `;
        container.appendChild(tag);
    });
}

/**
 * Highlight genes that match any of the selected phenotypes.
 * @param {Object} cy - Cytoscape instance
 */
function updatePhenotypeHighlight(cy) {
    // Reset existing highlights
    cy.nodes().removeClass("phenotype-highlight");

    if (selectedPhenotypes.size === 0) {
        return; // Nothing to highlight
    }

    // Highlight genes that match the selected phenotypes
    cy.nodes().forEach((node) => {
        const nodeData = node.data();

        if (nodeData.phenotype) {
            const nodePhenotypes = Array.isArray(nodeData.phenotype) ? nodeData.phenotype : [nodeData.phenotype];

            // Look for any overlap between the node's phenotypes and the selected ones
            const hasSelectedPhenotype = Array.from(selectedPhenotypes).some((selectedPhenotype) =>
                nodePhenotypes.some(
                    (nodePhenotype) => nodePhenotype && nodePhenotype.trim() === selectedPhenotype.trim(),
                ),
            );

            if (hasSelectedPhenotype) {
                node.addClass("phenotype-highlight");
            }
        }
    });
}

/**
 * Return the set of currently selected phenotypes.
 * @returns {Set} Selected phenotype set
 */
export function getSelectedPhenotypes() {
    return new Set(selectedPhenotypes);
}

/**
 * Clear all selected phenotypes.
 */
export function clearSelectedPhenotypes() {
    selectedPhenotypes.clear();
    displaySelectedPhenotypes();

    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

/**
 * Rebuild the phenotype list after filters change.
 */
function refreshPhenotypeList() {
    if (!cytoscapeInstance) return;

    // Preserve the current search term
    const searchInput = document.getElementById("phenotype-search");
    const currentSearchValue = searchInput ? searchInput.value : "";

    // Reinitialize the phenotype list
    initializePhenotypeSearch(cytoscapeInstance);

    // Drop selected phenotypes that no longer exist
    const updatedSelectedPhenotypes = new Set();
    selectedPhenotypes.forEach((phenotype) => {
        if (allPhenotypes.includes(phenotype)) {
            updatedSelectedPhenotypes.add(phenotype);
        }
    });
    selectedPhenotypes = updatedSelectedPhenotypes;

    // Refresh the UI
    displaySelectedPhenotypes();

    // Update suggestions if a search term was present
    if (searchInput && currentSearchValue.trim().length > 0) {
        const searchTerm = currentSearchValue.toLowerCase().trim();
        const filteredPhenotypes = allPhenotypes.filter(
            (phenotype) => phenotype.toLowerCase().includes(searchTerm) && !selectedPhenotypes.has(phenotype),
        );
        displayPhenotypeSuggestions(filteredPhenotypes);
    }

    // Refresh highlights
    if (window.updatePhenotypeHighlight) {
        window.updatePhenotypeHighlight();
    }
}

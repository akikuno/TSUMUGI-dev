function filterByNodeColorAndEdgeSize() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);

    let selectedMin = Math.min(...edgeSliderValues);
    let selectedMax = Math.max(...edgeSliderValues);

    if (edgeMin === edgeMax) {
        selectedMin = edgeMin;
        selectedMax = edgeMax;
    }

    const edgeMinValue = Math.max(edgeMin, selectedMin);
    const edgeMaxValue = Math.min(edgeMax, selectedMax);

    // 1. Hide everything for a clean slate
    cy.elements().forEach((ele) => ele.style("display", "none"));

    // 2. Show edges that meet the edge_size condition
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const isVisible = edgeSize >= Math.min(edgeMinValue, edgeMaxValue) && edgeSize <= Math.max(edgeMinValue, edgeMaxValue);
        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. Compute components from the currently visible edges and nodes
    const visibleEdges = cy.edges().filter(edge => edge.style("display") === "element");
    const candidateElements = visibleEdges.union(visibleEdges.connectedNodes());
    const components = candidateElements.components();

    // 4. Identify only the nodes directly connected to the target gene
    const targetGene = "XXX_NAME";
    const targetNode = cy.getElementById(targetGene);

    if (targetNode.length === 0) {
        return;
    }

    // 5. Ensure the target gene is visible
    targetNode.style("display", "element");

    // 6. Collect nodes directly connected to the target gene
    const directlyConnectedNodes = new Set([targetGene]);

    // First gather nodes connected to the target gene
    cy.edges().forEach((edge) => {
        if (edge.style("display") === "element") {
            const source = edge.data("source");
            const target = edge.data("target");

            // Track nodes joined by edges that involve the target gene
            if (source === targetGene) {
                directlyConnectedNodes.add(target);
            } else if (target === targetGene) {
                directlyConnectedNodes.add(source);
            }
        }
    });

    // 7. Keep only edges whose endpoints are directly connected nodes
    cy.edges().forEach((edge) => {
        if (edge.style("display") === "element") {
            const source = edge.data("source");
            const target = edge.data("target");

            // Show edges only when both ends belong to the retained set
            if (directlyConnectedNodes.has(source) && directlyConnectedNodes.has(target)) {
                edge.style("display", "element");
            } else {
                edge.style("display", "none");
            }
        }
    });

    // 8. Hide nodes that are not in the directly connected set
    cy.nodes().forEach((node) => {
        const nodeId = node.data("id");
        if (directlyConnectedNodes.has(nodeId)) {
            node.style("display", "element");
        } else {
            node.style("display", "none");
        }
    });

    // 9. Re-run the layout
    cy.layout(getLayoutOptions()).run();


    // 10. Refresh the phenotype list so it reflects current visibility
    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }
    
    // 11. Recalculate centrality for the filtered network
    if (typeof window.recalculateCentrality === 'function') {
        window.recalculateCentrality();
    }
}

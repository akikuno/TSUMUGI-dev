function filterByNodeColorAndEdgeSize() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax, 1, 100);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax, 1, 100);

    // 1. Start by showing all nodes
    cy.nodes().forEach((node) => node.style("display", "element"));

    // 2. Show or hide edges based on the edge_size threshold
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
        const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";
        const isVisible = sourceVisible && targetVisible && edgeSize >= Math.min(edgeMinValue, edgeMaxValue) && edgeSize <= Math.max(edgeMinValue, edgeMaxValue);
        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. Keep only the connected components that include a node with node_color === 1
    const components = calculateConnectedComponents(cy);
    const validComponents = components.filter((comp) =>
        Object.keys(comp).some((label) => {
            const node = cy.$(`node[label="${label}"]`);
            return node.data("node_color") === 1;
        })
    );

    // 4. Re-display nodes and edges for the retained components
    validComponents.forEach((comp) => {
        Object.keys(comp).forEach((label) => {
            const node = cy.$(`node[label="${label}"]`);
            node.style("display", "element");
            node.connectedEdges().forEach((edge) => {
                const edgeSize = edge.data("edge_size");
                if (edgeSize >= Math.min(edgeMinValue, edgeMaxValue) && edgeSize <= Math.max(edgeMinValue, edgeMaxValue)) {
                    edge.style("display", "element");
                }
            });
        });
    });

    // 5. Hide isolated nodes
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // 6. Re-run the layout
    cy.layout(getLayoutOptions()).run();


    // 7. Refresh the phenotype list so only visible genes remain
    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }
    
    // 8. Recalculate centrality for the filtered network
    if (typeof window.recalculateCentrality === 'function') {
        window.recalculateCentrality();
    }
}

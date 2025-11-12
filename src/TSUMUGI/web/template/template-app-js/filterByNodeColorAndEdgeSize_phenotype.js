function filterByNodeColorAndEdgeSize() {
    const hasNodeSlider = nodeSlider && nodeSlider.noUiSlider;
    const nodeSliderValues = hasNodeSlider
        ? nodeSlider.noUiSlider.get().map(Number)
        : [NODE_SLIDER_MIN, NODE_SLIDER_MAX];
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);

    const nodeLowerBound = Math.min(nodeMin, nodeMax);
    const nodeUpperBound = Math.max(nodeMin, nodeMax);
    const rawNodeMin = Math.min(...nodeSliderValues);
    const rawNodeMax = Math.max(...nodeSliderValues);
    let nodeMinValue = scaleToOriginalRange(rawNodeMin, nodeLowerBound, nodeUpperBound, NODE_SLIDER_MIN, NODE_SLIDER_MAX);
    let nodeMaxValue = scaleToOriginalRange(rawNodeMax, nodeLowerBound, nodeUpperBound, NODE_SLIDER_MIN, NODE_SLIDER_MAX);
    if (nodeLowerBound === nodeUpperBound) {
        nodeMinValue = nodeLowerBound;
        nodeMaxValue = nodeUpperBound;
    }

    const rawEdgeMin = Math.min(...edgeSliderValues);
    const rawEdgeMax = Math.max(...edgeSliderValues);
    let edgeMinValue = scaleToOriginalRange(rawEdgeMin, edgeMin, edgeMax, EDGE_SLIDER_MIN, EDGE_SLIDER_MAX);
    let edgeMaxValue = scaleToOriginalRange(rawEdgeMax, edgeMin, edgeMax, EDGE_SLIDER_MIN, EDGE_SLIDER_MAX);
    if (edgeMin === edgeMax) {
        edgeMinValue = edgeMin;
        edgeMaxValue = edgeMax;
    }

    // 1. Toggle node visibility based on the node_color range
    cy.nodes().forEach((node) => {
        const nodeColorForFilter = node.data("node_color_for_filter") || node.data("node_color");
        const isVisible = nodeColorForFilter >= Math.min(nodeMinValue, nodeMaxValue) && nodeColorForFilter <= Math.max(nodeMinValue, nodeMaxValue);
        node.style("display", isVisible ? "element" : "none");
    });

    // 2. Toggle edges using edge_size and shared-phenotype thresholds
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const sharedPhenotypes = edge.data("phenotype") || [];
        const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
        const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";

        const isVisible =
            sourceVisible &&
            targetVisible &&
            edgeSize >= Math.min(edgeMinValue, edgeMaxValue) &&
            edgeSize <= Math.max(edgeMinValue, edgeMaxValue) &&
            sharedPhenotypes.length >= 2; // Keep edges that share at least two phenotypes

        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. Hide isolated nodes
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // 4. Re-run the layout
    cy.layout(getLayoutOptions()).run();

    // 5. Refresh the phenotype list so only visible genes remain
    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }
    
    // 6. Recalculate centrality for the filtered network
    if (typeof window.recalculateCentrality === 'function') {
        window.recalculateCentrality();
    }
}

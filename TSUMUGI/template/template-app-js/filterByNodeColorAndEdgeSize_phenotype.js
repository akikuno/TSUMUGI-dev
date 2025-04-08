function filterByNodeColorAndEdgeSize() {
    let nodeSliderValues = [1, 10];

    nodeSliderValues = nodeSlider.noUiSlider.get().map(parseFloat); // REMOVE_THIS_LINE_IF_BINARY_PHENOTYPE

    const edgeSliderValues = edgeSlider.noUiSlider.get().map(parseFloat);

    const nodeMinValue = scaleToOriginalRange(nodeSliderValues[0], nodeMin, nodeMax);
    const nodeMaxValue = scaleToOriginalRange(nodeSliderValues[1], nodeMin, nodeMax);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // Filter nodes based on color
    cy.nodes().forEach(function (node) {
        const nodeColor = node.data("node_color");
        node.style("display", nodeColor >= nodeMinValue && nodeColor <= nodeMaxValue ? "element" : "none");
    });

    // Filter edges based on size
    cy.edges().forEach(function (edge) {
        const edgeSize = edge.data("edge_size");
        const sourceNode = cy.getElementById(edge.data("source"));
        const targetNode = cy.getElementById(edge.data("target"));

        if (
            sourceNode.style("display") === "element" &&
            targetNode.style("display") === "element" &&
            edgeSize >= edgeMinValue &&
            edgeSize <= edgeMaxValue
        ) {
            edge.style("display", "element");
        } else {
            edge.style("display", "none");
        }
    });

    // After filtering, remove nodes with no connected visible edges
    cy.nodes().forEach(function (node) {
        const connectedEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (connectedEdges.length === 0) {
            node.style("display", "none"); // Hide node if no connected edges
        }
    });

    // Reapply layout after filtering
    cy.layout(getLayoutOptions()).run();
}


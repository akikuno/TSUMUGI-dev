function filterByNodeColorAndEdgeSize() {

    let nodeSliderValues = [1, 10];
    nodeSliderValues = nodeSlider.noUiSlider.get().map(parseFloat); // REMOVE_THIS_LINE_IF_BINARY_PHENOTYPE

    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);

    const nodeMinValue = scaleToOriginalRange(nodeSliderValues[0], nodeMin, nodeMax);
    const nodeMaxValue = scaleToOriginalRange(nodeSliderValues[1], nodeMin, nodeMax);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // 1. node_color 範囲に基づきノードを表示/非表示
    cy.nodes().forEach((node) => {
        const nodeColorForFilter = node.data("node_color_for_filter") || node.data("node_color");
        const isVisible = nodeColorForFilter >= Math.min(nodeMinValue, nodeMaxValue) && nodeColorForFilter <= Math.max(nodeMinValue, nodeMaxValue);
        node.style("display", isVisible ? "element" : "none");
    });

    // 2. edge_size + 表現型数の条件でエッジを表示/非表示
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
            sharedPhenotypes.length >= 2; // 2つ以上の表現型を持つエッジのみ表示

        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. 孤立ノードを非表示
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // 4. レイアウト再適用
    cy.layout(getLayoutOptions()).run();

    // 5. 表現型リストを更新（フィルター変更後に現在表示されている遺伝子の表現型のみを表示）
    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }
}

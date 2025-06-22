function filterByNodeColorAndEdgeSize() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // 1. 一旦すべて非表示
    cy.elements().forEach((ele) => ele.style("display", "none"));

    // 2. edge_size 条件に一致するエッジのみ表示
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const isVisible = edgeSize >= Math.min(edgeMinValue, edgeMaxValue) && edgeSize <= Math.max(edgeMinValue, edgeMaxValue);
        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. 表示されているエッジとその接続ノードから連結成分を計算
    const visibleEdges = cy.edges().filter(edge => edge.style("display") === "element");
    const candidateElements = visibleEdges.union(visibleEdges.connectedNodes());
    const components = candidateElements.components();

    // 4. 標的遺伝子と直接接続されているノードのみを特定
    const targetGene = "XXX_NAME";
    const targetNode = cy.getElementById(targetGene);
    
    if (targetNode.length === 0) {
        return;
    }

    // 5. 標的遺伝子を表示
    targetNode.style("display", "element");

    // 6. 標的遺伝子と直接接続されているノードを特定
    const directlyConnectedNodes = new Set([targetGene]);
    
    // まず標的遺伝子と直接接続されているノードを特定
    cy.edges().forEach((edge) => {
        if (edge.style("display") === "element") {
            const source = edge.data("source");
            const target = edge.data("target");
            
            // 標的遺伝子が関与するエッジから接続ノードを特定
            if (source === targetGene) {
                directlyConnectedNodes.add(target);
            } else if (target === targetGene) {
                directlyConnectedNodes.add(source);
            }
        }
    });

    // 7. 直接接続されたノード間のすべてのエッジとノードを表示
    cy.edges().forEach((edge) => {
        if (edge.style("display") === "element") {
            const source = edge.data("source");
            const target = edge.data("target");
            
            // 両端のノードが直接接続されたノードセットに含まれている場合は表示
            if (directlyConnectedNodes.has(source) && directlyConnectedNodes.has(target)) {
                edge.style("display", "element");
            } else {
                edge.style("display", "none");
            }
        }
    });

    // 8. 直接接続されたノードのみ表示
    cy.nodes().forEach((node) => {
        const nodeId = node.data("id");
        if (directlyConnectedNodes.has(nodeId)) {
            node.style("display", "element");
        } else {
            node.style("display", "none");
        }
    });

    // 6. レイアウト再適用
    cy.layout(getLayoutOptions()).run();
}

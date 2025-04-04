function filterByNodeColorAndEdgeSize() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // 1. edge_size条件を満たすエッジを取得
    const visibleEdges = cy.edges().filter((edge) => {
        const edgeSize = edge.data("edge_size");
        return edgeSize >= edgeMinValue && edgeSize <= edgeMaxValue;
    });

    // 2. 条件を満たしたエッジ＋そのエッジに接続しているノードたちを取得
    const candidateElements = visibleEdges.union(visibleEdges.connectedNodes());

    // 3. 連結成分を取得
    const components = candidateElements.components();

    // 4. 一旦すべて非表示にしてから…
    cy.elements().forEach((ele) => ele.style("display", "none"));

    // 5. node_color === 1 を含むクラスタだけ表示
    components.forEach((comp) => {
        const hasColor1 = comp.nodes().some((node) => node.data("node_color") === 1);
        if (hasColor1) {
            comp.nodes().forEach((node) => node.style("display", "element"));
            comp.edges().forEach((edge) => edge.style("display", "element"));
        }
    });

    // 6. レイアウト再適用
    cy.layout(getLayoutOptions()).run();
}


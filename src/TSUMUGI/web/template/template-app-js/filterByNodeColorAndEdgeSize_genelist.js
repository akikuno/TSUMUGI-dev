function filterByNodeColorAndEdgeSize() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax, 1, 100);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax, 1, 100);

    // 1. 一旦すべてのノードを表示
    cy.nodes().forEach((node) => node.style("display", "element"));

    // 2. edge_size 条件に基づきエッジの表示/非表示を設定
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
        const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";
        const isVisible = sourceVisible && targetVisible && edgeSize >= Math.min(edgeMinValue, edgeMaxValue) && edgeSize <= Math.max(edgeMinValue, edgeMaxValue);
        edge.style("display", isVisible ? "element" : "none");
    });

    // 3. node_color === 1 を含むクラスタだけ残す
    const components = calculateConnectedComponents(cy);
    const validComponents = components.filter((comp) =>
        Object.keys(comp).some((label) => {
            const node = cy.$(`node[label="${label}"]`);
            return node.data("node_color") === 1;
        })
    );

    // 4. 対象クラスタのノードとエッジを再表示
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

    // 5. 孤立ノードを非表示にする
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // 6. レイアウト再適用
    cy.layout(getLayoutOptions()).run();


    // 7. 表現型リストを更新（フィルター変更後に現在表示されている遺伝子の表現型のみを表示）
    if (window.refreshPhenotypeList) {
        window.refreshPhenotypeList();
    }
    
    // 8. Recalculate centrality for the filtered network
    if (typeof window.recalculateCentrality === 'function') {
        window.recalculateCentrality();
    }
}

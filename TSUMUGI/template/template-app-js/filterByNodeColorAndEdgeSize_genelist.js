function filterByNodeColorAndEdgeSize() {
    const edgeSliderValues = edgeSlider.noUiSlider.get().map(Number);
    const edgeMinValue = scaleToOriginalRange(edgeSliderValues[0], edgeMin, edgeMax);
    const edgeMaxValue = scaleToOriginalRange(edgeSliderValues[1], edgeMin, edgeMax);

    // すべてのノードを一旦表示状態にする
    cy.nodes().forEach((node) => node.style("display", "element"));

    // edge_sizeの範囲でエッジをフィルターし、表示/非表示を設定
    cy.edges().forEach((edge) => {
        const edgeSize = edge.data("edge_size");
        const sourceVisible = cy.getElementById(edge.data("source")).style("display") === "element";
        const targetVisible = cy.getElementById(edge.data("target")).style("display") === "element";

        const isEdgeVisible = sourceVisible && targetVisible && edgeSize >= edgeMinValue && edgeSize <= edgeMaxValue;

        edge.style("display", isEdgeVisible ? "element" : "none");
    });

    // 連結成分を取得し、node_color === 1 を含むものだけ残す
    const connectedComponents = calculateConnectedComponents(cy);
    const componentsWithColor1 = connectedComponents.filter((component) =>
        Object.keys(component).some((label) => {
            const node = cy.$(`node[label="${label}"]`);
            return node.data("node_color") === 1;
        }),
    );

    // node_color === 1を含むノードのなかから、edge_size条件を満たすエッジを再表示
    componentsWithColor1.forEach((component) => {
        Object.keys(component).forEach((label) => {
            const node = cy.$(`node[label="${label}"]`);
            node.style("display", "element");

            node.connectedEdges().forEach((edge) => {
                const edgeSize = edge.data("edge_size");
                if (edgeSize >= edgeMinValue && edgeSize <= edgeMaxValue) {
                    edge.style("display", "element");
                }
            });
        });
    });

    // 接続エッジがすべて非表示のノードは非表示にする（孤立ノードの除去）
    cy.nodes().forEach((node) => {
        const visibleEdges = node.connectedEdges().filter((edge) => edge.style("display") === "element");
        if (visibleEdges.length === 0) {
            node.style("display", "none");
        }
    });

    // フィルタ後のレイアウトを再適用
    cy.layout(getLayoutOptions()).run();
}

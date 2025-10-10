// ============================================================================
// edgeMin/edgeMaxの計算：
// 1. node_color === 1 のノードに接続されたエッジの中で最小/最大のedge_sizeを取得
// 2. その値をedgeMin/edgeMaxとする
// 3. その後、elementsのedge_sizeをedgeMin/edgeMaxを上限として調整
// ============================================================================

function adjustConnectedEdgeSize(elements, mode = "max") {
    if (!["max", "min"].includes(mode)) {
        throw new Error("mode must be 'max' or 'min'");
    }

    // node_color === 1 のノードを1つ取得
    const targetNode = elements.find(ele => ele.data.node_color === 1);
    if (!targetNode) return undefined;

    const targetId = targetNode.data.id;

    // 対象ノードに接続されたエッジを取得
    const connectedEdges = elements.filter(
        ele => ele.data.source === targetId || ele.data.target === targetId
    );

    // 有効な edge_size を収集
    const edgeSizes = connectedEdges
        .filter(edge => edge.data.edge_size !== undefined)
        .map(edge => edge.data.edge_size);

    if (edgeSizes.length === 0) return undefined;

    // 最小または最大を取得
    const limit = mode === "max" ? Math.max(...edgeSizes) : Math.min(...edgeSizes);

    // 上限または下限でedge_sizeを調整
    connectedEdges.forEach(edge => {
        if (mode === "max" && edge.data.edge_size > limit) {
            edge.data.edge_size = limit;
        } else if (mode === "min" && edge.data.edge_size < limit) {
            edge.data.edge_size = limit;
        }
    });

    return limit;
}

const edgeMax = adjustConnectedEdgeSize(elements, "max");
const edgeMin = adjustConnectedEdgeSize(elements, "min");

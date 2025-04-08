// ============================================================================
// edgeMaxの計算：
// 1. node_color === 1 のノードに接続されたエッジの中で最大のedge_sizeを取得
// 2. その値をedgeMaxとする
// 3. その後、elementsのedge_sizeをedgeMaxを上限として調整
// ============================================================================

// node_color === 1 のノード(targetGene)を1つだけ取得
const targetGene = elements.find((ele) => ele.data.node_color === 1);

// targetGeneの ID (遺伝子シンボル)を取得
const targetGeneId = targetGene?.data?.id;

// targetGeneに接続されているエッジだけ抽出
const connectedEdges = elements.filter((ele) => ele.data.source === targetGeneId || ele.data.target === targetGeneId);

// そのエッジたちの edge_size を集めて最大値を取得
const edgeSizesTargetGene = connectedEdges
    .filter((edge) => edge.data.edge_size !== undefined)
    .map((edge) => edge.data.edge_size);

const edgeMax = Math.max(...edgeSizesTargetGene);

// elementsに含まれる全edge_sizeの最大値を、edgeMaxを上限とする
connectedEdges.forEach((edge) => {
    if (edge.data.edge_size > edgeMax) {
        edge.data.edge_size = edgeMax;
    }
});

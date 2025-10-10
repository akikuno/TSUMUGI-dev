// ==========================================================
// スライダーを上限値・下限値に合わせても、最低１つの遺伝子ペアが可視化できるようにする. Issue #72
// ==========================================================

// Step 1: node_color を ID にマップし、ランクをつける
const nodeColorMap = new Map();
elements.forEach(ele => {
    if (ele.data.node_color !== undefined && ele.data.id !== undefined) {
        nodeColorMap.set(ele.data.id, ele.data.node_color);
    }
});

// ランク付け
const sortedNodeColors = [...new Set([...nodeColorMap.values()])].sort((a, b) => a - b);
const nodeColorToRank = new Map();
sortedNodeColors.forEach((val, idx) => {
    nodeColorToRank.set(val, idx + 1);  // ランクは1スタート
});

// Step 2: エッジごとに source/target のランク合計と、元の値を保存
const edgeRankPairs = [];

elements.forEach(ele => {
    if (ele.data.source && ele.data.target) {
        const sourceVal = nodeColorMap.get(ele.data.source);
        const targetVal = nodeColorMap.get(ele.data.target);

        if (sourceVal !== undefined && targetVal !== undefined) {
            const sourceRank = nodeColorToRank.get(sourceVal);
            const targetRank = nodeColorToRank.get(targetVal);
            const rankSum = sourceRank + targetRank;

            edgeRankPairs.push({
                rankSum: rankSum,
                minVal: Math.min(sourceVal, targetVal),
                maxVal: Math.max(sourceVal, targetVal),
            });
        }
    }
});

// Step 3: 最小スコアのペアの max → nodeMin、最大スコアのペアの min → nodeMax
const minRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum < b.rankSum ? a : b));
const maxRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum > b.rankSum ? a : b));

// フィルタリング用の範囲のみ更新（色表示用は元の値を保持）
nodeMin = minRankEdge.maxVal;
nodeMax = maxRankEdge.minVal;

// 色表示用の元の値は保持し、フィルタリング用の値を新しく追加
elements.forEach(ele => {
    if (ele.data.node_color !== undefined) {
        // 色表示用の元の値を保存
        ele.data.original_node_color = ele.data.node_color;
        
        // フィルタリング用の値をクリップ
        if (ele.data.node_color <= nodeMin) {
            ele.data.node_color_for_filter = nodeMin;
        } else if (ele.data.node_color >= nodeMax) {
            ele.data.node_color_for_filter = nodeMax;
        } else {
            ele.data.node_color_for_filter = ele.data.node_color;
        }
    }
});

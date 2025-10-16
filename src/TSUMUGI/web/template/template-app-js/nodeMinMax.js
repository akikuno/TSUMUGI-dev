// ==========================================================
// Ensure at least one gene pair remains visible even at slider extremes. Issue #72
// ==========================================================

// Step 1: Map node_color to ID and assign ranking
const nodeColorMap = new Map();
elements.forEach(ele => {
    if (ele.data.node_color !== undefined && ele.data.id !== undefined) {
        nodeColorMap.set(ele.data.id, ele.data.node_color);
    }
});

// Assign ranks
const sortedNodeColors = [...new Set([...nodeColorMap.values()])].sort((a, b) => a - b);
const nodeColorToRank = new Map();
sortedNodeColors.forEach((val, idx) => {
    nodeColorToRank.set(val, idx + 1);  // Ranks start from 1
});

// Step 2: Record source/target rank sums and original values per edge
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

// Step 3: Use the max of the lowest-ranked pair for nodeMin and the min of the highest-ranked pair for nodeMax
const minRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum < b.rankSum ? a : b));
const maxRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum > b.rankSum ? a : b));

// Update only the filtering range (preserve original values for coloring)
nodeMin = minRankEdge.maxVal;
nodeMax = maxRankEdge.minVal;

// Preserve original values for coloring and add clipped values for filtering
elements.forEach(ele => {
    if (ele.data.node_color !== undefined) {
        // Store the original value for coloring
        ele.data.original_node_color = ele.data.node_color;
        
        // Clip the value used for filtering
        if (ele.data.node_color <= nodeMin) {
            ele.data.node_color_for_filter = nodeMin;
        } else if (ele.data.node_color >= nodeMax) {
            ele.data.node_color_for_filter = nodeMax;
        } else {
            ele.data.node_color_for_filter = ele.data.node_color;
        }
    }
});

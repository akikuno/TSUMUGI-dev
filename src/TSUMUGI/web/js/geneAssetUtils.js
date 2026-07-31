export const GENE_DISPLAY_MAX_NODES = 150;
export const GENE_LIST_MAX_NODES = 200;
export const GENE_PAGE_MIN_SHARED_CONTEXTS = 3;
export const GENE_LIST_MIN_SHARED_CONTEXTS = 1;
export const MIN_PHENOTYPE_SIMILARITY_SCORE = 1;

export function normalizeGeneInput(rawInput) {
    const seen = new Set();
    const normalized = [];
    String(rawInput || "")
        .split(/\r?\n/)
        .map((gene) => gene.trim())
        .filter(Boolean)
        .forEach((gene) => {
            if (seen.has(gene)) return;
            seen.add(gene);
            normalized.push(gene);
        });
    return normalized;
}

export function validateGeneListRequestGenes(genes) {
    if (!Array.isArray(genes)) {
        throw new Error("Gene List request is invalid. Please submit the list again.");
    }
    const normalized = normalizeGeneInput(genes.map((gene) => String(gene)).join("\n"));
    if (normalized.length < 2) {
        throw new Error("Gene List request is invalid. Please submit the list again.");
    }
    if (normalized.length > GENE_LIST_MAX_NODES) {
        throw new Error(`Gene List requests are limited to ${GENE_LIST_MAX_NODES} genes.`);
    }
    return normalized;
}

function cloneJson(value) {
    return JSON.parse(JSON.stringify(value));
}

function getOtherGene(edgeData, targetGene) {
    if (edgeData.source === targetGene) return edgeData.target;
    if (edgeData.target === targetGene) return edgeData.source;
    return null;
}

function pairKey(source, target) {
    return [source, target].sort().join("||");
}

function compareGeneSymbols(left, right) {
    if (left === right) return 0;
    return left < right ? -1 : 1;
}

function comparableEdgeData(data) {
    const [source, target] = [String(data.source), String(data.target)].sort();
    return {
        source,
        target,
        phenotype: [...(data.phenotype || [])].sort(),
        phenotype_similarity_score: Number(data.phenotype_similarity_score),
        shared_context_count: Number(data.shared_context_count),
    };
}

function scaleScores(scores) {
    if (!scores.length) return new Map();
    const minimum = Math.min(...scores);
    const maximum = Math.max(...scores);
    const scaled = new Map();
    [...new Set(scores)].forEach((score) => {
        const value = minimum === maximum ? 100 : Math.floor(1 + ((score - minimum) * 99) / (maximum - minimum));
        scaled.set(score, value);
    });
    return scaled;
}

export function validateGeneAsset(asset, expectedGene = null) {
    if (!asset || asset.schema_version !== 2 || !asset.node || !Array.isArray(asset.direct_edges)) {
        throw new Error("Unsupported or invalid gene asset.");
    }
    const gene = asset.node.data && asset.node.data.id;
    if (!gene || gene !== asset.gene) {
        throw new Error("Gene asset node does not match its gene identifier.");
    }
    if (expectedGene && gene !== expectedGene) {
        throw new Error(`Expected gene asset ${expectedGene}, received ${gene}.`);
    }
    return asset;
}

export function selectGeneDisplayIds(
    asset,
    {
        maxNodes = GENE_DISPLAY_MAX_NODES,
        minSharedContexts = GENE_PAGE_MIN_SHARED_CONTEXTS,
        minScore = MIN_PHENOTYPE_SIMILARITY_SCORE,
    } = {},
) {
    validateGeneAsset(asset);
    const targetGene = asset.gene;
    const candidates = asset.direct_edges
        .map((edge) => {
            const data = edge.data || {};
            return {
                gene: getOtherGene(data, targetGene),
                score: Number(data.phenotype_similarity_score),
                sharedContexts: Number(data.shared_context_count),
            };
        })
        .filter(
            (candidate) =>
                candidate.gene &&
                candidate.score >= minScore &&
                candidate.sharedContexts >= minSharedContexts,
        )
        .sort((left, right) => {
            if (right.score !== left.score) return right.score - left.score;
            if (right.sharedContexts !== left.sharedContexts) {
                return right.sharedContexts - left.sharedContexts;
            }
            return compareGeneSymbols(left.gene, right.gene);
        });

    return [targetGene, ...candidates.slice(0, Math.max(0, maxNodes - 1)).map((candidate) => candidate.gene)];
}

export function buildInducedGeneElements(
    assets,
    allowedGenes,
    {
        minSharedContexts = GENE_LIST_MIN_SHARED_CONTEXTS,
        minScore = MIN_PHENOTYPE_SIMILARITY_SCORE,
        targetGene = null,
    } = {},
) {
    const allowedGeneSet = new Set(allowedGenes);
    const assetsByGene = new Map();
    assets.forEach((asset) => {
        validateGeneAsset(asset);
        assetsByGene.set(asset.gene, asset);
    });

    const missingGenes = [...allowedGeneSet].filter((gene) => !assetsByGene.has(gene));
    if (missingGenes.length) {
        throw new Error(`Missing gene assets: ${missingGenes.join(", ")}`);
    }

    const nodes = [...allowedGeneSet]
        .sort()
        .map((gene) => {
            const node = cloneJson(assetsByGene.get(gene).node);
            node.data.node_color = targetGene === gene ? 100 : 1;
            node.data.hide_effect_size = true;
            return node;
        });

    const edgesByPair = new Map();
    assetsByGene.forEach((asset) => {
        asset.direct_edges.forEach((edge) => {
            const data = edge.data || {};
            if (!allowedGeneSet.has(data.source) || !allowedGeneSet.has(data.target)) return;
            if (Number(data.shared_context_count) < minSharedContexts) return;
            if (Number(data.phenotype_similarity_score) < minScore) return;

            const key = pairKey(data.source, data.target);
            const normalized = comparableEdgeData(data);
            const existing = edgesByPair.get(key);
            if (existing && JSON.stringify(existing) !== JSON.stringify(normalized)) {
                throw new Error(`Conflicting direct edge payload for ${key}.`);
            }
            edgesByPair.set(key, normalized);
        });
    });

    const edgeRecords = [...edgesByPair.values()].sort((left, right) => {
        const sourceOrder = compareGeneSymbols(left.source, right.source);
        return sourceOrder || compareGeneSymbols(left.target, right.target);
    });
    const scaledScores = scaleScores(edgeRecords.map((edge) => edge.phenotype_similarity_score));
    const edges = edgeRecords.map((data) => ({
        data: {
            ...data,
            edge_size: scaledScores.get(data.phenotype_similarity_score),
        },
    }));

    return [...nodes, ...edges];
}

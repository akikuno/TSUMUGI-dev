function compareIds(left, right) {
    if (left < right) return -1;
    if (left > right) return 1;
    return 0;
}

function normalizeIds(values) {
    if (!Array.isArray(values)) return [];
    return [...new Set(values.filter((value) => value !== null && value !== undefined).map(String))].sort(compareIds);
}

export function createModuleDescriptor({ id, label, nodeIds = [], edgeIds = [] }) {
    if (!id || !label) {
        throw new Error("Module descriptors require both id and label.");
    }

    return {
        id: String(id),
        label: String(label),
        nodeIds: normalizeIds(nodeIds),
        edgeIds: normalizeIds(edgeIds),
    };
}

export function createStableSimilarityModuleId(nodeIds) {
    const normalizedNodeIds = normalizeIds(nodeIds);
    return `similarity:${normalizedNodeIds.map((nodeId) => encodeURIComponent(nodeId)).join("|")}`;
}

export function getModuleNodeCount(module) {
    return normalizeIds(module?.nodeIds).length;
}

export function isModuleWithinNodeCountRange(module, minimum, maximum) {
    const minValue = Number(minimum);
    const maxValue = Number(maximum);
    if (!Number.isFinite(minValue) || !Number.isFinite(maxValue)) return false;

    const lowerBound = Math.min(minValue, maxValue);
    const upperBound = Math.max(minValue, maxValue);
    const nodeCount = getModuleNodeCount(module);
    return nodeCount >= lowerBound && nodeCount <= upperBound;
}

export function filterModulesByNodeCount(modules, minimum, maximum) {
    if (!Array.isArray(modules)) return [];
    return modules.filter((module) => isModuleWithinNodeCountRange(module, minimum, maximum));
}

export function collectModuleElementIds(modules) {
    const nodeIds = new Set();
    const edgeIds = new Set();

    (Array.isArray(modules) ? modules : []).forEach((module) => {
        normalizeIds(module?.nodeIds).forEach((nodeId) => nodeIds.add(nodeId));
        normalizeIds(module?.edgeIds).forEach((edgeId) => edgeIds.add(edgeId));
    });

    return { nodeIds, edgeIds };
}

export function isFullNodeCountRange(values, rangeMinimum, rangeMaximum) {
    if (!Array.isArray(values) || values.length < 2) return true;

    const selectedMinimum = Math.min(Number(values[0]), Number(values[1]));
    const selectedMaximum = Math.max(Number(values[0]), Number(values[1]));
    return selectedMinimum <= rangeMinimum && selectedMaximum >= rangeMaximum;
}

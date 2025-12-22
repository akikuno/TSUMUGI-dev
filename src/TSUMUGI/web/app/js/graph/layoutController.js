import { scaleToOriginalRange } from "./valueScaler.js";

const NODE_REPULSION_MIN = 1;
const NODE_REPULSION_MAX = 10000;
const COMPONENT_SPACING_MIN = 1;
const COMPONENT_SPACING_MAX = 200;

const REPULSION_SPACING_MIN = 20;
const REPULSION_SPACING_FACTOR_MIN = 0.75;
const REPULSION_SPACING_FACTOR_MAX = 2.6;
const REPULSION_STRENGTH_MIN = 0.25;
const REPULSION_STRENGTH_MAX = 1.1;
const REPULSION_RADIAL_MIN = 0.02;
const REPULSION_RADIAL_MAX = 0.12;

export function createLayoutController({ isGeneSymbolPage, defaultNodeRepulsion }) {
    let cy = null;
    let currentLayout = "cose";
    let nodeRepulsionScale = defaultNodeRepulsion;
    let nodeRepulsionValue = scaleToOriginalRange(defaultNodeRepulsion, NODE_REPULSION_MIN, NODE_REPULSION_MAX);
    let componentSpacingValue = scaleToOriginalRange(defaultNodeRepulsion, COMPONENT_SPACING_MIN, COMPONENT_SPACING_MAX);

    let repulsionRunId = 0;
    let repulsionAnimationId = null;
    let layoutRunToken = 0;
    let layoutRefreshTimeout = null;

    function getEffectiveRepulsionScale() {
        return currentLayout === "cose" ? nodeRepulsionScale : nodeRepulsionScale * 0.2;
    }

    function getLayoutOptions() {
        const effectiveScale = getEffectiveRepulsionScale();
        const spacingFactor = scaleToOriginalRange(effectiveScale, 0.65, 1.45);
        const overlapPadding = scaleToOriginalRange(effectiveScale, 2, 18);
        const minNodeSpacing = scaleToOriginalRange(effectiveScale, 10, 45);
        const coseIdealEdgeLength = scaleToOriginalRange(effectiveScale, 70, 140);
        const coseNodeOverlap = scaleToOriginalRange(effectiveScale, 10, 30);

        if (currentLayout === "cose") {
            const baseOptions = {
                name: currentLayout,
                nodeRepulsion: nodeRepulsionValue,
                componentSpacing: componentSpacingValue,
                idealEdgeLength: coseIdealEdgeLength,
                nodeOverlap: coseNodeOverlap,
                padding: 30,
            };

            if (isGeneSymbolPage) {
                return {
                    ...baseOptions,
                    animate: true,
                    animationDuration: 500,
                    gravity: -1.2,
                    numIter: 1500,
                    initialTemp: 200,
                    coolingFactor: 0.95,
                    minTemp: 1.0,
                    edgeElasticity: 100,
                };
            }

            return baseOptions;
        }

        if (currentLayout === "grid") {
            return {
                name: currentLayout,
                avoidOverlap: true,
                avoidOverlapPadding: overlapPadding,
                spacingFactor: spacingFactor,
            };
        }

        if (currentLayout === "concentric") {
            return {
                name: currentLayout,
                minNodeSpacing: minNodeSpacing,
                avoidOverlap: true,
                spacingFactor: spacingFactor,
                padding: 30,
            };
        }

        if (currentLayout === "breadthfirst") {
            return {
                name: currentLayout,
                spacingFactor: spacingFactor,
                avoidOverlap: true,
                padding: 30,
            };
        }

        return { name: currentLayout };
    }

    function getVisibleComponentsForRepulsion() {
        const visibleElements = cy.elements().filter((ele) => ele.style("display") === "element");
        return visibleElements.components().filter((comp) => comp.nodes().length > 1);
    }

    function getGlobalRepulsionSpacingBase() {
        const visibleNodes = cy.nodes().filter((node) => node.style("display") === "element");
        const totalNodes = Math.max(1, visibleNodes.length);
        const zoom = cy.zoom() || 1;
        const width = Math.max(1, cy.width() / zoom);
        const height = Math.max(1, cy.height() / zoom);
        const area = Math.max(1, width * height);
        const baseSpacing = Math.sqrt(area / totalNodes);
        return {
            baseSpacing: Math.max(REPULSION_SPACING_MIN, baseSpacing),
            totalNodes,
        };
    }

    function buildRepulsionState(nodes, baseSpacing, repulsionScale) {
        if (!nodes || nodes.length < 2) return null;

        const nodeArray = nodes.toArray();
        const nodeCount = nodeArray.length;
        const positions = new Array(nodeCount);
        const movable = new Array(nodeCount);
        const degreesById = new Map();
        const nodeIdSet = new Set();

        nodeArray.forEach((node, idx) => {
            const nodeId = node.id();
            degreesById.set(nodeId, 0);
            nodeIdSet.add(nodeId);
            const pos = node.position();
            positions[idx] = { x: pos.x, y: pos.y };
            const grabbed = typeof node.grabbed === "function" && node.grabbed();
            movable[idx] = !node.locked() && !grabbed;
        });

        nodes.connectedEdges().forEach((edge) => {
            if (edge.style("display") !== "element") {
                return;
            }
            const source = edge.data("source");
            const target = edge.data("target");
            if (!nodeIdSet.has(source) || !nodeIdSet.has(target)) return;
            degreesById.set(source, (degreesById.get(source) || 0) + 1);
            degreesById.set(target, (degreesById.get(target) || 0) + 1);
        });

        const degrees = new Float32Array(nodeCount);
        let minDegree = Infinity;
        let maxDegree = -Infinity;

        nodeArray.forEach((node, idx) => {
            const degree = degreesById.get(node.id()) || 0;
            degrees[idx] = degree;
            minDegree = Math.min(minDegree, degree);
            maxDegree = Math.max(maxDegree, degree);
        });

        if (!Number.isFinite(minDegree) || !Number.isFinite(maxDegree)) {
            minDegree = 0;
            maxDegree = 0;
        }

        const bbox = nodes.boundingBox({ includeLabels: false, includeOverlays: false });
        let centerX = (bbox.x1 + bbox.x2) / 2;
        let centerY = (bbox.y1 + bbox.y2) / 2;

        if (!Number.isFinite(centerX) || !Number.isFinite(centerY)) {
            const sum = positions.reduce(
                (acc, pos) => {
                    acc.x += pos.x;
                    acc.y += pos.y;
                    return acc;
                },
                { x: 0, y: 0 },
            );
            centerX = sum.x / positions.length;
            centerY = sum.y / positions.length;
        }

        const spacingFactor = scaleToOriginalRange(
            repulsionScale,
            REPULSION_SPACING_FACTOR_MIN,
            REPULSION_SPACING_FACTOR_MAX,
        );
        const spacing = baseSpacing * spacingFactor;
        const strength = scaleToOriginalRange(repulsionScale, REPULSION_STRENGTH_MIN, REPULSION_STRENGTH_MAX);
        const radialStrength = scaleToOriginalRange(repulsionScale, REPULSION_RADIAL_MIN, REPULSION_RADIAL_MAX);

        const radialBase = Math.max(1, spacing * Math.sqrt(nodeCount));
        const minRadius = Math.max(spacing * 0.8, radialBase * 0.35);
        const maxRadius = Math.max(minRadius + spacing * 2, radialBase * 0.95 + spacing * 2);
        // Low-degree nodes drift toward the periphery while hubs stay closer to center.
        const targetRadii = new Float32Array(nodeCount);

        nodeArray.forEach((node, idx) => {
            const degree = degrees[idx];
            const normalized = maxDegree === minDegree ? 0.5 : (degree - minDegree) / (maxDegree - minDegree);
            targetRadii[idx] = minRadius + (1 - normalized) * (maxRadius - minRadius);
        });

        let iterations = 4;
        if (nodeCount > 2000) {
            iterations = 1;
        } else if (nodeCount > 1200) {
            iterations = 2;
        } else if (nodeCount > 800) {
            iterations = 3;
        }

        const step = nodeCount > 1200 ? 0.55 : 0.65;
        const maxShift = spacing * 0.4;

        return {
            nodes: nodeArray,
            positions,
            movable,
            targetRadii,
            center: { x: centerX, y: centerY },
            config: {
                spacing,
                strength,
                radialStrength,
                step,
                iterations,
                maxShift,
            },
        };
    }

    function applyRepulsionIteration(state) {
        const { nodes, positions, movable, targetRadii, center, config } = state;
        const count = nodes.length;
        const spacing = config.spacing;
        const spacingSq = spacing * spacing;
        const cellSize = Math.max(1, spacing);
        // Spatial hashing keeps neighbor checks fast for large graphs.
        const grid = new Map();
        const cellX = new Int32Array(count);
        const cellY = new Int32Array(count);
        const dispX = new Float32Array(count);
        const dispY = new Float32Array(count);

        for (let i = 0; i < count; i += 1) {
            const pos = positions[i];
            const cx = Math.floor(pos.x / cellSize);
            const cyCell = Math.floor(pos.y / cellSize);
            cellX[i] = cx;
            cellY[i] = cyCell;
            const key = `${cx},${cyCell}`;
            if (!grid.has(key)) {
                grid.set(key, []);
            }
            grid.get(key).push(i);
        }

        for (let i = 0; i < count; i += 1) {
            const cx = cellX[i];
            const cyCell = cellY[i];
            for (let gx = -1; gx <= 1; gx += 1) {
                for (let gy = -1; gy <= 1; gy += 1) {
                    const key = `${cx + gx},${cyCell + gy}`;
                    const bucket = grid.get(key);
                    if (!bucket) continue;
                    for (let b = 0; b < bucket.length; b += 1) {
                        const j = bucket[b];
                        if (j <= i) continue;
                        let dx = positions[i].x - positions[j].x;
                        let dy = positions[i].y - positions[j].y;
                        let distSq = dx * dx + dy * dy;
                        if (distSq < 0.01) {
                            dx = (i % 2 === 0 ? 1 : -1) * 0.01;
                            dy = (j % 2 === 0 ? 1 : -1) * 0.01;
                            distSq = dx * dx + dy * dy;
                        }
                        if (distSq >= spacingSq) continue;
                        const dist = Math.sqrt(distSq);
                        const force = ((spacing - dist) / spacing) * config.strength;
                        const ux = dx / dist;
                        const uy = dy / dist;
                        const fx = ux * force;
                        const fy = uy * force;
                        dispX[i] += fx;
                        dispY[i] += fy;
                        dispX[j] -= fx;
                        dispY[j] -= fy;
                    }
                }
            }
        }

        if (config.radialStrength > 0) {
            for (let i = 0; i < count; i += 1) {
                if (!movable[i]) continue;
                let dx = positions[i].x - center.x;
                let dy = positions[i].y - center.y;
                let dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 0.01) {
                    const angle = (i / count) * Math.PI * 2;
                    dx = Math.cos(angle);
                    dy = Math.sin(angle);
                    dist = 1;
                }
                const delta = (targetRadii[i] - dist) * config.radialStrength;
                dispX[i] += (dx / dist) * delta;
                dispY[i] += (dy / dist) * delta;
            }
        }

        let moved = false;
        cy.batch(() => {
            for (let i = 0; i < count; i += 1) {
                if (!movable[i]) continue;
                let dx = dispX[i] * config.step;
                let dy = dispY[i] * config.step;
                const shift = Math.hypot(dx, dy);
                if (shift > config.maxShift) {
                    const scale = config.maxShift / shift;
                    dx *= scale;
                    dy *= scale;
                }
                if (Math.abs(dx) > 0.001 || Math.abs(dy) > 0.001) {
                    moved = true;
                }
                positions[i].x += dx;
                positions[i].y += dy;
                nodes[i].position({ x: positions[i].x, y: positions[i].y });
            }
        });

        return moved;
    }

    function scheduleNodeRepulsion() {
        if (!cy) return;
        if (repulsionAnimationId) {
            cancelAnimationFrame(repulsionAnimationId);
        }
        const components = getVisibleComponentsForRepulsion();
        if (!components.length) return;
        const { baseSpacing } = getGlobalRepulsionSpacingBase();
        const effectiveScale = getEffectiveRepulsionScale();
        const states = components
            .map((comp) => buildRepulsionState(comp.nodes(), baseSpacing, effectiveScale))
            .filter(Boolean);
        if (!states.length) return;
        const runId = ++repulsionRunId;
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("tsumugi:repulsion:start", { detail: { runId } }));
        }
        const stateIterations = states.map(() => 0);

        const tick = () => {
            if (runId !== repulsionRunId) return;
            let anyActive = false;

            states.forEach((state, idx) => {
                if (stateIterations[idx] >= state.config.iterations) {
                    return;
                }
                const moved = applyRepulsionIteration(state);
                stateIterations[idx] += 1;
                if (!moved) {
                    stateIterations[idx] = state.config.iterations;
                    return;
                }
                if (stateIterations[idx] < state.config.iterations) {
                    anyActive = true;
                }
            });

            if (anyActive) {
                repulsionAnimationId = requestAnimationFrame(tick);
            } else {
                repulsionAnimationId = null;
                if (typeof window !== "undefined") {
                    window.dispatchEvent(new CustomEvent("tsumugi:repulsion:finish", { detail: { runId } }));
                }
            }
        };

        repulsionAnimationId = requestAnimationFrame(tick);
    }

    function runLayoutWithRepulsion() {
        if (!cy) return;
        if (repulsionAnimationId) {
            cancelAnimationFrame(repulsionAnimationId);
            repulsionAnimationId = null;
        }
        repulsionRunId += 1;
        const layout = cy.layout(getLayoutOptions());
        const token = ++layoutRunToken;
        cy.one("layoutstop", () => {
            if (token !== layoutRunToken) return;
            scheduleNodeRepulsion();
        });
        layout.run();
    }

    function updateRepulsionScale(scale) {
        nodeRepulsionScale = scale;
        nodeRepulsionValue = scaleToOriginalRange(scale, NODE_REPULSION_MIN, NODE_REPULSION_MAX);
        componentSpacingValue = scaleToOriginalRange(scale, COMPONENT_SPACING_MIN, COMPONENT_SPACING_MAX);
    }

    function setLayout(layoutName) {
        currentLayout = layoutName;
    }

    function getLayout() {
        return currentLayout;
    }

    function attachCy(instance) {
        cy = instance;
    }

    function queueLayoutRefresh(delayMs = 150) {
        if (!cy) return;
        if (layoutRefreshTimeout) {
            clearTimeout(layoutRefreshTimeout);
        }
        layoutRefreshTimeout = setTimeout(() => {
            runLayoutWithRepulsion();
            layoutRefreshTimeout = null;
        }, delayMs);
    }

    function clearLayoutRefresh() {
        if (layoutRefreshTimeout) {
            clearTimeout(layoutRefreshTimeout);
            layoutRefreshTimeout = null;
        }
    }

    function registerInitialLayoutStop() {
        if (!cy) return;
        cy.one("layoutstop", scheduleNodeRepulsion);
    }

    return {
        attachCy,
        clearLayoutRefresh,
        getLayout,
        getLayoutOptions,
        queueLayoutRefresh,
        registerInitialLayoutStop,
        runLayoutWithRepulsion,
        scheduleNodeRepulsion,
        setLayout,
        updateRepulsionScale,
    };
}

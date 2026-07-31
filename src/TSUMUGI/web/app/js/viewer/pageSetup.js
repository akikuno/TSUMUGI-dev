import { fetchJSONGz, loadJSONGz } from "../data/dataLoader.js";
import {
    buildInducedGeneElements,
    GENE_LIST_MIN_SHARED_CONTEXTS,
    GENE_PAGE_MIN_SHARED_CONTEXTS,
    selectGeneDisplayIds,
    validateGeneAsset,
    validateGeneListRequestGenes,
} from "../../../js/geneAssetUtils.js";

const GENE_ASSET_FETCH_CONCURRENCY = 12;
const GENE_LIST_REQUEST_PREFIX = "tsumugi:gene-list:";

export function getPageConfig() {
    const params = new URLSearchParams(window.location.search);
    const modeParam = params.get("mode");
    const mode = ["phenotype", "genesymbol", "genelist"].includes(modeParam || "") ? modeParam : "phenotype";
    const providedName = params.get("name") || "";
    const name = mode === "genelist" && !providedName ? "geneList" : providedName;
    const title = params.get("title") || name;
    const requestId = params.get("request") || "";

    return {
        mode,
        name,
        displayName: title || name || "TSUMUGI",
        requestId,
    };
}

export function hidePhenotypeOnlySections(isPhenotypePage) {
    document.querySelectorAll(".phenotype-only").forEach((el) => {
        el.style.display = isPhenotypePage ? "" : "none";
    });
}

export function isBinaryPhenotypeElements(elements) {
    const nodeElements = elements.filter((ele) => ele.data && ele.data.node_color !== undefined);
    if (!nodeElements.length) {
        return false;
    }

    const hideEffectSizeFlags = nodeElements
        .map((ele) => ele.data.hide_effect_size ?? ele.data.hide_severity)
        .filter((value) => value !== undefined);
    if (hideEffectSizeFlags.length && hideEffectSizeFlags.every(Boolean)) {
        return true;
    }

    const uniqueColors = [...new Set(nodeElements.map((ele) => ele.data.node_color).filter((v) => v !== undefined))];
    if (uniqueColors.length === 1) {
        const normalized = String(Math.round(Number(uniqueColors[0])));
        return ["0", "1", "100"].includes(normalized);
    }

    return false;
}

export function setPageTitle(config, mapSymbolToId, mapPhenotypeToId) {
    const pageTitleLink = document.getElementById("page-title-link");
    const pageTitle = config.displayName || config.name || "TSUMUGI";
    let targetUrl = "";

    if (config.mode === "phenotype" && mapPhenotypeToId) {
        const phenotypeId = mapPhenotypeToId[config.name];
        if (phenotypeId) {
            targetUrl = `https://www.mousephenotype.org/data/phenotypes/${phenotypeId}`;
        }
    } else if (config.mode === "genesymbol" && mapSymbolToId) {
        const accession = mapSymbolToId[config.name];
        if (accession) {
            targetUrl = `https://www.mousephenotype.org/data/genes/${accession}`;
        }
    }

    if (targetUrl) {
        pageTitleLink.href = targetUrl;
        pageTitleLink.target = "_blank";
        pageTitleLink.rel = "noreferrer";
        pageTitleLink.style.pointerEvents = "";
        pageTitleLink.style.cursor = "";
    } else {
        pageTitleLink.removeAttribute("href");
        pageTitleLink.style.pointerEvents = "none";
        pageTitleLink.style.cursor = "default";
    }

    pageTitleLink.textContent = pageTitle;
    document.title = `${pageTitle} | TSUMUGI`;
}

async function fetchText(path) {
    let text = "";
    try {
        const response = await fetch(path, { cache: "no-cache" });
        if (response.ok || response.status === 0) {
            text = (await response.text()).trim();
            if (text) {
                return text;
            }
        }
    } catch (error) {
        // fall through to the XHR fallback
    }

    return new Promise((resolve) => {
        try {
            const xhr = new XMLHttpRequest();
            xhr.open("GET", path, true);
            xhr.onload = () => {
                if (xhr.status === 0 || (xhr.status >= 200 && xhr.status < 300)) {
                    resolve(xhr.responseText.trim());
                } else {
                    resolve("");
                }
            };
            xhr.onerror = () => resolve("");
            xhr.send();
        } catch (e) {
            resolve("");
        }
    });
}

export async function setVersionLabel() {
    const versionLabel = document.getElementById("tsumugi-version");
    if (!versionLabel) return;

    const candidates = ["../version.txt", "./version.txt"];
    let versionText = "";

    for (const path of candidates) {
        versionText = await fetchText(path);
        if (versionText) break;
    }

    versionLabel.textContent = versionText || "-";
}

async function mapWithConcurrency(items, concurrency, callback) {
    const results = new Array(items.length);
    let nextIndex = 0;

    async function worker() {
        while (nextIndex < items.length) {
            const index = nextIndex;
            nextIndex += 1;
            results[index] = await callback(items[index], index);
        }
    }

    const workerCount = Math.min(concurrency, items.length);
    await Promise.all(Array.from({ length: workerCount }, () => worker()));
    return results;
}

async function loadGeneAssets(genes, initialAssets = new Map()) {
    const assets = new Map(initialAssets);
    const missingGenes = genes.filter((gene) => !assets.has(gene));
    const loadedAssets = await mapWithConcurrency(
        missingGenes,
        GENE_ASSET_FETCH_CONCURRENCY,
        async (gene) => {
            const asset = await fetchJSONGz(`../data/genesymbol/${encodeURIComponent(gene)}.json.gz`);
            return validateGeneAsset(asset, gene);
        },
    );
    loadedAssets.forEach((asset) => assets.set(asset.gene, asset));
    return genes.map((gene) => assets.get(gene));
}

function readGeneListRequest(requestId) {
    if (!requestId) {
        throw new Error("Gene List request identifier is missing.");
    }
    const stored = localStorage.getItem(`${GENE_LIST_REQUEST_PREFIX}${requestId}`);
    if (!stored) {
        throw new Error("Gene List request was not found. Please submit the list again.");
    }
    const request = JSON.parse(stored);
    if (!request) {
        throw new Error("Gene List request is invalid. Please submit the list again.");
    }
    const genes = validateGeneListRequestGenes(request.genes);
    return { ...request, genes };
}

export async function loadElementsForConfig(config) {
    if (config.mode === "phenotype") {
        return loadJSONGz(`../data/phenotype/${config.name}.json.gz`) || [];
    }

    if (config.mode === "genesymbol") {
        const targetAsset = validateGeneAsset(
            await fetchJSONGz(`../data/genesymbol/${encodeURIComponent(config.name)}.json.gz`),
            config.name,
        );
        const selectedGenes = selectGeneDisplayIds(targetAsset);
        const assets = await loadGeneAssets(selectedGenes, new Map([[config.name, targetAsset]]));
        return buildInducedGeneElements(assets, selectedGenes, {
            minSharedContexts: GENE_PAGE_MIN_SHARED_CONTEXTS,
            targetGene: config.name,
        });
    }

    const request = readGeneListRequest(config.requestId);
    const assets = await loadGeneAssets(request.genes);
    const elements = buildInducedGeneElements(assets, request.genes, {
        minSharedContexts: GENE_LIST_MIN_SHARED_CONTEXTS,
    });
    if (!elements.some((element) => element.data && element.data.source && element.data.target)) {
        throw new Error("No similar phenotypes were found among the entered genes.");
    }
    return elements;
}

export function renderEmptyState(message) {
    const container = document.querySelector(".cy");
    if (!container) return;

    container.innerHTML = `<div style="padding: 24px; font-size: 16px;">${message}</div>`;
}

export function applyNodeMinMax(elements, nodeColorMin, nodeColorMax) {
    // Ensure at least one gene pair remains visible even at slider extremes. Issue #72
    const nodeColorMap = new Map();
    elements.forEach((ele) => {
        if (ele.data.node_color !== undefined && ele.data.id !== undefined) {
            nodeColorMap.set(ele.data.id, ele.data.node_color);
        }
    });

    const sortedNodeColors = [...new Set([...nodeColorMap.values()])].sort((a, b) => a - b);
    if (sortedNodeColors.length === 0) {
        return { nodeMin: nodeColorMin, nodeMax: nodeColorMax };
    }

    const nodeColorToRank = new Map();
    sortedNodeColors.forEach((val, idx) => {
        nodeColorToRank.set(val, idx + 1);
    });

    const edgeRankPairs = [];
    elements.forEach((ele) => {
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

    if (edgeRankPairs.length === 0) {
        return { nodeMin: nodeColorMin, nodeMax: nodeColorMax };
    }

    const minRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum < b.rankSum ? a : b));
    const maxRankEdge = edgeRankPairs.reduce((a, b) => (a.rankSum > b.rankSum ? a : b));

    const nodeMin = minRankEdge.maxVal;
    const nodeMax = maxRankEdge.minVal;

    elements.forEach((ele) => {
        if (ele.data.node_color !== undefined) {
            ele.data.original_node_color = ele.data.node_color;

            if (ele.data.node_color <= nodeMin) {
                ele.data.node_color_for_filter = nodeMin;
            } else if (ele.data.node_color >= nodeMax) {
                ele.data.node_color_for_filter = nodeMax;
            } else {
                ele.data.node_color_for_filter = ele.data.node_color;
            }
        }
    });

    return { nodeMin, nodeMax };
}

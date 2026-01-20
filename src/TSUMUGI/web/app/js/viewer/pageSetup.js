import { loadJSONGz } from "../data/dataLoader.js";

export function getPageConfig() {
    const params = new URLSearchParams(window.location.search);
    const modeParam = params.get("mode");
    const mode = ["phenotype", "genesymbol", "genelist"].includes(modeParam || "") ? modeParam : "phenotype";
    const providedName = params.get("name") || "";
    const name = mode === "genelist" && !providedName ? "geneList" : providedName;
    const title = params.get("title") || name;

    return {
        mode,
        name,
        displayName: title || name || "TSUMUGI",
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

    const hideSeverityFlags = nodeElements
        .map((ele) => ele.data.hide_severity)
        .filter((value) => value !== undefined);
    if (hideSeverityFlags.length && hideSeverityFlags.every(Boolean)) {
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

export function loadElementsForConfig(config) {
    if (config.mode === "phenotype") {
        return loadJSONGz(`../data/phenotype/${config.name}.json.gz`) || [];
    }

    if (config.mode === "genesymbol") {
        return loadJSONGz(`../data/genesymbol/${config.name}.json.gz`) || [];
    }

    // Gene list page pulls data from localStorage
    try {
        const stored = localStorage.getItem("elements");
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error("Failed to parse stored elements for gene list:", error);
        return [];
    }
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

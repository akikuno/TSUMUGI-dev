import { GENE_LIST_MAX_NODES, normalizeGeneInput } from "./geneAssetUtils.js";

const AVAILABLE_GENE_LIST_SYMBOLS_URL = "./data/available_gene_list_symbols.txt";
const GENE_LIST_REQUEST_PREFIX = "tsumugi:gene-list:";
const GENE_LIST_REQUEST_MAX_AGE_MS = 24 * 60 * 60 * 1000;

let availableGeneListSymbolsPromise = null;

async function loadAvailableGeneListSymbols() {
    if (!availableGeneListSymbolsPromise) {
        availableGeneListSymbolsPromise = fetch(AVAILABLE_GENE_LIST_SYMBOLS_URL, { cache: "no-cache" }).then(
            async (response) => {
                if (!response.ok) {
                    throw new Error(`Failed to load available gene symbols: HTTP ${response.status}`);
                }
                return new Set(
                    (await response.text())
                        .split(/\r?\n/)
                        .map((gene) => gene.trim())
                        .filter(Boolean),
                );
            },
        );
    }
    return availableGeneListSymbolsPromise;
}

function cleanupExpiredRequests() {
    const now = Date.now();
    const expiredKeys = [];
    for (let index = 0; index < localStorage.length; index += 1) {
        const key = localStorage.key(index);
        if (!key || !key.startsWith(GENE_LIST_REQUEST_PREFIX)) continue;
        try {
            const request = JSON.parse(localStorage.getItem(key));
            if (!request.createdAt || now - request.createdAt > GENE_LIST_REQUEST_MAX_AGE_MS) {
                expiredKeys.push(key);
            }
        } catch (error) {
            expiredKeys.push(key);
        }
    }
    expiredKeys.forEach((key) => localStorage.removeItem(key));
}

function createRequestId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
        return window.crypto.randomUUID();
    }
    return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export async function fetchGeneData() {
    const geneList = document.getElementById("geneList").value;
    const submittedGenes = normalizeGeneInput(geneList);
    if (submittedGenes.length === 0) {
        alert("Please enter at least two gene symbols.");
        return;
    }

    let availableGenes;
    try {
        availableGenes = await loadAvailableGeneListSymbols();
    } catch (error) {
        console.error("Failed to validate Gene List input:", error);
        alert("Gene List validation data could not be loaded. Please try again.");
        return;
    }

    const validGenes = submittedGenes.filter((gene) => availableGenes.has(gene));
    const unavailableGenes = submittedGenes.filter((gene) => !availableGenes.has(gene));
    if (unavailableGenes.length > 0) {
        alert(`Unavailable genes were excluded:\n${unavailableGenes.join("\n")}`);
    }
    if (validGenes.length < 2) {
        alert("At least two available genes are required.");
        return;
    }
    if (validGenes.length > GENE_LIST_MAX_NODES) {
        alert(`Too many genes submitted. Please limit the number to ${GENE_LIST_MAX_NODES} or fewer.`);
        return;
    }

    try {
        cleanupExpiredRequests();
        const requestId = createRequestId();
        localStorage.setItem(
            `${GENE_LIST_REQUEST_PREFIX}${requestId}`,
            JSON.stringify({
                genes: validGenes,
                createdAt: Date.now(),
            }),
        );
        const query = new URLSearchParams({
            mode: "genelist",
            name: "geneList",
            title: "Gene List",
            request: requestId,
        });
        window.open(`./app/viewer.html?${query.toString()}`, "_blank");
    } catch (error) {
        console.error("Failed to prepare Gene List request:", error);
        alert("The Gene List request could not be stored. Please try again.");
    }
}

window.fetchGeneData = fetchGeneData;

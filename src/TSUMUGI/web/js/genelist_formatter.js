export async function fetchGzippedJson(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        const compressedData = await response.arrayBuffer();
        const decompressedData = pako.inflate(compressedData, { to: "string" });
        return JSON.parse(decompressedData);
    } catch (error) {
        console.error(`Data fetch error (${url}):`, error);
        return null; // Skip on error
    }
}

export function filterJson(jsonDataList, geneKeys) {
    const elementsMap = new Map();

    const serializePhenotypes = (phenotype) => {
        if (Array.isArray(phenotype)) {
            return JSON.stringify([...phenotype].sort());
        }
        if (typeof phenotype === "string") {
            return JSON.stringify([phenotype]);
        }
        return JSON.stringify([]);
    };

    const buildEdgeKey = (data) => {
        if (!("source" in data) || !("target" in data)) return null;
        const pairKey = [data.source, data.target].sort().join("||");
        return `edge:${pairKey}|${serializePhenotypes(data.phenotype)}`;
    };

    const buildNodeKey = (data) => ("id" in data ? `node:${data.id}` : null);

    const upsertEdge = (key, item) => {
        const existing = elementsMap.get(key);
        const newEdgeSize = Number.isFinite(item.data.edge_size) ? item.data.edge_size : Number.NEGATIVE_INFINITY;
        if (!existing) {
            elementsMap.set(key, item);
            return;
        }
        const existingEdgeSize = Number.isFinite(existing.data.edge_size)
            ? existing.data.edge_size
            : Number.NEGATIVE_INFINITY;
        if (newEdgeSize > existingEdgeSize) {
            elementsMap.set(key, item);
        }
    };

    jsonDataList.forEach((jsonData) => {
        jsonData.forEach((item) => {
            const data = item.data;

            if ("node_color" in data && data.node_color !== 1) return;

            const isEdge = "source" in data && "target" in data;

            if (isEdge) {
                if (!geneKeys.includes(data.source) || !geneKeys.includes(data.target)) return;
                const edgeKey = buildEdgeKey(data);
                if (!edgeKey) return;
                upsertEdge(edgeKey, item);
                return;
            }

            if ("id" in data && !geneKeys.includes(data.id)) return;

            const nodeKey = buildNodeKey(data);
            if (!nodeKey) return;
            if (!elementsMap.has(nodeKey)) {
                elementsMap.set(nodeKey, item);
            }
        });
    });

    return Array.from(elementsMap.values());
}

export async function fetchGeneData() {
    let jsonDataList = [];

    const geneList = document.getElementById("geneList").value;
    const geneKeys = geneList
        .split(/\r?\n/)
        .map((gene) => gene.trim())
        .filter((gene) => gene !== "");

    const fetchPromises = geneKeys.map((gene) => fetchGzippedJson(`./data/genesymbol/${gene}.json.gz`));

    const results = await Promise.all(fetchPromises);
    jsonDataList = results.filter((data) => data !== null);

    const elements = filterJson(jsonDataList, geneKeys);

    const uniqueIds = new Set(elements.map((el) => el.data.id).filter((id) => id !== undefined));

    if (uniqueIds.size === 0) {
        alert("No similar phenotypes were found among the entered genes.");
        return;
    } else if (uniqueIds.size >= 200) {
        alert("Too many genes submitted. Please limit the number to 200 or fewer.");
        return;
    }

    localStorage.removeItem("elements");
    localStorage.setItem("elements", JSON.stringify(elements));
    const query = new URLSearchParams({
        mode: "genelist",
        name: "geneList",
        title: "Gene List",
    });
    window.open(`./app/viewer.html?${query.toString()}`, "_blank");
}

// Expose for form submission handler
window.fetchGeneData = fetchGeneData;

// Assign event listener to button
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submitBtn_List").addEventListener("click", fetchGeneData);
});

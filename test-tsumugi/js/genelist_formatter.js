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
    let elements = new Set();

    jsonDataList.forEach(jsonData => {
        jsonData.forEach(item => {
            const data = item.data;

            if ("node_color" in data && data.node_color !== 1) return;
            if ("source" in data && "target" in data) {
                if (!geneKeys.includes(data.source) || !geneKeys.includes(data.target)) return;
            }
            if ("id" in data && !geneKeys.includes(data.id)) return;

            elements.add(JSON.stringify(item));
        });
    });

    return Array.from(elements).map(item => JSON.parse(item));
}

export async function fetchGeneData() {
    let jsonDataList = [];

    const geneList = document.getElementById("geneList").value;
    const geneKeys = geneList.split(/\r?\n/).map(gene => gene.trim()).filter(gene => gene !== "");

    const fetchPromises = geneKeys.map(gene =>
        fetchGzippedJson(`./data/genesymbol/${gene}.json.gz`)
    );

    const results = await Promise.all(fetchPromises);
    jsonDataList = results.filter(data => data !== null);

    const elements = filterJson(jsonDataList, geneKeys);

    const uniqueIds = new Set(elements.map(el => el.data.id).filter(id => id !== undefined));

    if (uniqueIds.size === 0) {
        alert("No similar phenotypes were found among the entered genes.");
        return;
    } else if (uniqueIds.size >= 200) {
        alert("Too many genes submitted. Please limit the number to 200 or fewer.");
        return;
    }

    localStorage.removeItem('elements');
    localStorage.setItem('elements', JSON.stringify(elements));
    window.open('./app/genelist/network_genelist.html', '_blank');
}

// Assign event listener to button
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submitBtn_List").addEventListener("click", fetchGeneData);
});

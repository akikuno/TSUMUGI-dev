import { calculateConnectedComponents } from "../graph/components.js";

export const DEFAULT_EXPORT_SCALE = 6.25;

function normalizeScale(scale) {
    const parsed = Number(scale);
    if (!Number.isFinite(parsed) || parsed <= 0) {
        return DEFAULT_EXPORT_SCALE;
    }
    return parsed;
}

function triggerDownloadFromBlob(blob, fileName) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function serializeModuleMemberships(modules) {
    if (!Array.isArray(modules)) return "";
    return modules
        .filter((module) => module && module.label)
        .map((module) => {
            const weight = Number(module.weight);
            const weightText = Number.isFinite(weight) ? weight.toFixed(3) : "";
            return `${module.label}:${weightText}:${module.support_count || 0}`;
        })
        .join(";");
}

function escapeCsv(value) {
    const text = String(value ?? "");
    return `"${text.replace(/"/g, '""')}"`;
}

// --------------------------------------------------------
// PNG Exporter
// --------------------------------------------------------

export function exportGraphAsPNG(cy, fileName, scale = DEFAULT_EXPORT_SCALE) {
    const pngContent = cy.png({
        scale: normalizeScale(scale), // Scale to achieve desired DPI
        full: true, // Set to true to include the entire graph, even the offscreen parts
    });

    const a = document.createElement("a");
    a.href = pngContent;
    a.download = `${fileName}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// --------------------------------------------------------
// JPG Exporter
// --------------------------------------------------------

export function exportGraphAsJPG(cy, fileName, scale = DEFAULT_EXPORT_SCALE) {
    const jpgContent = cy.jpg({
        scale: normalizeScale(scale),
        full: true,
        quality: 0.95,
    });

    const a = document.createElement("a");
    a.href = jpgContent;
    a.download = `${fileName}.jpg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// --------------------------------------------------------
// SVG Exporter
// --------------------------------------------------------

export function exportGraphAsSVG(cy, fileName, scale = DEFAULT_EXPORT_SCALE) {
    if (typeof cy.svg !== "function") {
        console.error("SVG export requires the cytoscape-svg extension.");
        return;
    }

    const svgContent = cy.svg({
        scale: normalizeScale(scale),
        full: true,
    });

    const blob = new Blob([svgContent], { type: "image/svg+xml;charset=utf-8" });
    triggerDownloadFromBlob(blob, `${fileName}.svg`);
}

// --------------------------------------------------------
// CSV Exporter
// --------------------------------------------------------

export function exportGraphAsCSV(cy, fileName) {
    // Use calculateConnectedComponents to gather connected components
    const connectedComponents = calculateConnectedComponents(cy);

    // CSV header row
    let csvContent = "module,gene,phenotypes,phenotype_axis_modules\n";

    // Assign module numbers and format the data as CSV rows
    connectedComponents.forEach((component, moduleIndex) => {
        const moduleNumber = moduleIndex + 1;

        Object.keys(component).forEach((gene) => {
            const phenotypes = component[gene].join(";"); // Join phenotypes with semicolons
            const node = cy.nodes().filter((candidate) => (candidate.data("label") || candidate.id()) === gene)[0];
            const modules = node ? serializeModuleMemberships(node.data("module_memberships")) : "";

            // Append each CSV row
            csvContent += `${moduleNumber},${escapeCsv(gene)},${escapeCsv(phenotypes)},${escapeCsv(modules)}\n`;
        });
    });

    // Generate and download the CSV file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${fileName}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// --------------------------------------------------------
// GraphML Exporter for Desktop Cytoscape Compatibility
// --------------------------------------------------------

export function exportGraphAsGraphML(cy, fileName) {
    const nodes = cy.nodes();
    const edges = cy.edges();

    // GraphML header
    let graphmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">

  <!-- Node attributes -->
  <key id="n0" for="node" attr.name="id" attr.type="string"/>
  <key id="n1" for="node" attr.name="label" attr.type="string"/>
  <key id="n2" for="node" attr.name="color" attr.type="double"/>
  <key id="n3" for="node" attr.name="phenotypes" attr.type="string"/>
  <key id="n4" for="node" attr.name="primary_module" attr.type="string"/>
  <key id="n5" for="node" attr.name="phenotype_axis_modules" attr.type="string"/>
  
  <!-- Edge attributes -->
  <key id="e0" for="edge" attr.name="interaction" attr.type="string"/>
  <key id="e1" for="edge" attr.name="width" attr.type="double"/>
  <key id="e2" for="edge" attr.name="shared_phenotypes" attr.type="string"/>
  <key id="e3" for="edge" attr.name="similarity" attr.type="double"/>
  <key id="e4" for="edge" attr.name="primary_module" attr.type="string"/>
  <key id="e5" for="edge" attr.name="phenotype_axis_modules" attr.type="string"/>

  <graph id="TSUMUGI_Network" edgedefault="undirected">
`;

    // Add nodes
    nodes.forEach((node) => {
        const data = node.data();
        const id = data.id || "";
        const label = data.label || id;
        const color = data.node_color || 0;
        const phenotypes = Array.isArray(data.phenotype) ? data.phenotype.join(";") : data.phenotype || "";
        const primaryModule = data.primary_module_label || data.primary_module || "";
        const moduleMemberships = serializeModuleMemberships(data.module_memberships);

        graphmlContent += `    <node id="${escapeXml(id)}">
      <data key="n0">${escapeXml(id)}</data>
      <data key="n1">${escapeXml(label)}</data>
      <data key="n2">${color}</data>
      <data key="n3">${escapeXml(phenotypes)}</data>
      <data key="n4">${escapeXml(primaryModule)}</data>
      <data key="n5">${escapeXml(moduleMemberships)}</data>
    </node>
`;
    });

    // Add edges
    edges.forEach((edge, index) => {
        const data = edge.data();
        const source = data.source || "";
        const target = data.target || "";
        const width = data.edge_size || 1;
        const sharedPhenotypes = Array.isArray(data.phenotype) ? data.phenotype.join(";") : data.phenotype || "";
        const similarity = data.similarity || 0;
        const primaryModule = data.primary_module_label || data.primary_module || "";
        const moduleMemberships = serializeModuleMemberships(data.module_memberships);

        graphmlContent += `    <edge id="e${index}" source="${escapeXml(source)}" target="${escapeXml(target)}">
      <data key="e0">interaction</data>
      <data key="e1">${width}</data>
      <data key="e2">${escapeXml(sharedPhenotypes)}</data>
      <data key="e3">${similarity}</data>
      <data key="e4">${escapeXml(primaryModule)}</data>
      <data key="e5">${escapeXml(moduleMemberships)}</data>
    </edge>
`;
    });

    // GraphML footer
    graphmlContent += `  </graph>
</graphml>`;

    // Download GraphML file
    const blob = new Blob([graphmlContent], { type: "application/xml;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${fileName}.graphml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// --------------------------------------------------------
// Utility function for XML escaping
// --------------------------------------------------------

function escapeXml(unsafe) {
    return String(unsafe ?? "").replace(/[<>&'"]/g, function (c) {
        switch (c) {
            case "<":
                return "&lt;";
            case ">":
                return "&gt;";
            case "&":
                return "&amp;";
            case "'":
                return "&apos;";
            case '"':
                return "&quot;";
        }
    });
}

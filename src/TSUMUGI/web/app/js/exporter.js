import { calculateConnectedComponents } from "./components.js";

// --------------------------------------------------------
// PNG Exporter
// --------------------------------------------------------

export function exportGraphAsPNG(cy, file_name) {
    const pngContent = cy.png({
        scale: 6.25, // Scale to achieve 600 DPI
        full: true, // Set to true to include the entire graph, even the offscreen parts
    });

    const a = document.createElement("a");
    a.href = pngContent;
    a.download = `${file_name}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// --------------------------------------------------------
// JPG Exporter
// --------------------------------------------------------

export function exportGraphAsJPG(cy, file_name) {
    const jpgContent = cy.jpg({
        scale: 6.25,
        full: true,
        quality: 0.95,
    });

    const a = document.createElement("a");
    a.href = jpgContent;
    a.download = `${file_name}.jpg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// --------------------------------------------------------
// CSV Exporter
// --------------------------------------------------------

export function exportGraphAsCSV(cy, file_name) {
    // Use calculateConnectedComponents to gather connected components
    const connected_component = calculateConnectedComponents(cy);

    // CSV header row
    let csvContent = "module,gene,phenotypes\n";

    // Assign module numbers and format the data as CSV rows
    connected_component.forEach((component, moduleIndex) => {
        const moduleNumber = moduleIndex + 1;

        Object.keys(component).forEach((gene) => {
            const phenotypes = component[gene].join(";"); // Join phenotypes with semicolons

            // Append each CSV row
            csvContent += `${moduleNumber},${gene},"${phenotypes}"\n`;
        });
    });

    // Generate and download the CSV file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${file_name}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// --------------------------------------------------------
// GraphML Exporter for Desktop Cytoscape Compatibility
// --------------------------------------------------------

export function exportGraphAsGraphML(cy, file_name) {
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
  
  <!-- Edge attributes -->
  <key id="e0" for="edge" attr.name="interaction" attr.type="string"/>
  <key id="e1" for="edge" attr.name="width" attr.type="double"/>
  <key id="e2" for="edge" attr.name="shared_phenotypes" attr.type="string"/>
  <key id="e3" for="edge" attr.name="similarity" attr.type="double"/>

  <graph id="TSUMUGI_Network" edgedefault="undirected">
`;

    // Add nodes
    nodes.forEach((node) => {
        const data = node.data();
        const id = data.id || "";
        const label = data.label || id;
        const color = data.node_color || 0;
        const phenotypes = Array.isArray(data.phenotype) ? data.phenotype.join(";") : data.phenotype || "";

        graphmlContent += `    <node id="${escapeXml(id)}">
      <data key="n0">${escapeXml(id)}</data>
      <data key="n1">${escapeXml(label)}</data>
      <data key="n2">${color}</data>
      <data key="n3">${escapeXml(phenotypes)}</data>
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

        graphmlContent += `    <edge id="e${index}" source="${escapeXml(source)}" target="${escapeXml(target)}">
      <data key="e0">interaction</data>
      <data key="e1">${width}</data>
      <data key="e2">${escapeXml(sharedPhenotypes)}</data>
      <data key="e3">${similarity}</data>
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
    a.download = `${file_name}.graphml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// --------------------------------------------------------
// Utility function for XML escaping
// --------------------------------------------------------

function escapeXml(unsafe) {
    return unsafe.replace(/[<>&'"]/g, function (c) {
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

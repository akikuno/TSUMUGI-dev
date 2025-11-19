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
// CSV Exporter
// --------------------------------------------------------

export function exportGraphAsCSV(cy, file_name) {
    // Use calculateConnectedComponents to obtain connected components
    const connected_component = calculateConnectedComponents(cy);

    // CSV header row
    let csvContent = "cluster,gene,phenotypes\n";

    // Assign cluster numbers and convert to CSV format
    connected_component.forEach((component, clusterIndex) => {
        const clusterNumber = clusterIndex + 1;

        Object.keys(component).forEach((gene) => {
            const phenotypes = component[gene].join(";"); // Join phenotypes separated by semicolons

            // Generate each CSV row
            csvContent += `${clusterNumber},${gene},"${phenotypes}"\n`;
        });
    });

    // Create and download the CSV file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${file_name}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

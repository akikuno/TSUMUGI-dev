import { calculateConnectedComponents } from "../graph/components.js";

export const DEFAULT_EXPORT_SCALE = 6.25;

function normalizeExportOptions(scaleOrOptions, maybeOptions = {}) {
    if (scaleOrOptions && typeof scaleOrOptions === "object") {
        return {
            scale: DEFAULT_EXPORT_SCALE,
            frameElements: [],
            frames: [],
            csvMode: "similarity",
            topLevelModuleDataKey: "top_level_module_memberships",
            ...scaleOrOptions,
        };
    }

    return {
        scale: scaleOrOptions ?? DEFAULT_EXPORT_SCALE,
        frameElements: [],
        frames: [],
        csvMode: "similarity",
        topLevelModuleDataKey: "top_level_module_memberships",
        ...maybeOptions,
    };
}

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

function serializeModuleLabels(modules) {
    if (!Array.isArray(modules)) return "";
    return modules
        .filter((module) => module && module.label)
        .map((module) => module.label)
        .join(";");
}

function getNodeModuleMemberships(node, exportOptions) {
    if (!node) return [];
    const publicMemberships = node.data("module_memberships");
    if (Array.isArray(publicMemberships) && publicMemberships.length > 0) {
        return publicMemberships;
    }
    const topLevelMemberships = node.data(exportOptions.topLevelModuleDataKey);
    return Array.isArray(topLevelMemberships) ? topLevelMemberships : [];
}

function escapeCsv(value) {
    const text = String(value ?? "");
    return `"${text.replace(/"/g, '""')}"`;
}

function withTemporaryElements(cy, elements, callback) {
    const safeElements = Array.isArray(elements) ? elements : [];
    if (safeElements.length === 0) {
        return callback();
    }

    let added = null;
    cy.startBatch();
    try {
        added = cy.add(safeElements);
    } finally {
        cy.endBatch();
    }

    try {
        return callback();
    } finally {
        if (added && added.length > 0) {
            cy.remove(added);
        }
    }
}

function getVisibleExportBounds(cy) {
    const visibleElements = cy.elements(":visible");
    if (visibleElements.length === 0) {
        return { x1: 0, y1: 0, x2: cy.width(), y2: cy.height(), w: cy.width(), h: cy.height() };
    }

    const bounds = visibleElements.boundingBox({ includeLabels: true, includeOverlays: false });
    if (!bounds || !Number.isFinite(bounds.x1) || !Number.isFinite(bounds.y1) || bounds.w <= 0 || bounds.h <= 0) {
        return { x1: 0, y1: 0, x2: cy.width(), y2: cy.height(), w: cy.width(), h: cy.height() };
    }

    return bounds;
}

function getFrameBounds(frame) {
    const labelPadding = 30;
    return {
        x1: Math.min(frame.x1, frame.labelX ?? frame.x1),
        y1: Math.min(frame.y1, (frame.labelY ?? frame.y1) - labelPadding),
        x2: frame.x2,
        y2: frame.y2,
    };
}

function combineBounds(baseBounds, frames) {
    return frames.reduce(
        (combined, frame) => {
            const frameBounds = getFrameBounds(frame);
            combined.x1 = Math.min(combined.x1, frameBounds.x1);
            combined.y1 = Math.min(combined.y1, frameBounds.y1);
            combined.x2 = Math.max(combined.x2, frameBounds.x2);
            combined.y2 = Math.max(combined.y2, frameBounds.y2);
            combined.w = combined.x2 - combined.x1;
            combined.h = combined.y2 - combined.y1;
            return combined;
        },
        { ...baseBounds },
    );
}

function loadImageFromDataUrl(dataUrl) {
    return new Promise((resolve, reject) => {
        const image = new Image();
        image.onload = () => resolve(image);
        image.onerror = reject;
        image.src = dataUrl;
    });
}

function canvasToBlob(canvas, mimeType, quality) {
    return new Promise((resolve) => {
        canvas.toBlob((blob) => resolve(blob), mimeType, quality);
    });
}

function drawRoundedRect(ctx, x, y, width, height, radius) {
    const safeRadius = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + safeRadius, y);
    ctx.lineTo(x + width - safeRadius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + safeRadius);
    ctx.lineTo(x + width, y + height - safeRadius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - safeRadius, y + height);
    ctx.lineTo(x + safeRadius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - safeRadius);
    ctx.lineTo(x, y + safeRadius);
    ctx.quadraticCurveTo(x, y, x + safeRadius, y);
    ctx.closePath();
}

function drawFramesOnCanvas(ctx, frames, bounds, scaleX, scaleY) {
    const averageScale = (scaleX + scaleY) / 2;
    const lineWidth = Math.max(2, 2 * averageScale);
    const fontSize = Math.max(12, 12 * averageScale);
    const labelPaddingX = Math.max(5, 5 * averageScale);
    const labelPaddingY = Math.max(3, 3 * averageScale);
    const labelHeight = fontSize + labelPaddingY * 2;

    ctx.save();
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = "#888888";
    ctx.setLineDash([Math.max(4, 6 * averageScale), Math.max(3, 4 * averageScale)]);
    frames.forEach((frame) => {
        const x = (frame.x1 - bounds.x1) * scaleX;
        const y = (frame.y1 - bounds.y1) * scaleY;
        const width = (frame.x2 - frame.x1) * scaleX;
        const height = (frame.y2 - frame.y1) * scaleY;
        ctx.strokeRect(x + lineWidth / 2, y + lineWidth / 2, Math.max(0, width - lineWidth), Math.max(0, height - lineWidth));
    });
    ctx.restore();

    ctx.save();
    ctx.font = `bold ${fontSize}px Arial, sans-serif`;
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#ffffff";
    frames.forEach((frame) => {
        const label = frame.label || "";
        if (!label) return;
        const x = (frame.labelX - bounds.x1) * scaleX;
        const centerY = (frame.labelY - bounds.y1) * scaleY;
        const textWidth = ctx.measureText(label).width;
        const boxWidth = textWidth + labelPaddingX * 2;
        const boxY = centerY - labelHeight / 2;
        ctx.fillStyle = "rgba(51, 51, 51, 0.85)";
        drawRoundedRect(ctx, x, boxY, boxWidth, labelHeight, Math.max(3, 3 * averageScale));
        ctx.fill();
        ctx.fillStyle = "#ffffff";
        ctx.fillText(label, x + labelPaddingX, centerY);
    });
    ctx.restore();
}

async function composeRasterExportWithFrames(dataUrl, cy, frames, mimeType, quality) {
    const safeFrames = Array.isArray(frames) ? frames : [];
    if (safeFrames.length === 0) {
        return null;
    }

    const image = await loadImageFromDataUrl(dataUrl);
    const baseBounds = getVisibleExportBounds(cy);
    const combinedBounds = combineBounds(baseBounds, safeFrames);
    const scaleX = image.width / baseBounds.w;
    const scaleY = image.height / baseBounds.h;
    const canvas = document.createElement("canvas");
    canvas.width = Math.ceil(combinedBounds.w * scaleX);
    canvas.height = Math.ceil(combinedBounds.h * scaleY);

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    if (mimeType === "image/jpeg") {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    ctx.drawImage(
        image,
        (baseBounds.x1 - combinedBounds.x1) * scaleX,
        (baseBounds.y1 - combinedBounds.y1) * scaleY,
        image.width,
        image.height,
    );
    drawFramesOnCanvas(ctx, safeFrames, combinedBounds, scaleX, scaleY);
    return canvasToBlob(canvas, mimeType, quality);
}

function parseSvgViewBox(svg) {
    const viewBox = svg.getAttribute("viewBox");
    if (viewBox) {
        const values = viewBox.trim().split(/\s+/).map(Number);
        if (values.length === 4 && values.every(Number.isFinite) && values[2] > 0 && values[3] > 0) {
            return { x: values[0], y: values[1], w: values[2], h: values[3] };
        }
    }

    const width = Number.parseFloat(svg.getAttribute("width")) || 1;
    const height = Number.parseFloat(svg.getAttribute("height")) || 1;
    return { x: 0, y: 0, w: width, h: height };
}

function appendSvgFrames(svgContent, cy, frames) {
    const safeFrames = Array.isArray(frames) ? frames : [];
    if (safeFrames.length === 0) return svgContent;

    const doc = new DOMParser().parseFromString(svgContent, "image/svg+xml");
    const svg = doc.documentElement;
    if (!svg || svg.nodeName.toLowerCase() !== "svg") return svgContent;

    const ns = "http://www.w3.org/2000/svg";
    const baseBounds = getVisibleExportBounds(cy);
    const combinedBounds = combineBounds(baseBounds, safeFrames);
    const viewBox = parseSvgViewBox(svg);
    const scaleX = viewBox.w / baseBounds.w;
    const scaleY = viewBox.h / baseBounds.h;
    const averageScale = (scaleX + scaleY) / 2;
    const combinedViewBox = {
        x: viewBox.x + (combinedBounds.x1 - baseBounds.x1) * scaleX,
        y: viewBox.y + (combinedBounds.y1 - baseBounds.y1) * scaleY,
        w: combinedBounds.w * scaleX,
        h: combinedBounds.h * scaleY,
    };

    svg.setAttribute("viewBox", `${combinedViewBox.x} ${combinedViewBox.y} ${combinedViewBox.w} ${combinedViewBox.h}`);
    svg.setAttribute("width", String(combinedViewBox.w));
    svg.setAttribute("height", String(combinedViewBox.h));

    const group = doc.createElementNS(ns, "g");
    group.setAttribute("class", "tsumugi-export-module-frames");
    group.setAttribute("fill", "none");
    group.setAttribute("stroke", "#888888");
    group.setAttribute("stroke-width", String(Math.max(2, 2 * averageScale)));
    group.setAttribute("stroke-dasharray", `${Math.max(4, 6 * averageScale)} ${Math.max(3, 4 * averageScale)}`);

    safeFrames.forEach((frame) => {
        const rect = doc.createElementNS(ns, "rect");
        rect.setAttribute("x", String(viewBox.x + (frame.x1 - baseBounds.x1) * scaleX));
        rect.setAttribute("y", String(viewBox.y + (frame.y1 - baseBounds.y1) * scaleY));
        rect.setAttribute("width", String((frame.x2 - frame.x1) * scaleX));
        rect.setAttribute("height", String((frame.y2 - frame.y1) * scaleY));
        group.appendChild(rect);
    });
    svg.appendChild(group);

    const labelGroup = doc.createElementNS(ns, "g");
    labelGroup.setAttribute("class", "tsumugi-export-module-labels");
    const fontSize = Math.max(12, 12 * averageScale);
    const labelPaddingX = Math.max(5, 5 * averageScale);
    const labelPaddingY = Math.max(3, 3 * averageScale);
    const labelHeight = fontSize + labelPaddingY * 2;
    safeFrames.forEach((frame) => {
        const label = frame.label || "";
        if (!label) return;
        const x = viewBox.x + (frame.labelX - baseBounds.x1) * scaleX;
        const centerY = viewBox.y + (frame.labelY - baseBounds.y1) * scaleY;
        const approxTextWidth = label.length * fontSize * 0.58;

        const labelRect = doc.createElementNS(ns, "rect");
        labelRect.setAttribute("x", String(x));
        labelRect.setAttribute("y", String(centerY - labelHeight / 2));
        labelRect.setAttribute("width", String(approxTextWidth + labelPaddingX * 2));
        labelRect.setAttribute("height", String(labelHeight));
        labelRect.setAttribute("rx", String(Math.max(3, 3 * averageScale)));
        labelRect.setAttribute("fill", "#333333");
        labelRect.setAttribute("fill-opacity", "0.85");
        labelRect.setAttribute("stroke", "none");
        labelGroup.appendChild(labelRect);

        const text = doc.createElementNS(ns, "text");
        text.textContent = label;
        text.setAttribute("x", String(x + labelPaddingX));
        text.setAttribute("y", String(centerY));
        text.setAttribute("fill", "#ffffff");
        text.setAttribute("font-family", "Arial, sans-serif");
        text.setAttribute("font-size", String(fontSize));
        text.setAttribute("font-weight", "bold");
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("stroke", "none");
        labelGroup.appendChild(text);
    });
    svg.appendChild(labelGroup);

    return new XMLSerializer().serializeToString(doc);
}

// --------------------------------------------------------
// PNG Exporter
// --------------------------------------------------------

export async function exportGraphAsPNG(cy, fileName, scaleOrOptions = DEFAULT_EXPORT_SCALE, maybeOptions = {}) {
    const options = normalizeExportOptions(scaleOrOptions, maybeOptions);
    const pngContent = withTemporaryElements(cy, options.frameElements, () => cy.png({
        scale: normalizeScale(options.scale), // Scale to achieve desired DPI
        full: true, // Set to true to include the entire graph, even the offscreen parts
    }));

    try {
        const framedBlob = await composeRasterExportWithFrames(pngContent, cy, options.frames, "image/png");
        if (framedBlob) {
            triggerDownloadFromBlob(framedBlob, `${fileName}.png`);
            return;
        }
    } catch (error) {
        console.warn("Failed to compose module frames into PNG export.", error);
    }

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

export async function exportGraphAsJPG(cy, fileName, scaleOrOptions = DEFAULT_EXPORT_SCALE, maybeOptions = {}) {
    const options = normalizeExportOptions(scaleOrOptions, maybeOptions);
    const jpgContent = withTemporaryElements(cy, options.frameElements, () => cy.jpg({
        scale: normalizeScale(options.scale),
        full: true,
        quality: 0.95,
    }));

    try {
        const framedBlob = await composeRasterExportWithFrames(jpgContent, cy, options.frames, "image/jpeg", 0.95);
        if (framedBlob) {
            triggerDownloadFromBlob(framedBlob, `${fileName}.jpg`);
            return;
        }
    } catch (error) {
        console.warn("Failed to compose module frames into JPG export.", error);
    }

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

export function exportGraphAsSVG(cy, fileName, scaleOrOptions = DEFAULT_EXPORT_SCALE, maybeOptions = {}) {
    if (typeof cy.svg !== "function") {
        console.error("SVG export requires the cytoscape-svg extension.");
        return;
    }

    const options = normalizeExportOptions(scaleOrOptions, maybeOptions);
    const svgContent = withTemporaryElements(cy, options.frameElements, () => cy.svg({
        scale: normalizeScale(options.scale),
        full: true,
    }));
    let exportContent = svgContent;
    try {
        exportContent = appendSvgFrames(svgContent, cy, options.frames);
    } catch (error) {
        console.warn("Failed to compose module frames into SVG export.", error);
    }

    const blob = new Blob([exportContent], { type: "image/svg+xml;charset=utf-8" });
    triggerDownloadFromBlob(blob, `${fileName}.svg`);
}

// --------------------------------------------------------
// CSV Exporter
// --------------------------------------------------------

export function exportGraphAsCSV(cy, fileName, options = {}) {
    const exportOptions = normalizeExportOptions(options);
    // Use calculateConnectedComponents to gather connected components
    const connectedComponents = calculateConnectedComponents(cy);
    const isTopLevelMpMode = exportOptions.csvMode === "top-level-mp";

    // CSV header row
    let csvContent = isTopLevelMpMode
        ? "Top-level-MP,gene,phenotypes,phenotype_axis_modules\n"
        : "module,gene,phenotypes,phenotype_axis_modules\n";

    // Assign module numbers and format the data as CSV rows
    connectedComponents.forEach((component, moduleIndex) => {
        const moduleNumber = moduleIndex + 1;

        Object.keys(component).forEach((gene) => {
            const phenotypes = component[gene].join(";"); // Join phenotypes with semicolons
            const node = cy.nodes().filter((candidate) => (candidate.data("label") || candidate.id()) === gene)[0];
            const memberships = getNodeModuleMemberships(node, exportOptions);
            const modules = serializeModuleMemberships(memberships);
            if (isTopLevelMpMode) {
                const topLevelMp = serializeModuleLabels(memberships);
                csvContent += `${escapeCsv(topLevelMp)},${escapeCsv(gene)},${escapeCsv(phenotypes)},${escapeCsv(modules)}\n`;
                return;
            }

            // Append each CSV row
            csvContent += `${moduleNumber},${escapeCsv(gene)},${escapeCsv(phenotypes)},${escapeCsv(modules)}\n`;
        });
    });

    // Generate and download the CSV file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    triggerDownloadFromBlob(blob, `${fileName}.csv`);
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

// ============================================================
// Tooltip + Info Tooltip Utilities
// ============================================================

const DEFAULT_TOOLTIP_HEIGHT = 220;
const MIN_TOOLTIP_WIDTH = 220;
const MIN_TOOLTIP_HEIGHT = 140;
const MIN_SECTION_HEIGHT = 80;
const TOOLTIP_OFFSET = 10;
const DEFAULT_SECTION_HEIGHTS = {
    phenotypes: 120,
    diseases: 90,
    modules: 160,
};

let infoTooltipsInitialized = false;

function formatPhenotypesWithHighlight(phenotypes, targetPhenotype) {
    const safePhenotypes = Array.isArray(phenotypes) ? phenotypes : [];
    const cleanedPhenotypes = safePhenotypes.filter((phenotype) => phenotype && phenotype !== "");
    if (!targetPhenotype) {
        return cleanedPhenotypes.map((anno) => "・ " + anno).join("<br>");
    }

    const matching = [];
    const others = [];

    for (const phenotype of cleanedPhenotypes) {
        if (phenotype.startsWith(targetPhenotype)) {
            matching.push(phenotype);
        } else {
            others.push(phenotype);
        }
    }

    const ordered = [...matching, ...others];

    return ordered
        .map((phenotype) =>
            phenotype.startsWith(targetPhenotype) ? `▶ ${phenotype}` : "・ " + phenotype,
        )
        .join("<br>");
}

function buildNodeTooltipContent({ data, mapSymbolToId, targetPhenotype, nodeColorValues }) {
    const geneId = mapSymbolToId[data.id] || "UNKNOWN";
    const urlImpc = `https://www.mousephenotype.org/data/genes/${geneId}`;
    const shouldHideSeverity = Boolean(data.hide_severity);
    const rawSeverity = Number.isFinite(data.original_node_color) ? data.original_node_color : data.node_color;
    const nodeColorSet = Array.isArray(nodeColorValues) ? new Set(nodeColorValues) : new Set();
    const uniqueValues = [...nodeColorSet];
    const isBinary =
        uniqueValues.length === 1 &&
        ["0", "1", "100"].includes(String(Math.round(Number(uniqueValues[0]))));
    const severityValue =
        !shouldHideSeverity && !isBinary && Number.isFinite(rawSeverity) ? Math.round(rawSeverity) : null;
    const severityText = severityValue !== null ? ` (Severity: ${severityValue})` : "";

    const phenotypes = Array.isArray(data.phenotype)
        ? data.phenotype
        : data.phenotype
            ? [data.phenotype]
            : [];
    const diseases = Array.isArray(data.disease)
        ? data.disease
        : data.disease
            ? [data.disease]
            : [];
    const phenotypesHtml = formatPhenotypesWithHighlight(phenotypes, targetPhenotype);
    const phenotypeSection = `
        <div class="cy-tooltip__section cy-tooltip__section--phenotypes" data-section="phenotypes">
            <div class="cy-tooltip__section-title">
                <b>Phenotypes of <a href="${urlImpc}" target="_blank">${data.id} KO mice</a>${severityText}</b>
            </div>
            <div class="cy-tooltip__section-body">${phenotypesHtml}</div>
        </div>
    `;

    const cleanedDiseases = diseases.filter((disease) => disease && disease !== "");
    let diseaseSection = "";
    if (cleanedDiseases.length > 0) {
        const diseasesHtml = cleanedDiseases.map((disease) => "・ " + disease).join("<br>");
        diseaseSection = `
            <div class="cy-tooltip__section cy-tooltip__section--diseases" data-section="diseases">
                <div class="cy-tooltip__section-title"><b>Associated Human Diseases</b></div>
                <div class="cy-tooltip__section-body">${diseasesHtml}</div>
            </div>
        `;
    }

    return `${phenotypeSection}${diseaseSection}`;
}

function buildEdgeTooltipContent({ data, cy, targetPhenotype }) {
    const phenotypes = Array.isArray(data.phenotype)
        ? data.phenotype
        : data.phenotype
            ? [data.phenotype]
            : [];
    const sourceNode = cy.getElementById(data.source).data("label");
    const targetNode = cy.getElementById(data.target).data("label");
    const hasSimilarityValue = Number.isFinite(data.edge_size);
    const similarityText = hasSimilarityValue ? ` (Similarity: ${Math.round(data.edge_size)})` : "";

    let tooltipText = `<div><b>Shared phenotypes of ${sourceNode} and ${targetNode} KOs${similarityText}</b><br>`;
    tooltipText += formatPhenotypesWithHighlight(phenotypes, targetPhenotype);
    tooltipText += "</div>";

    const sourcePos = cy.getElementById(data.source).renderedPosition();
    const targetPos = cy.getElementById(data.target).renderedPosition();
    const position = {
        x: (sourcePos.x + targetPos.x) / 2,
        y: (sourcePos.y + targetPos.y) / 2,
    };

    return { content: tooltipText, position };
}

function createTooltipContent(event, cy, mapSymbolToId, targetPhenotype, { nodeColorValues } = {}) {
    const data = event.target.data();

    if (event.target.isNode()) {
        return {
            content: buildNodeTooltipContent({ data, mapSymbolToId, targetPhenotype, nodeColorValues }),
            position: event.target.renderedPosition(),
        };
    }

    if (event.target.isEdge()) {
        return buildEdgeTooltipContent({ data, cy, targetPhenotype });
    }

    return { content: "", position: { x: 0, y: 0 } };
}

function setTooltipPosition(tooltip, position) {
    tooltip.style.left = `${Math.round(position.x + TOOLTIP_OFFSET)}px`;
    tooltip.style.top = `${Math.round(position.y + TOOLTIP_OFFSET)}px`;
}

function enableTooltipDrag(tooltip, containerElement = null) {
    let isDragging = false;
    let dragOffset = { x: 0, y: 0 };
    const container = containerElement || tooltip.parentElement || document.querySelector(".cy");
    if (!container) return;

    const startDrag = (clientX, clientY) => {
        const rect = tooltip.getBoundingClientRect();
        dragOffset = {
            x: clientX - rect.left,
            y: clientY - rect.top,
        };
        isDragging = true;
        tooltip.style.cursor = "grabbing";
    };

    const handleDrag = (clientX, clientY) => {
        if (!isDragging) return;
        const containerRect = container.getBoundingClientRect();
        tooltip.style.left = `${clientX - dragOffset.x - containerRect.left}px`;
        tooltip.style.top = `${clientY - dragOffset.y - containerRect.top}px`;
    };

    const stopDrag = () => {
        isDragging = false;
        tooltip.style.cursor = "move";
    };

    // Mouse events
    tooltip.addEventListener("mousedown", (event) => {
        if (event.target.closest(".cy-tooltip__resize-handle")) return;
        event.stopPropagation();
        startDrag(event.clientX, event.clientY);
    });

    document.addEventListener("mousemove", (event) => {
        handleDrag(event.clientX, event.clientY);
    });

    document.addEventListener("mouseup", stopDrag);

    // Touch events for tablet/mobile support
    tooltip.addEventListener("touchstart", (event) => {
        if (event.target.closest(".cy-tooltip__resize-handle")) return;
        event.stopPropagation();
        event.preventDefault();
        const touch = event.touches[0];
        startDrag(touch.clientX, touch.clientY);
    });

    document.addEventListener("touchmove", (event) => {
        if (!isDragging) return;
        event.preventDefault();
        const touch = event.touches[0];
        handleDrag(touch.clientX, touch.clientY);
    });

    document.addEventListener("touchend", stopDrag);
}

function updateTooltipSectionHeights(tooltip, tooltipHeight = DEFAULT_TOOLTIP_HEIGHT) {
    const safeHeight = Math.max(MIN_TOOLTIP_HEIGHT, tooltipHeight);
    const sections = Array.from(tooltip.querySelectorAll(".cy-tooltip__section"));
    if (sections.length === 0) return;

    // Distribute space by section weights, while keeping each section readable.
    const styles = window.getComputedStyle(tooltip);
    const paddingY = parseFloat(styles.paddingTop || "0") + parseFloat(styles.paddingBottom || "0");
    const gapY = parseFloat(styles.rowGap || styles.gap || "0");
    const reservedHeight = paddingY + gapY * Math.max(0, sections.length - 1);
    const availableHeight = Math.max(MIN_SECTION_HEIGHT * sections.length, safeHeight - reservedHeight);

    const weights = sections.map((section) => {
        const key = section.dataset.section;
        return DEFAULT_SECTION_HEIGHTS[key] || MIN_SECTION_HEIGHT;
    });
    const totalWeight = weights.reduce((sum, w) => sum + w, 0) || 1;

    sections.forEach((section, idx) => {
        const weight = weights[idx];
        const target = Math.max(
            MIN_SECTION_HEIGHT,
            Math.round((weight / totalWeight) * availableHeight),
        );

        section.style.maxHeight = `${target}px`;

        const key = section.dataset.section;
        if (key) {
            tooltip.style.setProperty(`--cy-tooltip-${key}-max`, `${target}px`);
        }
    });

    tooltip.style.setProperty("--cy-tooltip-height", `${Math.round(safeHeight)}px`);
}

function applyInitialTooltipSize(tooltip) {
    const rect = tooltip.getBoundingClientRect();
    const width = Math.max(MIN_TOOLTIP_WIDTH, Math.round(rect.width));
    const height = Math.max(MIN_TOOLTIP_HEIGHT, Math.round(rect.height || DEFAULT_TOOLTIP_HEIGHT));

    tooltip.style.width = `${width}px`;
    tooltip.style.height = `${height}px`;
    updateTooltipSectionHeights(tooltip, height);
}

function enableTooltipResize(tooltip, containerElement = null) {
    const container = containerElement || tooltip.parentElement || document.querySelector(".cy");
    if (!container) return;

    const resizeHandle = document.createElement("div");
    resizeHandle.classList.add("cy-tooltip__resize-handle");
    tooltip.appendChild(resizeHandle);

    resizeHandle.addEventListener("pointerdown", (event) => {
        event.preventDefault();
        event.stopPropagation();

        const startRect = tooltip.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        const startLeft = tooltip.offsetLeft;
        const startTop = tooltip.offsetTop;
        const startX = event.clientX;
        const startY = event.clientY;

        const handlePointerMove = (moveEvent) => {
            // Dragging left increases width while anchoring the right edge.
            const deltaX = startX - moveEvent.clientX;
            const deltaY = moveEvent.clientY - startY;

            let newWidth = startRect.width + deltaX;
            let newLeft = startLeft - deltaX;
            let newHeight = startRect.height + deltaY;

            const containerWidth = containerRect.width;
            const containerHeight = containerRect.height;
            const minWidth = Math.min(MIN_TOOLTIP_WIDTH, containerWidth);
            const minHeight = Math.min(MIN_TOOLTIP_HEIGHT, containerHeight);

            newWidth = Math.max(minWidth, newWidth);
            newHeight = Math.max(minHeight, newHeight);

            if (newLeft < 0) {
                newWidth += newLeft;
                newLeft = 0;
            }

            const maxLeft = Math.max(0, containerWidth - minWidth);
            if (newLeft > maxLeft) {
                newLeft = maxLeft;
            }

            const maxWidth = containerWidth - newLeft;
            newWidth = Math.min(maxWidth, newWidth);
            if (newWidth < minWidth) {
                newWidth = minWidth;
                newLeft = Math.max(0, containerWidth - newWidth);
            }

            const maxHeight = Math.max(minHeight, containerHeight - startTop);
            newHeight = Math.min(maxHeight, newHeight);

            tooltip.style.width = `${Math.round(newWidth)}px`;
            tooltip.style.left = `${Math.round(newLeft)}px`;
            tooltip.style.height = `${Math.round(newHeight)}px`;
            updateTooltipSectionHeights(tooltip, newHeight);
        };

        const stopResize = () => {
            document.removeEventListener("pointermove", handlePointerMove);
            document.removeEventListener("pointerup", stopResize);
        };

        document.addEventListener("pointermove", handlePointerMove);
        document.addEventListener("pointerup", stopResize);
    });
}

function isolateTooltipScroll(tooltip, cyInstance = null) {
    void cyInstance;
    const stopScrollPropagation = (event) => {
        event.stopPropagation();
    };

    // Capture-phase listeners ensure Cytoscape does not see wheel/touch events.
    tooltip.addEventListener("wheel", stopScrollPropagation, { passive: true, capture: true });
    tooltip.addEventListener("mousewheel", stopScrollPropagation, { passive: true, capture: true });
    tooltip.addEventListener("touchstart", stopScrollPropagation, { passive: true, capture: true });
    tooltip.addEventListener("touchmove", stopScrollPropagation, { passive: true, capture: true });

    // Allow cleanup if the tooltip is removed while hovered.
    tooltip.__restoreCyInteractions = () => {};
}

function addCopyButtonToTooltip(tooltip) {
    const copyWrapper = document.createElement("div");
    copyWrapper.classList.add("cy-tooltip__copy");
    copyWrapper.innerHTML =
        '<button class="cy-tooltip__copy-btn" title="Copy to clipboard" aria-label="Copy to clipboard">' +
        '<i class="fa-regular fa-copy"></i>' +
        "</button>";
    tooltip.appendChild(copyWrapper);

    const button = copyWrapper.querySelector("button");
    button.addEventListener("mousedown", (event) => event.stopPropagation());
    button.addEventListener("click", (event) => {
        event.stopPropagation();

        // Clone the tooltip so the copy button can be stripped before exporting text.
        const clone = tooltip.cloneNode(true);
        const buttonInClone = clone.querySelector(".cy-tooltip__copy");
        if (buttonInClone) {
            buttonInClone.remove();
        }

        let extractedHtml = clone.innerHTML;
        extractedHtml = extractedHtml.replace(/<br\s*\/?>/gi, "\n");
        extractedHtml = extractedHtml.replace(/<\/div>/gi, "</div>\n");

        const tempElement = document.createElement("div");
        tempElement.innerHTML = extractedHtml;
        let text = tempElement.textContent || tempElement.innerText || "";
        text = text.replace(/\n\s*\n/g, "\n").trim();

        if (navigator.clipboard) {
            navigator.clipboard
                .writeText(text)
                .then(() => {
                    button.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => (button.innerHTML = '<i class="fa-regular fa-copy"></i>'), 2000);
                })
                .catch((error) => {
                    console.error("Failed to copy:", error);
                    alert("Failed to copy to clipboard");
                });
        } else {
            alert("Clipboard API not available");
        }
    });
}

function createTooltipElement({ content, position, containerSelector = ".cy", cyInstance = null }) {
    removeTooltips();

    const container = document.querySelector(containerSelector);
    if (!container) {
        console.warn(`Container "${containerSelector}" not found; tooltip not rendered.`);
        return null;
    }

    const tooltip = document.createElement("div");
    tooltip.classList.add("cy-tooltip");
    tooltip.innerHTML = content;
    setTooltipPosition(tooltip, position);

    container.appendChild(tooltip);
    applyInitialTooltipSize(tooltip);
    addCopyButtonToTooltip(tooltip);
    enableTooltipDrag(tooltip, container);
    enableTooltipResize(tooltip, container);
    isolateTooltipScroll(tooltip, cyInstance);

    return tooltip;
}

function closeInfoTooltips(except = null) {
    document.querySelectorAll(".info-tooltip-container.active").forEach((el) => {
        if (el !== except) {
            el.classList.remove("active");
        }
    });
}

/**
 * Enable click-to-toggle info tooltips using a single delegated listener.
 */
export function initInfoTooltips() {
    if (infoTooltipsInitialized) return;
    infoTooltipsInitialized = true;

    // Event delegation keeps newly injected tooltip icons working.
    document.addEventListener("click", (event) => {
        const icon = event.target.closest(".info-tooltip-icon");
        const container = event.target.closest(".info-tooltip-container");

        if (icon && container) {
            event.preventDefault();
            const isActive = container.classList.toggle("active");
            if (isActive) {
                closeInfoTooltips(container);
            }
            return;
        }

        if (!container) {
            closeInfoTooltips();
        }
    });
}

/**
 * Render a tooltip for the current Cytoscape event target.
 */
export function showTooltip(event, cy, mapSymbolToId, targetPhenotype = null, options = {}) {
    const { content, position } = createTooltipContent(event, cy, mapSymbolToId, targetPhenotype, options);

    if (!content) return;

    createTooltipElement({
        content,
        position,
        containerSelector: ".cy",
        cyInstance: cy,
    });
}

export function removeTooltips() {
    document.querySelectorAll(".cy-tooltip").forEach((el) => {
        if (typeof el.__restoreCyInteractions === "function") {
            el.__restoreCyInteractions();
        }
        el.remove();
    });
}

/**
 * Render a custom tooltip at a fixed rendered position.
 */
export function showCustomTooltip({ content, position, containerSelector = ".cy", cyInstance = null }) {
    createTooltipElement({ content, position, containerSelector, cyInstance });
}

/**
 * Render a module summary tooltip for a connected component.
 */
export function showSubnetworkTooltip({ component, renderedPos, containerSelector = ".cy", cyInstance = null }) {
    if (!component) return;

    const lines =
        component.phenotypes && component.phenotypes.length > 0
            ? component.phenotypes.map(([name, count]) => `・ ${name} (${count})`)
            : ["No shared phenotypes on visible edges."];

    const infoIcon = `
        <div class="info-tooltip-container">
            <div class="info-tooltip-icon" aria-label="Tooltip: shared phenotype counts">i</div>
            <div class="info-tooltip-content">
                The number in parentheses indicates the count of shared phenotypes within the module.
            </div>
        </div>
    `;

    const header = `
        <div class="cy-tooltip__header">
            <b>Phenotypes shared in Module ${component.id}</b>
            ${infoIcon}
        </div>
    `;
    const linesHtml = lines.join("<br>");
    const bodySection = `
        <div class="cy-tooltip__section cy-tooltip__section--modules" data-section="modules">
            <div class="cy-tooltip__section-body">${linesHtml}</div>
        </div>
    `;
    const tooltipContent = `${header}${bodySection}`;
    const anchor =
        renderedPos ||
        {
            x: (component.bbox.x1 + component.bbox.x2) / 2,
            y: (component.bbox.y1 + component.bbox.y2) / 2,
        };

    createTooltipElement({ content: tooltipContent, position: anchor, containerSelector, cyInstance });
}

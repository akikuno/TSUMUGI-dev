// ############################################################
// Tooltip Handling Functions
// ############################################################

const DEFAULT_TOOLTIP_HEIGHT = 220;
const MIN_TOOLTIP_WIDTH = 220;
const MIN_TOOLTIP_HEIGHT = 140;
const MIN_SECTION_HEIGHT = 80;
const DEFAULT_SECTION_HEIGHTS = {
    phenotypes: 120,
    diseases: 90,
    modules: 160,
};

/*
    Formats phenotypes for tooltips, placing and highlighting the target phenotype at the top.
*/
function formatPhenotypesWithHighlight(phenotypes, target_phenotype) {
    if (!target_phenotype) {
        return phenotypes.map((anno) => "・ " + anno).join("<br>");
    }

    const matching = [];
    const others = [];

    for (const phenotype of phenotypes) {
        if (phenotype.startsWith(target_phenotype)) {
            matching.push(phenotype);
        } else {
            others.push(phenotype);
        }
    }

    const ordered = [...matching, ...others];

    return ordered
        .map((phenotype) => {
            if (phenotype.startsWith(target_phenotype)) {
                return `▶ ${phenotype}`;
            } else {
                return "・ " + phenotype;
            }
        })
        .join("<br>");
}

function createTooltip(
    event,
    cy,
    map_symbol_to_id,
    target_phenotype = null,
    { allNodeColors } = {},
) {
    const data = event.target.data();
    let tooltipText = "";
    let pos;

    const phenotypes = Array.isArray(data.phenotype) ? data.phenotype : [data.phenotype];
    const diseases = Array.isArray(data.disease) ? data.disease : [data.disease];

    if (event.target.isNode()) {
        const geneID = map_symbol_to_id[data.id] || "UNKNOWN";
        const url_impc = `https://www.mousephenotype.org/data/genes/${geneID}`;
        const shouldHideSeverity = Boolean(data.hide_severity);
        const rawSeverity = Number.isFinite(data.original_node_color) ? data.original_node_color : data.node_color;
        const nodeColorSet = Array.isArray(allNodeColors) ? new Set(allNodeColors) : new Set();
        const uniqueValues = [...nodeColorSet];
        const isBinary =
            uniqueValues.length === 1 &&
            ["0", "1", "100"].includes(String(Math.round(Number(uniqueValues[0]))));
        const severityValue =
            !shouldHideSeverity && !isBinary && Number.isFinite(rawSeverity) ? Math.round(rawSeverity) : null;
        const severityText = severityValue !== null ? ` (Severity: ${severityValue})` : "";

        const phenotypesHtml = formatPhenotypesWithHighlight(phenotypes, target_phenotype);
        const phenotypeSection = `<div class="cy-tooltip__section cy-tooltip__section--phenotypes" data-section="phenotypes"><div class="cy-tooltip__section-title"><b>Phenotypes of <a href="${url_impc}" target="_blank">${data.id} KO mice</a>${severityText}</b></div><div class="cy-tooltip__section-body">${phenotypesHtml}</div></div>`;

        let diseaseSection = "";
        if (diseases && diseases.length > 0 && diseases[0] !== "") {
            const diseasesHtml = diseases.map((disease) => "・ " + disease).join("<br>");
            diseaseSection = `<div class="cy-tooltip__section cy-tooltip__section--diseases" data-section="diseases"><div class="cy-tooltip__section-title"><b>Associated Human Diseases</b></div><div class="cy-tooltip__section-body">${diseasesHtml}</div></div>`;
        }

        tooltipText = `${phenotypeSection}${diseaseSection}`;
        pos = event.target.renderedPosition();
    } else if (event.target.isEdge()) {
        const sourceNode = cy.getElementById(data.source).data("label");
        const targetNode = cy.getElementById(data.target).data("label");
        const hasSimilarityValue = Number.isFinite(data.edge_size);
        const similarityText = hasSimilarityValue ? ` (Similarity: ${Math.round(data.edge_size)})` : "";
        tooltipText = `<div><b>Shared phenotypes of ${sourceNode} and ${targetNode} KOs${similarityText}</b><br>`;
        tooltipText += formatPhenotypesWithHighlight(phenotypes, target_phenotype);
        tooltipText += "</div>";

        const sourcePos = cy.getElementById(data.source).renderedPosition();
        const targetPos = cy.getElementById(data.target).renderedPosition();
        pos = {
            x: (sourcePos.x + targetPos.x) / 2,
            y: (sourcePos.y + targetPos.y) / 2,
        };
    }

    return { tooltipText, pos };
}

function enableTooltipDrag(tooltip, containerElement = null) {
    let isDragging = false;
    let offset = { x: 0, y: 0 };
    const container = containerElement || tooltip.parentElement || document.querySelector(".cy");
    if (!container) return;

    // Mouse events (existing functionality)
    tooltip.addEventListener("mousedown", function (e) {
        if (e.target.closest(".cy-tooltip__resize-handle")) return;
        e.stopPropagation();
        isDragging = true;
        const rect = tooltip.getBoundingClientRect();
        offset.x = e.clientX - rect.left;
        offset.y = e.clientY - rect.top;
        tooltip.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", function (e) {
        if (isDragging) {
            const containerRect = container.getBoundingClientRect();
            tooltip.style.left = `${e.clientX - offset.x - containerRect.left}px`;
            tooltip.style.top = `${e.clientY - offset.y - containerRect.top}px`;
        }
    });

    document.addEventListener("mouseup", function () {
        isDragging = false;
        tooltip.style.cursor = "move";
    });

    // Touch events for tablet/mobile support
    tooltip.addEventListener("touchstart", function (e) {
        if (e.target.closest(".cy-tooltip__resize-handle")) return;
        e.stopPropagation();
        e.preventDefault();
        isDragging = true;
        const touch = e.touches[0];
        const rect = tooltip.getBoundingClientRect();
        offset.x = touch.clientX - rect.left;
        offset.y = touch.clientY - rect.top;
        tooltip.style.cursor = "grabbing";
    });

    document.addEventListener("touchmove", function (e) {
        if (isDragging) {
            e.preventDefault();
            const touch = e.touches[0];
            const containerRect = container.getBoundingClientRect();
            tooltip.style.left = `${touch.clientX - offset.x - containerRect.left}px`;
            tooltip.style.top = `${touch.clientY - offset.y - containerRect.top}px`;
        }
    });

    document.addEventListener("touchend", function () {
        isDragging = false;
        tooltip.style.cursor = "move";
    });
}

function updateTooltipSectionHeights(tooltip, tooltipHeight = DEFAULT_TOOLTIP_HEIGHT) {
    const safeHeight = Math.max(MIN_TOOLTIP_HEIGHT, tooltipHeight);
    const sections = Array.from(tooltip.querySelectorAll(".cy-tooltip__section"));
    if (sections.length === 0) return;

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
            const deltaX = startX - moveEvent.clientX; // dragging left increases width
            const deltaY = moveEvent.clientY - startY; // dragging down increases height

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
    let previousZoomEnabled;
    let previousPanEnabled;
    const restoreCyInteractions = () => {
        if (!cyInstance) return;
        if (typeof previousZoomEnabled === "boolean") {
            cyInstance.userZoomingEnabled(previousZoomEnabled);
        }
        if (typeof previousPanEnabled === "boolean") {
            cyInstance.userPanningEnabled(previousPanEnabled);
        }
    };

    const stopScrollPropagation = (event) => {
        event.stopPropagation();
    };

    // Capture-phase listeners ensure Cytoscape does not see wheel/touch events
    tooltip.addEventListener("wheel", stopScrollPropagation, { passive: true, capture: true });
    tooltip.addEventListener("mousewheel", stopScrollPropagation, { passive: true, capture: true });
    tooltip.addEventListener("touchstart", stopScrollPropagation, { passive: true, capture: true });
    tooltip.addEventListener("touchmove", stopScrollPropagation, { passive: true, capture: true });

    // Temporarily disable Cytoscape zoom/pan while hovering the tooltip
    tooltip.addEventListener(
        "mouseenter",
        () => {
            if (!cyInstance) return;
            previousZoomEnabled = cyInstance.userZoomingEnabled();
            previousPanEnabled = cyInstance.userPanningEnabled();
            cyInstance.userZoomingEnabled(false);
            cyInstance.userPanningEnabled(false);
        },
        { capture: true },
    );

    tooltip.addEventListener(
        "mouseleave",
        restoreCyInteractions,
        { capture: true },
    );

    // Allow cleanup if the tooltip is removed programmatically while hovered
    tooltip.__restoreCyInteractions = restoreCyInteractions;
}

function addCopyButtonToTooltip(tooltip) {
    const copyBtnWrapper = document.createElement("div");
    Object.assign(copyBtnWrapper.style, {
        position: "absolute",
        right: "6px", // Align with padding/resize handle
        bottom: "6px", // Align with padding/resize handle
        zIndex: "1001", // Ensure it's above other tooltip content
    });

    copyBtnWrapper.innerHTML =
        '<button class="cy-tooltip__copy-btn" title="Copy to clipboard" style="background:none; border:none; cursor:pointer; color:#888; padding: 2px 5px;"><i class="fa-regular fa-copy"></i></button>';
    tooltip.appendChild(copyBtnWrapper);

    const btn = copyBtnWrapper.querySelector("button");
    btn.addEventListener("mousedown", (e) => e.stopPropagation());
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const clone = tooltip.cloneNode(true);
        const btnInClone = clone.querySelector(".cy-tooltip__copy-btn");
        if (btnInClone && btnInClone.parentElement) {
            btnInClone.parentElement.remove();
        }

        let extractedHtml = clone.innerHTML;

        // <br>タグを改行文字に置換
        extractedHtml = extractedHtml.replace(/<br\s*\/?>/gi, '\n');
        
        // divの閉じタグの後に改行を追加してブロック要素間の改行を確保
        extractedHtml = extractedHtml.replace(/<\/div>/gi, '</div>\n');

        // 一時的なDOM要素を作成し、innerHTMLを設定してtextContentを取得する
        const tempElement = document.createElement('div');
        tempElement.innerHTML = extractedHtml;
        let text = tempElement.textContent || tempElement.innerText || "";
        
        // 連続する改行を1つにまとめる
        text = text.replace(/\n\s*\n/g, '\n').trim();


        if (navigator.clipboard) {
            navigator.clipboard
                .writeText(text)
                .then(() => {
                    btn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => (btn.innerHTML = '<i class="fa-regular fa-copy"></i>'), 2000);
                })
                .catch((err) => {
                    console.error("Failed to copy:", err);
                    alert("Failed to copy to clipboard");
                });
        } else {
            alert("Clipboard API not available");
        }
    });
}

/*
    Accepts target_phenotype and passes it to createTooltip
*/
export function showTooltip(
    event,
    cy,
    map_symbol_to_id,
    target_phenotype = null,
    nodeColorMin,
    nodeColorMax,
    nodeSizes,
) {
    removeTooltips();

    const { tooltipText, pos } = createTooltip(event, cy, map_symbol_to_id, target_phenotype, {
        nodeColorMin,
        nodeColorMax,
        allNodeColors: nodeSizes,
    });

    const tooltip = document.createElement("div");
    tooltip.classList.add("cy-tooltip");
    tooltip.innerHTML = tooltipText;
    Object.assign(tooltip.style, {
        position: "absolute",
        left: `${pos.x + 10}px`,
        top: `${pos.y + 10}px`,
        padding: "10px",
        paddingBottom: "18px",
        paddingLeft: "14px",
        background: "white",
        border: "1px solid #ccc",
        borderRadius: "5px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
        zIndex: "1000",
        cursor: "move",
        userSelect: "text",
        overflow: "hidden",
        overscrollBehavior: "contain",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        minWidth: `${MIN_TOOLTIP_WIDTH}px`,
        minHeight: `${MIN_TOOLTIP_HEIGHT}px`,
        boxSizing: "border-box",
    });

    const container = document.querySelector(".cy");
    if (!container) {
        console.warn("Cytoscape container not found; tooltip not rendered.");
        return;
    }

    container.appendChild(tooltip);
    applyInitialTooltipSize(tooltip);
    addCopyButtonToTooltip(tooltip);
    enableTooltipDrag(tooltip, container);
    enableTooltipResize(tooltip, container);
    isolateTooltipScroll(tooltip, cy);
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
 * Creates a reusable custom tooltip. Position is given in rendered coordinates relative to the Cytoscape container.
 */
export function showCustomTooltip({ content, position, containerSelector = ".cy", cyInstance = null }) {
    removeTooltips();

    const tooltip = document.createElement("div");
    tooltip.classList.add("cy-tooltip");
    tooltip.innerHTML = content;
    Object.assign(tooltip.style, {
        position: "absolute",
        left: `${position.x + 10}px`,
        top: `${position.y + 10}px`,
        padding: "10px",
        paddingBottom: "18px",
        paddingLeft: "14px",
        background: "white",
        border: "1px solid #ccc",
        borderRadius: "5px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
        zIndex: "1000",
        cursor: "move",
        userSelect: "text",
        overflow: "hidden",
        overscrollBehavior: "contain",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        minWidth: `${MIN_TOOLTIP_WIDTH}px`,
        minHeight: `${MIN_TOOLTIP_HEIGHT}px`,
        boxSizing: "border-box",
    });

    const container = document.querySelector(containerSelector);
    if (!container) {
        console.warn(`Container "${containerSelector}" not found; tooltip not rendered.`);
        return;
    }

    container.appendChild(tooltip);
    applyInitialTooltipSize(tooltip);
    addCopyButtonToTooltip(tooltip);
    enableTooltipDrag(tooltip, container);
    enableTooltipResize(tooltip, container);
    isolateTooltipScroll(tooltip, cyInstance);
}

/**
 * Shared tooltip for modules (connected components)
 */
export function showSubnetworkTooltip({ component, renderedPos, containerSelector = ".cy", cyInstance = null }) {
    if (!component) return;

    const lines =
        component.phenotypes && component.phenotypes.length > 0
            ? component.phenotypes.map(([name, count]) => `・ ${name} (${count})`)
            : ["No shared phenotypes on visible edges."];

    const infoIcon = `<div class="info-tooltip-container"><div class="info-tooltip-icon" aria-label="Tooltip: shared phenotype counts">i</div><div class="info-tooltip-content">The number in parentheses indicates the count of shared phenotypes within the module.</div></div>`;

    const header = `<div style="display: flex; align-items: center; gap: 6px;"><b>Phenotypes shared in Module ${component.id}</b>${infoIcon}</div>`;
    const linesHtml = lines.join("<br>");
    const bodySection = `<div class="cy-tooltip__section cy-tooltip__section--modules" data-section="modules"><div class="cy-tooltip__section-body">${linesHtml}</div></div>`;
    const tooltipContent = `${header}${bodySection}`;
    const anchor =
        renderedPos ||
        {
            x: (component.bbox.x1 + component.bbox.x2) / 2,
            y: (component.bbox.y1 + component.bbox.y2) / 2,
        };

    showCustomTooltip({ content: tooltipContent, position: anchor, containerSelector, cyInstance });

    // Enable click-to-toggle for dynamically created info icons (for touch devices)
    const tooltipEl = document.querySelector(".cy-tooltip");
    if (tooltipEl) {
        const tooltipIcons = tooltipEl.querySelectorAll(".info-tooltip-icon");
        tooltipIcons.forEach((icon) => {
            icon.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();

                const container = this.parentElement;
                container.classList.toggle("active");

                tooltipEl.querySelectorAll(".info-tooltip-container.active").forEach((el) => {
                    if (el !== container) {
                        el.classList.remove("active");
                    }
                });
            });
        });
    }
}

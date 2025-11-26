// ############################################################
// Tooltip Handling Functions
// ############################################################

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
        tooltipText = `<b>Phenotypes of <a href="${url_impc}" target="_blank">${data.id} KO mice</a>${severityText}</b><br>`;
        tooltipText += formatPhenotypesWithHighlight(phenotypes, target_phenotype);
        // Append the associated human diseases section when data is available
        if (diseases && diseases.length > 0 && diseases[0] !== "") {
            tooltipText += `<br><br><b>Associated Human Diseases</b><br>`;
            tooltipText += diseases.map((disease) => "・ " + disease).join("<br>");
        }
        pos = event.target.renderedPosition();
    } else if (event.target.isEdge()) {
        const sourceNode = cy.getElementById(data.source).data("label");
        const targetNode = cy.getElementById(data.target).data("label");
        const hasSimilarityValue = Number.isFinite(data.edge_size);
        const similarityText = hasSimilarityValue ? ` (Similarity: ${Math.round(data.edge_size)})` : "";
        tooltipText = `<b>Shared phenotypes of ${sourceNode} and ${targetNode} KOs${similarityText}</b><br>`;
        tooltipText += formatPhenotypesWithHighlight(phenotypes, target_phenotype);

        const sourcePos = cy.getElementById(data.source).renderedPosition();
        const targetPos = cy.getElementById(data.target).renderedPosition();
        pos = {
            x: (sourcePos.x + targetPos.x) / 2,
            y: (sourcePos.y + targetPos.y) / 2,
        };
    }

    return { tooltipText, pos };
}

function enableTooltipDrag(tooltip) {
    let isDragging = false;
    let offset = { x: 0, y: 0 };

    // Mouse events (existing functionality)
    tooltip.addEventListener("mousedown", function (e) {
        e.stopPropagation();
        isDragging = true;
        const rect = tooltip.getBoundingClientRect();
        offset.x = e.clientX - rect.left;
        offset.y = e.clientY - rect.top;
        tooltip.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", function (e) {
        if (isDragging) {
            const containerRect = document.querySelector(".cy").getBoundingClientRect();
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
            const containerRect = document.querySelector(".cy").getBoundingClientRect();
            tooltip.style.left = `${touch.clientX - offset.x - containerRect.left}px`;
            tooltip.style.top = `${touch.clientY - offset.y - containerRect.top}px`;
        }
    });

    document.addEventListener("touchend", function () {
        isDragging = false;
        tooltip.style.cursor = "move";
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
        padding: "5px",
        background: "white",
        border: "1px solid #ccc",
        borderRadius: "5px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
        zIndex: "1000",
        cursor: "move",
        userSelect: "text",
    });

    document.querySelector(".cy").appendChild(tooltip);
    enableTooltipDrag(tooltip);
}

export function removeTooltips() {
    document.querySelectorAll(".cy-tooltip").forEach((el) => el.remove());
}

/**
 * Creates a reusable custom tooltip. Position is given in rendered coordinates relative to the Cytoscape container.
 */
export function showCustomTooltip({ content, position, containerSelector = ".cy" }) {
    removeTooltips();

    const tooltip = document.createElement("div");
    tooltip.classList.add("cy-tooltip");
    tooltip.innerHTML = content;
    Object.assign(tooltip.style, {
        position: "absolute",
        left: `${position.x + 10}px`,
        top: `${position.y + 10}px`,
        padding: "5px",
        background: "white",
        border: "1px solid #ccc",
        borderRadius: "5px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
        zIndex: "1000",
        cursor: "move",
        userSelect: "text",
        maxWidth: "320px",
    });

    const container = document.querySelector(containerSelector);
    if (!container) {
        console.warn(`Container "${containerSelector}" not found; tooltip not rendered.`);
        return;
    }

    container.appendChild(tooltip);
    enableTooltipDrag(tooltip);
}

/**
 * Shared tooltip for modules (connected components)
 */
export function showSubnetworkTooltip({ component, renderedPos, containerSelector = ".cy" }) {
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

    const header = `<div style="display: flex; align-items: center; gap: 6px;"><b>Phenotypes shared in Module ${component.id}</b>${infoIcon}</div>`;
    const tooltipContent = `${header}${lines.join("<br>")}`;
    const anchor =
        renderedPos ||
        {
            x: (component.bbox.x1 + component.bbox.x2) / 2,
            y: (component.bbox.y1 + component.bbox.y2) / 2,
        };

    showCustomTooltip({ content: tooltipContent, position: anchor, containerSelector });

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

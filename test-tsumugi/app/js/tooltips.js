// ############################################################
// Tooltip Handling Functions
// ############################################################

export function removeTooltips() {
    document.querySelectorAll(".cy-tooltip").forEach((el) => el.remove());
}

function createTooltip(event, cy, map_symbol_to_id, target_phenotype = null) {
    const data = event.target.data();
    let tooltipText = "";
    let pos;

    if (event.target.isNode()) {
        const annotations = Array.isArray(data.annotation) ? data.annotation : [data.annotation];

        const geneID = map_symbol_to_id[data.label] || "UNKNOWN";
        const url_impc = `https://www.mousephenotype.org/data/genes/${geneID}`;

        tooltipText = `<b>Phenotypes of <a href="${url_impc}" target="_blank">${data.label} KO mice</a></b><br>`;

        const annotationLines = annotations.map((anno) => {
            if (target_phenotype && anno.includes(target_phenotype)) {
                return `・ <span style="font-weight: bold; color: #333;">🚩 ${anno}</span>`;
            } else {
                return "・ " + anno;
            }
        }).join("<br>");

        tooltipText += annotationLines;
        pos = event.target.renderedPosition();
    } else if (event.target.isEdge()) {
        const sourceNode = cy.getElementById(data.source).data("label");
        const targetNode = cy.getElementById(data.target).data("label");
        const annotations = Array.isArray(data.annotation) ? data.annotation : [data.annotation];

        tooltipText = `<b>Shared phenotypes of ${sourceNode} and ${targetNode} KOs</b><br>`;

        const annotationLines = annotations.map((anno) => {
            if (target_phenotype && anno.includes(target_phenotype)) {
                return `・ <span style="font-weight: bold; color: #333;">🚩 ${anno}</span>`;
            } else {
                return "・ " + anno;
            }
        }).join("<br>");

        tooltipText += annotationLines;

        const sourcePos = cy.getElementById(data.source).renderedPosition();
        const targetPos = cy.getElementById(data.target).renderedPosition();
        pos = {
            x: (sourcePos.x + targetPos.x) / 2,
            y: (sourcePos.y + targetPos.y) / 2,
        };
    }

    return { tooltipText, pos };
}


// Accepts target_phenotype and passes it to createTooltip
export function showTooltip(event, cy, map_symbol_to_id, target_phenotype = null) {
    removeTooltips();

    const { tooltipText, pos } = createTooltip(event, cy, map_symbol_to_id, target_phenotype);

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

function enableTooltipDrag(tooltip) {
    let isDragging = false;
    let offset = { x: 0, y: 0 };

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
}

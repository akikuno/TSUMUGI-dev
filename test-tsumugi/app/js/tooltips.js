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
                return `🚩 ${phenotype}`;
            } else {
                return "・ " + phenotype;
            }
        })
        .join("<br>");
}

function createTooltip(event, cy, map_symbol_to_id, target_phenotype = null) {
    const data = event.target.data();
    let tooltipText = "";
    let pos;

    const phenotypes = Array.isArray(data.phenotype) ? data.phenotype : [data.phenotype];
    const diseases = Array.isArray(data.disease) ? data.disease : [data.disease];

    if (event.target.isNode()) {
        const geneID = map_symbol_to_id[data.id] || "UNKNOWN";
        const url_impc = `https://www.mousephenotype.org/data/genes/${geneID}`;
        tooltipText = `<b>Phenotypes of <a href="${url_impc}" target="_blank">${data.id} KO mice</a></b><br>`;
        tooltipText += formatPhenotypesWithHighlight(phenotypes, target_phenotype);
        // もしdiseasesが""出ない場合は、Associated Human Diseasesを追加
        if (diseases && diseases.length > 0 && diseases[0] !== "") {
            tooltipText += `<br><br><b>Associated Human Diseases</b><br>`;
            tooltipText += diseases.map((disease) => "・ " + disease).join("<br>");
        }
        pos = event.target.renderedPosition();
    } else if (event.target.isEdge()) {
        const sourceNode = cy.getElementById(data.source).data("label");
        const targetNode = cy.getElementById(data.target).data("label");
        tooltipText = `<b>Shared phenotypes of ${sourceNode} and ${targetNode} KOs</b><br>`;
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

/*
    Accepts target_phenotype and passes it to createTooltip
*/
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

export function removeTooltips() {
    document.querySelectorAll(".cy-tooltip").forEach((el) => el.remove());
}

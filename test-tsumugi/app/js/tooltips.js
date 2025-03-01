// ############################################################
// Tooltip Handling Functions
// ############################################################

// Function to remove all existing tooltips
export function removeTooltips() {
    document.querySelectorAll('.cy-tooltip').forEach(el => el.remove());
}

// Function to create tooltip content for nodes and edges
function createTooltip(event, cy, map_symbol_to_id) {
    const data = event.target.data();
    let tooltipText = '';
    let pos;

    if (event.target.isNode()) {
        const annotations = Array.isArray(data.annotation)
            ? data.annotation.map(anno => '・ ' + anno).join('<br>')
            : '・ ' + data.annotation;

        const geneID = map_symbol_to_id[data.label] || "UNKNOWN"; // undefined の場合に備える
        const url_impc = `https://www.mousephenotype.org/data/genes/${geneID}`;
        tooltipText = `<b>Phenotypes of <a href="${url_impc}" target="_blank">${data.label} KO mice</a></b><br>` + annotations;

        pos = event.target.renderedPosition();
    } else if (event.target.isEdge()) {
        const sourceNode = cy.getElementById(data.source).data('label');
        const targetNode = cy.getElementById(data.target).data('label');
        const annotations = Array.isArray(data.annotation)
            ? data.annotation.map(anno => '・ ' + anno).join('<br>')
            : '・ ' + data.annotation;

        tooltipText = `<b>Shared phenotypes of ${sourceNode} and ${targetNode} KOs</b><br>` + annotations;

        const sourcePos = cy.getElementById(data.source).renderedPosition();
        const targetPos = cy.getElementById(data.target).renderedPosition();
        pos = { x: (sourcePos.x + targetPos.x) / 2, y: (sourcePos.y + targetPos.y) / 2 };
    }

    return { tooltipText, pos };
}

// Function to show tooltip
export function showTooltip(event, cy, map_symbol_to_id) {
    removeTooltips(); // Remove existing tooltips

    const { tooltipText, pos } = createTooltip(event, cy, map_symbol_to_id);

    const tooltip = document.createElement('div');
    tooltip.classList.add('cy-tooltip');
    tooltip.innerHTML = tooltipText;
    Object.assign(tooltip.style, {
        position: 'absolute',
        left: `${pos.x + 10}px`,
        top: `${pos.y + 10}px`,
        padding: '5px',
        background: 'white',
        border: '1px solid #ccc',
        borderRadius: '5px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        zIndex: '1000',
        cursor: 'move',
        userSelect: 'text'
    });

    document.querySelector('.cy').appendChild(tooltip);
    enableTooltipDrag(tooltip);
}

// Function to enable dragging for tooltips
function enableTooltipDrag(tooltip) {
    let isDragging = false;
    let offset = { x: 0, y: 0 };

    tooltip.addEventListener('mousedown', function (e) {
        e.stopPropagation();
        isDragging = true;
        const rect = tooltip.getBoundingClientRect();
        offset.x = e.clientX - rect.left;
        offset.y = e.clientY - rect.top;
        tooltip.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', function (e) {
        if (isDragging) {
            const containerRect = document.querySelector('.cy').getBoundingClientRect();
            tooltip.style.left = `${e.clientX - offset.x - containerRect.left}px`;
            tooltip.style.top = `${e.clientY - offset.y - containerRect.top}px`;
        }
    });

    document.addEventListener('mouseup', function () {
        isDragging = false;
        tooltip.style.cursor = 'move';
    });
}

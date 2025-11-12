// Initialization of the Node color slider
const NODE_SLIDER_MIN = 1;
const NODE_SLIDER_MAX = 100;
const nodeSlider = document.getElementById("filter-node-slider");

if (nodeSlider) {
    noUiSlider.create(nodeSlider, {
        start: [NODE_SLIDER_MIN, NODE_SLIDER_MAX],
        connect: true,
        range: { min: NODE_SLIDER_MIN, max: NODE_SLIDER_MAX },
        step: 1,
    });
}

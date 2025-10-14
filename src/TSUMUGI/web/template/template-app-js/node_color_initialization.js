// Initialization of the Node color slider
const nodeSlider = document.getElementById("filter-node-slider");
noUiSlider.create(nodeSlider, { start: [1, 100], connect: true, range: { min: 1, max: 100 }, step: 1 });

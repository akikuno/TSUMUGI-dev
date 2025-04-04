// Initialization of the Node color slider
const nodeSlider = document.getElementById("filter-node-slider");
noUiSlider.create(nodeSlider, { start: [1, 10], connect: true, range: { min: 1, max: 10 }, step: 1 });

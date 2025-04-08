// Update the slider values when the sliders are moved
nodeSlider.noUiSlider.on("update", function (values) {
    const intValues = values.map((value) => Math.round(value));
    document.getElementById("node-color-value").textContent = intValues.join(" - ");
    filterByNodeColorAndEdgeSize();
});



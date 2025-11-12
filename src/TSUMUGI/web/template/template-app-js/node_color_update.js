// Update the slider values when the sliders are moved
if (nodeSlider && nodeSlider.noUiSlider) {
    nodeSlider.noUiSlider.on("update", function (values) {
        const intValues = values.map((value) => Math.round(value));
        const label = document.getElementById("node-color-value");
        if (label) {
            label.textContent = intValues.join(" - ");
        }
        filterByNodeColorAndEdgeSize();
    });
}


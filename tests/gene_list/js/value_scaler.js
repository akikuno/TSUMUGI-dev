export function scaleToOriginalRange(value, minValue, maxValue) {
    // Scales a value from the range [1, 10] to a new range [minValue, maxValue].
    return minValue + ((value - 1) * (maxValue - minValue)) / 9;
}

export function scaleValue(value, minValue, maxValue, minScale, maxScale) {
    // Convert the scale to the range between minScale and maxScale
    if (minValue == maxValue) {
        return (maxScale + minScale) / 2;
    }
    return minScale + ((value - minValue) * (maxScale - minScale)) / (maxValue - minValue);
}

export function getColorForValue(value) {
    // Map value from the 1-10 range to a 0-1 range
    const ratio = (value - 1) / (10 - 1);

    // Gradient from Light Yellow to Orange
    const r1 = 248,
        g1 = 229,
        b1 = 140; // Light Yellow
    const r2 = 255,
        g2 = 140,
        b2 = 0; // Orange

    const r = Math.round(r1 + (r2 - r1) * ratio);
    const g = Math.round(g1 + (g2 - g1) * ratio);
    const b = Math.round(b1 + (b2 - b1) * ratio);

    return `rgb(${r}, ${g}, ${b})`;
}

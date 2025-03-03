
export function scaleToOriginalRange(value, minValue, maxValue) {
    // Scales a value from the range [1, 10] to a new range [minValue, maxValue].
    return minValue + (value - 1) * (maxValue - minValue) / 9;
}

export function scaleValue(value, minValue, maxValue, minScale, maxScale) {
    // スケールをminScaleとmaxScaleの範囲に変換
    if (minValue == maxValue) {
        return (maxScale + minScale) / 2;
    }
    return minScale + (value - minValue) * (maxScale - minScale) / (maxValue - minValue);
}

export function getColorForValue(value) {
    // value を1-10の範囲から0-1の範囲に変換
    const ratio = (value - 1) / (10 - 1);

    // Light Yellow から Orange へのグラデーション
    const r1 = 248, g1 = 229, b1 = 140; // Light Yellow
    const r2 = 255, g2 = 140, b2 = 0;   // Orange

    const r = Math.round(r1 + (r2 - r1) * ratio);
    const g = Math.round(g1 + (g2 - g1) * ratio);
    const b = Math.round(b1 + (b2 - b1) * ratio);

    return `rgb(${r}, ${g}, ${b})`;
}

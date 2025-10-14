export function scaleToOriginalRange(value, minValue, maxValue, scaleMin = 1, scaleMax = 10) {
    // Scales a value from the range [scaleMin, scaleMax] to a new range [minValue, maxValue].
    if (maxValue === minValue) {
        return minValue;
    }

    const denominator = scaleMax - scaleMin;
    if (denominator === 0) {
        return minValue;
    }

    const clampedValue = Math.min(Math.max(value, scaleMin), scaleMax);
    return minValue + ((clampedValue - scaleMin) * (maxValue - minValue)) / denominator;
}

export function scaleValue(value, minValue, maxValue, minScale, maxScale) {
    // スケールをminScaleとmaxScaleの範囲に変換
    if (minValue == maxValue) {
        return (maxScale + minScale) / 2;
    }
    return minScale + ((value - minValue) * (maxScale - minScale)) / (maxValue - minValue);
}

export function getColorForValue(value, scaleMin = 1, scaleMax = 10) {
    // value をscaleMin-scaleMaxの範囲から0-1の範囲に変換
    const denominator = scaleMax - scaleMin;
    const clampedValue = Math.min(Math.max(value, scaleMin), scaleMax);
    const ratio = denominator === 0 ? 0 : (clampedValue - scaleMin) / denominator;

    // Light Yellow から Orange へのグラデーション
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

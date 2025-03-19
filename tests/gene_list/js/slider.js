// 汎用スライダー作成関数（単一値 & 範囲スライダーに対応）
export function createSlider(id, start, min, max, step, updateCallback, isRange = false) {
    const slider = document.getElementById(id);
    if (!slider) {
        console.error(`Slider with ID '${id}' not found.`);
        return;
    }

    noUiSlider.create(slider, {
        start: isRange ? start : [start], // isRangeなら[start, end]、単一なら[start]
        connect: true,
        range: { min: min, max: max },
        step: step,
    });

    slider.noUiSlider.on("update", function (value) {
        const intValues = isRange ? value.map(Math.round) : Math.round(value);
        updateCallback(intValues);
    });
}

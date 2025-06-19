export function initDynamicFontSize() {
    function adjustHeaderFontSize() {
        const header = document.querySelector(".header-container h1");
        if (!header) return;

        const containerWidth = header.parentElement.offsetWidth;
        const viewportWidth = window.innerWidth;

        // ビューポート幅に基づく基本サイズ
        let baseFontSize = viewportWidth * 0.04; // 4vw

        // 最小・最大値で制限
        baseFontSize = Math.max(14, Math.min(36, baseFontSize));

        // スマホの場合はさらに調整
        if (viewportWidth <= 600) {
            baseFontSize = Math.min(baseFontSize, viewportWidth * 0.045);
        }

        header.style.fontSize = baseFontSize + "px";
    }

    // 初期実行
    adjustHeaderFontSize();

    // リサイズ時の実行（デバウンス付き）
    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(adjustHeaderFontSize, 100);
    });
}

// 自動実行
document.addEventListener("DOMContentLoaded", initDynamicFontSize);

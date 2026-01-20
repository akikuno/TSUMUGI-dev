// ============================================================
// Dynamic header font sizing
// ============================================================

export function initDynamicFontSize() {
    const adjustHeaderFontSize = () => {
        const header = document.querySelector(".header-container h1");
        if (!header) return;

        const viewportWidth = window.innerWidth;

        // Base font size derived from viewport width.
        let baseFontSize = viewportWidth * 0.04;
        baseFontSize = Math.max(14, Math.min(36, baseFontSize));

        if (viewportWidth <= 600) {
            baseFontSize = Math.min(baseFontSize, viewportWidth * 0.045);
        }

        header.style.fontSize = `${baseFontSize}px`;
    };

    adjustHeaderFontSize();

    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(adjustHeaderFontSize, 100);
    });
}

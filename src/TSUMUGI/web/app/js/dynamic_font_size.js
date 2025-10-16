export function initDynamicFontSize() {
    function adjustHeaderFontSize() {
        const header = document.querySelector(".header-container h1");
        if (!header) return;

        const containerWidth = header.parentElement.offsetWidth;
        const viewportWidth = window.innerWidth;

        // Base font size derived from viewport width
        let baseFontSize = viewportWidth * 0.04; // 4vw

        // Clamp to reasonable min/max values
        baseFontSize = Math.max(14, Math.min(36, baseFontSize));

        // Apply additional scaling for small screens
        if (viewportWidth <= 600) {
            baseFontSize = Math.min(baseFontSize, viewportWidth * 0.045);
        }

        header.style.fontSize = baseFontSize + "px";
    }

    // Run once on initialization
    adjustHeaderFontSize();

    // Recalculate on resize (with debouncing)
    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(adjustHeaderFontSize, 100);
    });
}

// Auto-run when the DOM is ready
document.addEventListener("DOMContentLoaded", initDynamicFontSize);

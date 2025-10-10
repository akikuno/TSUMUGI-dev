// ============================================================
// Info Tooltip Functionality for Network Pages
// ============================================================

document.addEventListener("DOMContentLoaded", function () {
    // Handle tooltip click interactions for mobile devices
    const tooltipIcons = document.querySelectorAll(".info-tooltip-icon");

    tooltipIcons.forEach((icon) => {
        icon.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            const container = this.parentElement;
            container.classList.toggle("active");

            // Close other active tooltips
            document.querySelectorAll(".info-tooltip-container.active").forEach((el) => {
                if (el !== container) {
                    el.classList.remove("active");
                }
            });
        });
    });

    // Close tooltips when clicking outside
    document.addEventListener("click", function () {
        document.querySelectorAll(".info-tooltip-container.active").forEach((el) => {
            el.classList.remove("active");
        });
    });
});

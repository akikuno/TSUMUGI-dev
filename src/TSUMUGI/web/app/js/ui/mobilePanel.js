// ============================================================
// Mobile panel toggles for small screens
// ============================================================

export function initMobilePanel() {
    const menuToggle = document.getElementById("menu-toggle");
    const leftPanel = document.querySelector(".left-control-panel-container");
    const rightPanel = document.querySelector(".right-control-panel-container");
    const closeButton = document.getElementById("close-panel");

    if (!menuToggle || !leftPanel || !rightPanel || !closeButton) {
        return;
    }

    // On small screens move the right panel beneath the left panel.
    const reorganizePanels = () => {
        if (window.innerWidth <= 600) {
            if (rightPanel.parentNode !== leftPanel) {
                leftPanel.appendChild(rightPanel);
            }
        } else {
            const bodyContainer = document.querySelector(".body-container");
            if (rightPanel.parentNode === leftPanel && bodyContainer) {
                bodyContainer.appendChild(rightPanel);
            }
        }
    };

    reorganizePanels();
    window.addEventListener("resize", reorganizePanels);

    const openPanel = (event) => {
        event.stopPropagation();
        event.preventDefault();

        menuToggle.style.display = "none";
        leftPanel.classList.add("active");
        if (window.innerWidth <= 600) {
            rightPanel.classList.add("active");
        }
        closeButton.style.display = "block";
    };

    const closePanel = (event) => {
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        leftPanel.classList.remove("active");
        rightPanel.classList.remove("active");
        closeButton.style.display = "none";

        setTimeout(() => {
            menuToggle.style.display = "block";
        }, 50);
    };

    ["click", "touchstart"].forEach((eventName) => {
        menuToggle.addEventListener(eventName, openPanel);
    });

    ["click", "touchstart"].forEach((eventName) => {
        closeButton.addEventListener(eventName, closePanel);
    });

    document.addEventListener("click", (event) => {
        if (
            leftPanel.classList.contains("active") &&
            !leftPanel.contains(event.target) &&
            !menuToggle.contains(event.target) &&
            !closeButton.contains(event.target)
        ) {
            closePanel();
        }
    });
}

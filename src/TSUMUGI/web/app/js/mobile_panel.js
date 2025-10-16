// Initialize once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Look up the toggle icon, control panels, and close button
    const menuToggle = document.getElementById("menu-toggle");
    const leftPanel = document.querySelector(".left-control-panel-container");
    const rightPanel = document.querySelector(".right-control-panel-container");
    const closeButton = document.getElementById("close-panel");

    // Proceed only when all required elements are present
    if (menuToggle && leftPanel && rightPanel && closeButton) {
        // On small screens move the right panel beneath the left panel
        const reorganizePanels = () => {
            if (window.innerWidth <= 600) {
                // Append the right panel to the left container
                if (rightPanel.parentNode !== leftPanel) {
                    leftPanel.appendChild(rightPanel);
                }
            } else {
                // Restore the desktop layout
                const bodyContainer = document.querySelector(".body-container");
                if (rightPanel.parentNode === leftPanel && bodyContainer) {
                    bodyContainer.appendChild(rightPanel);
                }
            }
        };

        // Handle the initial layout and respond to resizes
        reorganizePanels();
        window.addEventListener("resize", reorganizePanels);

        const openPanel = (event) => {
            event.stopPropagation();
            event.preventDefault(); // Prevent default behavior as well

            // Hide the menu toggle icon
            menuToggle.style.display = "none";

            // Reveal the panels
            leftPanel.classList.add("active");
            if (window.innerWidth <= 600) {
                rightPanel.classList.add("active");
            }

            // Show the close button
            closeButton.style.display = "block";
        };

        const closePanel = (event) => {
            if (event) {
                event.stopPropagation();
                event.preventDefault();
            }

            // Hide both panels
            leftPanel.classList.remove("active");
            rightPanel.classList.remove("active");

            // Hide the close button
            closeButton.style.display = "none";

            // Bring back the menu toggle (with a slight delay)
            setTimeout(() => {
                menuToggle.style.display = "block";
            }, 50);
        };

        // Support both click and touch events on the icon
        ["click", "touchstart"].forEach((evt) => {
            menuToggle.addEventListener(evt, openPanel);
        });

        // Apply the same handlers to the close button
        ["click", "touchstart"].forEach((evt) => {
            closeButton.addEventListener(evt, closePanel);
        });

        // Close the panel when clicking outside
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
});

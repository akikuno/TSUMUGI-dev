// DOMの読み込みが完了したら実行
document.addEventListener("DOMContentLoaded", () => {
    // アイコン、コントロールパネル、✕ボタンの要素を取得
    const menuToggle = document.getElementById("menu-toggle");
    const leftPanel = document.querySelector(".left-control-panel-container");
    const rightPanel = document.querySelector(".right-control-panel-container");
    const closeButton = document.getElementById("close-panel");

    // すべての要素が取得できている場合のみ処理を進める
    if (menuToggle && leftPanel && rightPanel && closeButton) {
        // スマホ表示時のみ右パネルを左パネルに移動
        const reorganizePanels = () => {
            if (window.innerWidth <= 600) {
                // 右パネルを左パネルの最後に追加
                if (rightPanel.parentNode !== leftPanel) {
                    leftPanel.appendChild(rightPanel);
                }
            } else {
                // デスクトップ表示に戻す
                const bodyContainer = document.querySelector(".body-container");
                if (rightPanel.parentNode === leftPanel && bodyContainer) {
                    bodyContainer.appendChild(rightPanel);
                }
            }
        };

        // 初期化とリサイズ時の処理
        reorganizePanels();
        window.addEventListener("resize", reorganizePanels);

        const openPanel = (event) => {
            event.stopPropagation();
            event.preventDefault(); // デフォルト動作も防ぐ

            // menu-toggleを完全に非表示
            menuToggle.style.display = "none";

            // パネルを表示
            leftPanel.classList.add("active");
            if (window.innerWidth <= 600) {
                rightPanel.classList.add("active");
            }

            // close-buttonを表示
            closeButton.style.display = "block";
        };

        const closePanel = (event) => {
            if (event) {
                event.stopPropagation();
                event.preventDefault();
            }

            // パネルを非表示
            leftPanel.classList.remove("active");
            rightPanel.classList.remove("active");

            // close-buttonを非表示
            closeButton.style.display = "none";

            // menu-toggleを再表示（少し遅延させる）
            setTimeout(() => {
                menuToggle.style.display = "block";
            }, 50);
        };

        // アイコンに click と touchstart の両方を登録
        ["click", "touchstart"].forEach((evt) => {
            menuToggle.addEventListener(evt, openPanel);
        });

        // ✕ボタンも同様に click と touchstart を登録
        ["click", "touchstart"].forEach((evt) => {
            closeButton.addEventListener(evt, closePanel);
        });

        // 外部クリックで閉じる（click のみでOK）
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

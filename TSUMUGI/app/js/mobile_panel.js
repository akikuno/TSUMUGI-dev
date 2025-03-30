// DOMの読み込みが完了したら実行
document.addEventListener("DOMContentLoaded", () => {
    // アイコン、コントロールパネル、✕ボタンの要素を取得
    const menuToggle = document.getElementById("menu-toggle");
    const controlPanel = document.querySelector(".control-panel-container");
    const closeButton = document.getElementById("close-panel");

    // すべての要素が取得できている場合のみ処理を進める
    if (menuToggle && controlPanel && closeButton) {
        const openPanel = (event) => {
            event.stopPropagation();
            controlPanel.classList.add("active");
            menuToggle.classList.add("hidden");
            closeButton.classList.add("active");
        };

        const closePanel = () => {
            controlPanel.classList.remove("active");
            menuToggle.classList.remove("hidden");
            closeButton.classList.remove("active");
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
                controlPanel.classList.contains("active") &&
                !controlPanel.contains(event.target) &&
                !menuToggle.contains(event.target) &&
                !closeButton.contains(event.target)
            ) {
                closePanel();
            }
        });
    }
});

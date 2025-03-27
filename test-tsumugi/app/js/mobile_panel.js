// DOMの読み込みが完了したら実行
document.addEventListener("DOMContentLoaded", () => {
    // アイコン、コントロールパネル、✕ボタンの要素を取得
    const menuToggle = document.getElementById("menu-toggle");
    const controlPanel = document.querySelector(".control-panel-container");
    const closeButton = document.getElementById("close-panel");

    // すべての要素が取得できている場合のみ処理を進める
    if (menuToggle && controlPanel && closeButton) {
        // アイコンをクリックしたときの処理
        menuToggle.addEventListener("click", (event) => {
            event.stopPropagation(); // イベントのバブリングを止める（外側のclickイベントが発火しないように）
            controlPanel.classList.add("active"); // パネルを表示
            menuToggle.classList.add("hidden"); // アイコンを非表示
            closeButton.classList.add("active"); // ✕ボタンを表示
        });

        // ✕ボタンをクリックしたときの処理
        closeButton.addEventListener("click", () => {
            controlPanel.classList.remove("active"); // パネルを閉じる
            menuToggle.classList.remove("hidden"); // アイコンを再表示
            closeButton.classList.remove("active"); // ✕ボタンを非表示
        });

        // 画面のどこかをクリックしたときの処理（外部クリックで閉じる）
        document.addEventListener("click", (event) => {
            if (
                controlPanel.classList.contains("active") && // パネルが開いていて
                !controlPanel.contains(event.target) && // パネル内ではなく
                !menuToggle.contains(event.target) && // アイコンでもなく
                !closeButton.contains(event.target) // ✕ボタンでもない場合
            ) {
                controlPanel.classList.remove("active"); // パネルを閉じる
                menuToggle.classList.remove("hidden"); // アイコンを再表示
                closeButton.classList.remove("active"); // ✕ボタンを非表示
            }
        });
    }
});

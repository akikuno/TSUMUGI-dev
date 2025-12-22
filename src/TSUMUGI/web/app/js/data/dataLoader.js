export function loadJSONGz(url) {
    const req = new XMLHttpRequest();
    let result = null;

    try {
        req.open("GET", url, false);
        req.overrideMimeType("text/plain; charset=x-user-defined"); // Treat the response as binary data
        req.send(null);

        if (req.status === 200) {
            const compressedData = new Uint8Array(req.responseText.split("").map((c) => c.charCodeAt(0) & 0xff));
            result = JSON.parse(window.pako.ungzip(compressedData, { to: "string" }));
        } else {
            console.error("HTTP error!! status:", req.status);
        }
    } catch (error) {
        console.error("Failed to load or decode JSON.gz:", error);
    }

    return result;
}

export function loadJSON(url) {
    const req = new XMLHttpRequest();
    let result = null;

    try {
        req.open("GET", url, false);
        req.send(null);

        if (req.status === 200) {
            result = JSON.parse(req.responseText);
        } else {
            console.error("HTTP error!! status:", req.status);
        }
    } catch (error) {
        console.error("Failed to load JSON:", error);
    }

    return result;
}

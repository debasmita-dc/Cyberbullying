function analyzeText() {
    const text = document.getElementById("bullyText").value;
    const button = document.getElementById("analyzeBtn");
    const loader = document.getElementById("loader");
    const resultCard = document.getElementById("resultCard");
    const alertBanner = document.getElementById("alertBanner");

    if (text.trim() === "") {
        alert("Please enter text");
        return;
    }

    button.disabled = true;
    loader.style.display = "block";
    resultCard.innerHTML = "";
    alertBanner.innerHTML = "";

    fetch("/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
    .then(res => res.json())
    .then(data => {
        resultCard.innerHTML = `
            <p><b>Result:</b> ${data.label}</p>
            <p><b>Confidence:</b> ${(data.confidence * 100).toFixed(2)}%</p>
            <p><b>Severity:</b> ${data.severity}</p>
        `;

        if (data.severity === "High") {
            alertBanner.innerHTML = "⚠ Severe Cyberbullying Detected. Immediate action required.";
            alertBanner.style.color = "red";
        }
    })
    .catch(() => {
        resultCard.innerHTML = "Error connecting to server.";
    })
    .finally(() => {
        loader.style.display = "none";
        button.disabled = false;
    });
}

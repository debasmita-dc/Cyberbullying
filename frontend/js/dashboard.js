fetch("/api/dashboard")
.then(res => res.json())
.then(data => {
    const ctx = document.getElementById("caseChart");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Low", "Medium", "High"],
            datasets: [{
                label: "Severity Distribution",
                data: [data.low, data.medium, data.high]
            }]
        }
    });
})
.catch(() => console.log("Dashboard API error"));

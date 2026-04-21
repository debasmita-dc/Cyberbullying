document.addEventListener("DOMContentLoaded", () => {
    fetchDashboardData();
});

function fetchDashboardData() {
    /*
      Backend will expose an API like:
      GET /api/dashboard
      {
        total: 25,
        detected: 18,
        resolved: 10,
        complaints: [
          { name: "Asha", platform: "Instagram", status: "Pending" },
          { name: "Rahul", platform: "Twitter", status: "Resolved" }
        ]
      }
    */

    fetch("/api/dashboard")
        .then(response => response.json())
        .then(data => {
            document.getElementById("totalComplaints").innerText = data.total;
            document.getElementById("detectedCases").innerText = data.detected;
            document.getElementById("resolvedCases").innerText = data.resolved;

            const tableBody = document.getElementById("complaintTable");
            tableBody.innerHTML = "";

            data.complaints.forEach(c => {
                const row = `
                    <tr>
                        <td>${c.name}</td>
                        <td>${c.platform}</td>
                        <td>${c.status}</td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
        })
        .catch(() => {
            document.getElementById("complaintTable").innerHTML =
                "<tr><td colspan='3'>Failed to load data</td></tr>";
        });
}

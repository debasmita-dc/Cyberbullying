document.addEventListener("DOMContentLoaded", async () => {
  const tableBody = document.getElementById("complaintTable");

  try {
    const res = await fetch("/api/dashboard", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    console.log("Dashboard data:", data);

    // ---- Cards ----
    animateCounter("totalComplaints", data.total ?? 0);
    animateCounter("detectedCases", data.detected ?? 0);
    animateCounter("resolvedCases", data.resolved ?? 0);

    const low = data.low ?? 0;
    const medium = data.medium ?? 0;
    const high = data.high ?? 0;

    // ---- Chart ----
    const canvas = document.getElementById("severityChart");
    const ctx = canvas.getContext("2d");

    if (window.__severityChart) window.__severityChart.destroy();

    window.__severityChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Low", "Medium", "High"],
        datasets: [{
          label: "Number of Cases",
          data: [low, medium, high],
          backgroundColor: [
            "rgba(6, 214, 160, 0.7)",
            "rgba(255, 209, 102, 0.7)",
            "rgba(230, 57, 70, 0.7)"
          ],
          borderColor: [
            "#06d6a0",
            "#ffd166",
            "#e63946"
          ],
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            labels: {
              color: "#9ca3af",
              font: { family: "'Inter', sans-serif", size: 13 },
              padding: 20,
              usePointStyle: true,
              pointStyleWidth: 12,
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: "#9ca3af",
              font: { family: "'Inter', sans-serif", size: 13, weight: 600 }
            },
            grid: { color: "rgba(255,255,255,0.04)" },
            border: { color: "rgba(255,255,255,0.06)" }
          },
          y: {
            beginAtZero: true,
            ticks: {
              color: "#9ca3af",
              font: { family: "'Inter', sans-serif", size: 12 },
              stepSize: 1
            },
            grid: { color: "rgba(255,255,255,0.04)" },
            border: { color: "rgba(255,255,255,0.06)" }
          }
        }
      }
    });

    // ---- Table ----
    const complaints = data.complaints ?? [];

    if (complaints.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:#6b7280;">
        <i class="fas fa-inbox" style="margin-right:8px; font-size:16px;"></i>No complaints yet
      </td></tr>`;
      return;
    }

    tableBody.innerHTML = complaints.map(c => {
      const severityClass = getSeverityClass(c.severity);
      return `
      <tr>
        <td style="font-weight:600; color:#f0f2f5;">${c.id ?? ""}</td>
        <td>${c.name ?? ""}</td>
        <td><span style="display:inline-flex; align-items:center; gap:6px;">${getPlatformIcon(c.platform)} ${c.platform ?? ""}</span></td>
        <td><span class="severity-badge ${severityClass}">${c.severity ?? ""}</span></td>
        <td>
          <select onchange="updateStatus(${c.id}, this.value)" style="min-width:110px;">
            <option value="Pending" ${c.status === "Pending" ? "selected" : ""}>⏳ Pending</option>
            <option value="Resolved" ${c.status === "Resolved" ? "selected" : ""}>✅ Resolved</option>
          </select>
        </td>
        <td style="font-size:13px; white-space:nowrap;">${c.created_at ?? ""}</td>
      </tr>`;
    }).join("");

  } catch (err) {
    console.error("Dashboard load error:", err);
    if (tableBody) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:#ff6b6b;">
        <i class="fas fa-exclamation-circle" style="margin-right:8px;"></i>Failed to load data
      </td></tr>`;
    }
  }
});

async function updateStatus(id, status) {
  await fetch(`/api/complaints/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });
  location.reload();
}

function getSeverityClass(severity) {
  switch ((severity || "").toLowerCase()) {
    case "critical": return "severity-critical";
    case "high": return "severity-high";
    case "moderate":
    case "medium": return "severity-moderate";
    case "low": return "severity-low";
    case "minimal": return "severity-minimal";
    default: return "";
  }
}

function getPlatformIcon(platform) {
  const icons = {
    instagram: '<i class="fab fa-instagram" style="color:#E1306C;"></i>',
    facebook: '<i class="fab fa-facebook" style="color:#1877F2;"></i>',
    twitter: '<i class="fab fa-x-twitter" style="color:#fff;"></i>',
    whatsapp: '<i class="fab fa-whatsapp" style="color:#25D366;"></i>',
    snapchat: '<i class="fab fa-snapchat" style="color:#FFFC00;"></i>',
    telegram: '<i class="fab fa-telegram" style="color:#0088cc;"></i>',
  };
  return icons[(platform || "").toLowerCase()] || '<i class="fas fa-globe" style="color:#9ca3af;"></i>';
}

function animateCounter(elementId, target) {
  const el = document.getElementById(elementId);
  if (!el) return;
  if (target === 0) { el.textContent = "0"; return; }

  let current = 0;
  const step = Math.max(1, Math.ceil(target / 30));
  const interval = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(interval);
    }
    el.textContent = current;
  }, 30);
}
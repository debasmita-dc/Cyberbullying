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
    body: JSON.stringify({ text })
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        resultCard.innerHTML = `<p style="color:var(--accent-light);"><i class="fas fa-exclamation-circle" style="margin-right:8px;"></i>${data.error}</p>`;
        return;
      }

      const lm = data.legal_mapping || null;
      const severityClass = getSeverityClass(data.severity);

      let legalHtml = "";
      if (lm && typeof lm === "object") {
        const sections = Array.isArray(lm.legal_sections) ? lm.legal_sections : [];
        const reasons = Array.isArray(lm.reasons) ? lm.reasons : [];
        const guidance = Array.isArray(lm.guidance) ? lm.guidance : [];

        legalHtml = `
          <div style="margin-top:20px; padding-top:20px; border-top:1px solid var(--border);">
            <p style="font-weight:700; font-size:16px; margin-bottom:10px;">
              <i class="fas fa-scale-balanced" style="color:var(--accent); margin-right:8px;"></i>Legal Sections
            </p>
            ${sections.length
              ? `<ul>${sections.map(s => `<li>${s}</li>`).join("")}</ul>`
              : `<p style="color:var(--text-muted);">None applicable</p>`}

            <p style="font-weight:700; font-size:16px; margin:14px 0 10px;">
              <i class="fas fa-circle-question" style="color:var(--blue-light); margin-right:8px;"></i>Why This Mapping
            </p>
            ${reasons.length
              ? `<ul>${reasons.map(r => `<li>${r}</li>`).join("")}</ul>`
              : `<p style="color:var(--text-muted);">—</p>`}

            <p style="font-weight:700; font-size:16px; margin:14px 0 10px;">
              <i class="fas fa-lightbulb" style="color:var(--yellow); margin-right:8px;"></i>What To Do Next
            </p>
            ${guidance.length
              ? `<ul>${guidance.map(g => `<li>${g}</li>`).join("")}</ul>`
              : `<p style="color:var(--text-muted);">—</p>`}
          </div>
        `;
      } else {
        legalHtml = lm
          ? `<p><b>Legal Mapping:</b> ${data.legal_section || "—"}</p>`
          : "";
      }

      // Confidence bar
      const conf = (data.confidence * 100).toFixed(1);
      const confColor = data.confidence >= 0.75 ? "var(--accent)" : data.confidence >= 0.5 ? "var(--yellow)" : "var(--green)";

      resultCard.innerHTML = `
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:44px; height:44px; border-radius:12px; background:${data.severity === 'Minimal' || data.severity === 'Low' ? 'rgba(6,214,160,0.12)' : 'rgba(230,57,70,0.12)'}; display:flex;align-items:center;justify-content:center;">
            <i class="fas ${data.severity === 'Minimal' || data.severity === 'Low' ? 'fa-check-circle' : 'fa-exclamation-triangle'}" style="font-size:18px; color:${data.severity === 'Minimal' || data.severity === 'Low' ? 'var(--green)' : 'var(--accent-light)'};"></i>
          </div>
          <div>
            <p style="font-size:20px; font-weight:800; margin:0; letter-spacing:-0.3px;">${data.label}</p>
            <p style="font-size:13px; color:var(--text-muted); margin:0;">Severity: <span class="severity-badge ${severityClass}">${data.severity}</span></p>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:16px;">
          <div style="padding:14px 18px; background:var(--bg-secondary); border-radius:var(--radius-md); border:1px solid var(--border);">
            <p style="font-size:12px; text-transform:uppercase; letter-spacing:1px; color:var(--text-muted); margin-bottom:4px;">Confidence</p>
            <p style="font-size:22px; font-weight:800; margin-bottom:6px;">${conf}%</p>
            <div style="height:4px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden;">
              <div style="height:100%; width:${conf}%; background:${confColor}; border-radius:4px; transition:width 1s ease;"></div>
            </div>
          </div>
          <div style="padding:14px 18px; background:var(--bg-secondary); border-radius:var(--radius-md); border:1px solid var(--border);">
            <p style="font-size:12px; text-transform:uppercase; letter-spacing:1px; color:var(--text-muted); margin-bottom:4px;">Scores</p>
            <p style="font-size:14px; margin-bottom:4px;"><i class="fas fa-biohazard" style="color:var(--accent); margin-right:6px; width:16px;"></i>Toxic: <b>${data.toxic_score}</b></p>
            <p style="font-size:14px;"><i class="fas fa-skull-crossbones" style="color:var(--orange); margin-right:6px; width:16px;"></i>Threat: <b>${data.threat_score}</b></p>
          </div>
        </div>

        ${legalHtml}
      `;

      // Alert banner
      if (data.severity === "Critical" || data.severity === "High") {
        alertBanner.innerHTML = `<i class="fas fa-exclamation-triangle" style="margin-right:8px;"></i>Severe cyberbullying detected. Immediate action recommended.`;
        alertBanner.style.background = "rgba(230, 57, 70, 0.1)";
        alertBanner.style.border = "1px solid rgba(230, 57, 70, 0.25)";
        alertBanner.style.color = "#ff6b6b";
      } else if (data.severity === "Moderate" || data.severity === "Medium") {
        alertBanner.innerHTML = `<i class="fas fa-info-circle" style="margin-right:8px;"></i>Potential bullying detected. Consider reporting this content.`;
        alertBanner.style.background = "rgba(255, 209, 102, 0.1)";
        alertBanner.style.border = "1px solid rgba(255, 209, 102, 0.25)";
        alertBanner.style.color = "#ffd166";
      } else if (data.severity === "Low") {
        alertBanner.innerHTML = `<i class="fas fa-shield-halved" style="margin-right:8px;"></i>Low-level harassment detected. Monitor and save evidence if repeated.`;
        alertBanner.style.background = "rgba(6, 214, 160, 0.08)";
        alertBanner.style.border = "1px solid rgba(6, 214, 160, 0.2)";
        alertBanner.style.color = "#06d6a0";
      } else {
        alertBanner.innerHTML = "";
        alertBanner.style.background = "";
        alertBanner.style.border = "";
      }
    })
    .catch(() => {
      resultCard.innerHTML = `<p style="color:var(--accent-light);"><i class="fas fa-plug-circle-xmark" style="margin-right:8px;"></i>Error connecting to server. Make sure the backend is running.</p>`;
    })
    .finally(() => {
      loader.style.display = "none";
      button.disabled = false;
    });
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

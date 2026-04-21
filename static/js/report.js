function previewImage() {
  const file = document.getElementById("screenshot").files[0];
  const preview = document.getElementById("preview");
  if (file) {
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
  }
}

function submitComplaint() {
  const name = document.getElementById("name").value.trim();
  const platform = document.getElementById("platform").value;
  const complaint = document.getElementById("complaintText").value.trim();
  const fileInput = document.getElementById("screenshot");
  const reportResult = document.getElementById("reportResult");

  if (!name || !complaint) {
    alert("Please enter Victim Name and Bullying Content");
    return;
  }

  const formData = new FormData();
  formData.append("name", name);
  formData.append("platform", platform);
  formData.append("complaint", complaint);

  if (fileInput.files[0]) {
    formData.append("screenshot", fileInput.files[0]);
  }

  // Show loading state
  reportResult.innerHTML = `
    <div class="glass-card" style="text-align:center; padding:24px;">
      <i class="fas fa-spinner fa-spin" style="font-size:20px; color:var(--accent); margin-right:10px;"></i>
      <span style="color:var(--text-secondary);">Submitting report & analyzing content...</span>
    </div>`;

  fetch("/api/report", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        reportResult.innerHTML = `
          <div class="glass-card" style="border-color:rgba(230,57,70,0.3);">
            <p style="color:var(--accent-light);"><i class="fas fa-exclamation-circle" style="margin-right:8px;"></i>${data.error}</p>
          </div>`;
        return;
      }
      reportResult.innerHTML = `
        <div class="glass-card" style="border-color:rgba(6,214,160,0.3);">
          <p style="font-size:18px; font-weight:700; color:var(--green); margin-bottom:12px;">
            <i class="fas fa-check-circle" style="margin-right:8px;"></i>Report Submitted Successfully
          </p>
          <p style="margin-bottom:6px;"><b style="color:var(--accent-light);">Severity:</b> <span class="severity-badge ${getSeverityClass(data.severity)}">${data.severity}</span></p>
          <p style="margin-bottom:12px;"><b style="color:var(--accent-light);">Legal Section:</b> ${data.legal_section || "—"}</p>
          <p style="opacity:0.6; font-size:13px;">
            <i class="fas fa-arrow-right" style="margin-right:6px;"></i>
            View it on the <a href="/dashboard" style="color:var(--cyan); text-decoration:underline;">Dashboard</a>
          </p>
        </div>`;
    })
    .catch(() => {
      reportResult.innerHTML = `
        <div class="glass-card" style="border-color:rgba(230,57,70,0.3);">
          <p style="color:var(--accent-light);"><i class="fas fa-exclamation-circle" style="margin-right:8px;"></i>Error submitting complaint. Please try again.</p>
        </div>`;
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

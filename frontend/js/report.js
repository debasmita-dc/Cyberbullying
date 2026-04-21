function previewImage() {
    const file = document.getElementById("screenshot").files[0];
    const preview = document.getElementById("preview");

    if (file) {
        preview.src = URL.createObjectURL(file);
    }
}

function submitComplaint() {
    const formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("platform", document.getElementById("platform").value);
    formData.append("complaint", document.getElementById("complaintText").value);
    formData.append("screenshot", document.getElementById("screenshot").files[0]);

    fetch("/api/report", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(() => alert("Complaint submitted successfully"))
    .catch(() => alert("Error submitting complaint"));
}

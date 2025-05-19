let resumeUploaded = false;
let uploadedResumeId = null;

function uploadResume() {
    const fileInput = document.getElementById('resumeUpload');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a resume file.");
        return;
    }

    const formData = new FormData();
    formData.append('resume', file);

    fetch('http://localhost:5000/upload_resume', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.resume_id) {
            resumeUploaded = true;
            uploadedResumeId = data.resume_id;

            const textarea = document.getElementById('parsedResumeText');
            let formatted = '';
            for (const [key, value] of Object.entries(data.parsed_data)) {
                formatted += `${key}: ${Array.isArray(value) ? value.join(', ') : value}\n`;
            }
            textarea.value = formatted;

            alert("Resume uploaded and parsed successfully!");
        } else {
            alert("Resume uploaded but no ID received.");
        }
    })
    .catch(error => {
        alert("Error uploading resume: " + error.message);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('resumeUpload').addEventListener('change', uploadResume);
});

function toggleEdit() {
    const textarea = document.getElementById('parsedResumeText');
    textarea.readOnly = !textarea.readOnly;
    if (!textarea.readOnly) {
        textarea.focus();
    }
}

function updateResumeInfo() {
    if (!uploadedResumeId) {
        alert("No resume uploaded yet.");
        return;
    }

    const editedText = document.getElementById('parsedResumeText').value;

    fetch('http://localhost:5000/update_resume_info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            resume_id: uploadedResumeId,
            edited_text: editedText
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        alert("Failed to update resume info: " + error.message);
    });
}

// Common function to send JD data (from file or manual input)
function submitJD(title, description) {
    if (!resumeUploaded || !uploadedResumeId) {
        return alert("Upload a resume first.");
    }

    if (!title || !description) {
        return alert("Please enter both title and description.");
    }

    fetch('http://localhost:5000/add_jd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title,
            description,
            resume_id: uploadedResumeId
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(err => {
        alert("Error submitting JD: " + err.message);
    });
}

// Manual JD submission
function uploadJDManual() {
    const title = document.getElementById('jdTitleManual').value.trim();
    const description = document.getElementById('jdDescManual').value.trim();
    submitJD(title, description);
}

// JD File upload
function uploadJDFile() {
    const title = document.getElementById('jdTitleFile').value.trim();
    const fileInput = document.getElementById('jdFileInput');
    const file = fileInput.files[0];

    if (!resumeUploaded || !uploadedResumeId) {
        return alert("Upload a resume first.");
    }

    if (!title || !file) {
        return alert("Please select a title and JD file.");
    }

    const formData = new FormData();
    formData.append('jd_file', file);

    fetch('http://localhost:5000/parse_jd_file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.description) {
            let formatted = '';
            for (const [key, value] of Object.entries(data.description)) {
                formatted += `${key}: ${Array.isArray(value) ? value.join(', ') : value}\n`;
            }
            submitJD(title, formatted);
        } else {
            alert("Failed to parse JD file.");
        }
    })
    .catch(err => {
        alert("Error parsing JD file: " + err.message);
    });
}

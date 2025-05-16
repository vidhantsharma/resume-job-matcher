let resumeUploaded = false;
let uploadedResumeId = null;  // To store resume_id returned by the backend

function uploadResume() {
    const fileInput = document.getElementById('resumeInput');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a resume first.");
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
            uploadedResumeId = data.resume_id;  // Save the ID
            alert("Upload successful: " + data.message);
        } else {
            alert("Upload failed: No resume ID received.");
        }
    })
    .catch(error => {
        alert("Upload failed: " + error.message);
    });
}

async function uploadJD() {
    if (!resumeUploaded || !uploadedResumeId) {
        alert("Please upload your resume before submitting the job description.");
        return;
    }

    const title = document.getElementById('jd-input').value.trim();
    const description = document.getElementById('jd-desc').value.trim();

    if (!title || !description) {
        return alert("Fill in both fields.");
    }

    try {
        const res = await fetch('/add_jd', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description,
                resume_id: uploadedResumeId  // Send the stored resume_id
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message);

        alert(data.message);
        console.log('JD uploaded and linked to resume:', data.jd_id);
    } catch (err) {
        console.error(err);
        alert("Failed to upload JD: " + err.message);
    }
}

document.getElementById('enter-button').addEventListener('click', function () {
    uploadJD();
});

document.getElementById('resumeInput').addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        uploadResume();
    }
});

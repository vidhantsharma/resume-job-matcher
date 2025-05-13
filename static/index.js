// sends uploaded resume to formData
function uploadResume() {
    const fileInput = document.getElementById('resumeInput');
    const file = fileInput.files[0];

    /*if (!file) {
        console.log("file not received")
        return;
    }*/
    const formData = new FormData();
    formData.append('resume', file);

    fetch('http://localhost:5000/upload_resume', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert("Upload successful: " + data.message);
    })
    .catch(error => {
        alert("Upload failed: " + error.message);
    });
}


document.getElementById('enter-button').addEventListener('click', function() {
    // Functionality for the Enter button
    let jobDescription = document.getElementById('job-description').value;
    console.log('Job Description:', jobDescription);
    // Add logic to process the job description
});

document.getElementById('resumeInput').addEventListener('click', function() {
    // Functionality for the Upload Resume button
    console.log('Resume Uploaded');
    uploadResume()
});


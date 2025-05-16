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

async function uploadJD() {
  const title = document.getElementById('jd-input').value.trim();
  const description = document.getElementById('jd-desc').value.trim();
  if (!title || !description) {
    return alert("Fill in both fields.");
  }

  try {
    const res = await fetch('/add_jd', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({title, description})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message);

    currentJdId = data.jd_id;                // store the new JD ID
    alert(data.message);

    // now enable the resume form
    document.getElementById('resume-form').style.display = 'block';
  } catch(err) {
    console.error(err);
    alert("Failed to upload JD: " + err.message);
  }
}


document.getElementById('enter-button').addEventListener('click', function() {
    // Functionality for the Enter button
    uploadJD();
    console.log('Job Description Upoaded', jobDescription);
    // Add logic to process the job description
});

document.getElementById('resumeInput').addEventListener('change', function() {
    // Functionality for the Upload Resume button
    uploadResume();
    console.log('Resume Uploaded');
});


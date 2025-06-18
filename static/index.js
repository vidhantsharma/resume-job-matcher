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

    // Show spinner
    document.getElementById('spinner-overlay').style.display = 'flex';

    fetch('http://localhost:5000/upload_resume', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('spinner-overlay').style.display = 'none';

        if (data.resume_id) {
            resumeUploaded = true;
            uploadedResumeId = data.resume_id;

            const first_name = document.getElementById('first_name');
            const last_name = document.getElementById('last_name');
            const email = document.getElementById('email');
            const phone = document.getElementById('phone');
            const total_experience = document.getElementById('total_experience');
            const degrees = document.getElementById('degrees');
            const institutions = document.getElementById('institutions');
            const majors = document.getElementById('majors');
            const skills = document.getElementById('skills');
            
            let formatted = {};
            const order = [
                'first_name',
                'last_name',
                'email',
                'phone',
                'total_experience',
                'degrees',
                'institutions',
                'majors',
                'skills'
            ];
            const labels = {
                first_name: 'First Name',
                last_name: 'Last Name',
                email: 'Email',
                phone: 'Phone',
                total_experience: 'Total Experience',
                degrees: 'Degrees',
                institutions: 'Institutions',
                majors: 'Majors',
                skills: 'Skills'
            };
            for (const key of order) {
                
                if (key in data.parsed_data) {
                    let value = data.parsed_data[key];

                    switch(key){
                        case "first_name":                        
                            first_name.value=value 
                            break;
                        
                        case "last_name":                        
                            last_name.value=value
                            break;

                        case "email":
                            email.value=value
                            break;

                        case "phone":
                            phone.value=value
                            break;

                        case "total_experience":
                            total_experience.value=value
                            console.log(total_experience.value)
                            break;

                        case "degrees":
                            degrees.value=value
                            break;

                        case "institutions":
                            institutions.value=value
                            break;

                        case "majors":
                            majors.value=value
                            break;

                        case "skills":
                            skills.value=value
                            break;
                }
                    
                    
                    formatted += `${labels[key]}: ${Array.isArray(value) ? value.join(', ') : value}\n`;
                }
            }
            

            alert("Resume uploaded and parsed successfully!");
        } else {
            alert("Resume uploaded but no ID received.");
        }
    })
    .catch(error => {
        alert("Error uploading resume: " + error.message);
    });
}

// form actions
document.getElementById("contactForm").addEventListener("submit", function(event) {
      event.preventDefault(); // Stop the form from submitting the default way

      // Get form values
      const name = document.getElementById("name").value.trim();
      const email = document.getElementById("email").value.trim();
      const message = document.getElementById("message").value.trim();

      // Basic validation
      if (!name || !email) {
        document.getElementById("responseMessage").textContent = "Please fill in all required fields.";
        document.getElementById("responseMessage").style.color = "red";
        return;
      }

      // Simulate sending data (you could send this to a server using fetch/AJAX)
      console.log("Form Submitted:", { name, email, message });

      // Show success message
      document.getElementById("responseMessage").textContent = "Thank you! Your message has been sent.";
      document.getElementById("responseMessage").style.color = "green";

      // Optionally, reset the form
      document.getElementById("contactForm").reset();
    });

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('resumeUpload').addEventListener('change', uploadResume);
});

function toggleEdit(id) {
    let textarea;

    switch (id) {
        case 'nameEdit':
            textarea = document.getElementById('name');
            break;
        case 'emailEdit':
            textarea = document.getElementById('email');
            break;
        // add more cases as needed
        default:
            console.warn('Unknown ID:', id);
            return;
    }

    if (textarea) {
        textarea.readOnly = !textarea.readOnly;
        if (!textarea.readOnly) {
            textarea.focus();
        }
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

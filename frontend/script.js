function recommendWhisky() {
    const whisky1 = document.getElementById("whisky1").value;
    const whisky2 = document.getElementById("whisky2").value;
    const whisky3 = document.getElementById("whisky3").value;

    // Replace this logic with your whisky recommender model
    // For this example, we'll just concatenate the whisky names.
    const recommendedWhisky = whisky1 + " " + whisky2 + " " + whisky3;

    document.getElementById("recommendedWhisky").textContent = `Recommended Whisky: ${recommendedWhisky}`;
}


// Add this JavaScript code to dynamically load unique distillery options from the CSV file


// Function to load distillery options from the CSV file
function loadDistilleryOptions() {
    fetch('distillery_data.csv') // Replace with the path to your CSV file
        .then(response => response.text())
        .then(data => {
            const distilleries = new Set(); // Use a Set to store unique distilleries

            // Parse the CSV data and extract distilleries
            const rows = data.split('\n');
            for (let i = 1; i < rows.length; i++) {
                const distillery = rows[i].split(',')[0].trim();
                distilleries.add(distillery);
            }

            // Populate distillery dropdowns with unique distillery options
            distillerySelects.forEach((distillerySelect) => {
                distilleries.forEach((distillery) => {
                    const option = document.createElement("option");
                    option.value = distillery;
                    option.textContent = distillery;
                    distillerySelect.appendChild(option);
                });
            });
        })
        .catch(error => {
            console.error('Error loading distillery data:', error);
        });
}


// Function to update the whisky dropdown based on distillery selection
function updateWhiskyDropdown(selectedDistillerySelect, whiskySelectId) {
    const selectedDistillery = selectedDistillerySelect.value;
    const whiskySelect = document.getElementById(whiskySelectId); // Get the whisky select element by ID

    // Fetch the CSV file
    fetch('distillery_data.csv')
        .then(response => response.text())
        .then(data => {
            // Parse the CSV data into an array of objects
            const rows = data.split('\n');
            const distilleryWhiskies = {};
            for (let i = 1; i < rows.length; i++) {
                const [distillery, whiskyName] = rows[i].split(',');
                if (!distilleryWhiskies[distillery]) {
                    distilleryWhiskies[distillery] = [];
                }
                distilleryWhiskies[distillery].push(whiskyName);
            }

            // Update the whisky dropdown
            const whiskies = distilleryWhiskies[selectedDistillery] || [];
            whiskySelect.innerHTML = "";
            if (whiskies.length === 0) {
                const option = document.createElement("option");
                option.value = "";
                option.textContent = "No whiskies available for this distillery";
                option.disabled = true;
                whiskySelect.appendChild(option);
            } else {
                whiskies.forEach((whiskyName) => {
                    const option = document.createElement("option");
                    option.value = whiskyName;
                    option.textContent = whiskyName;
                    whiskySelect.appendChild(option);
                });
            }
        });
}


// Model operation: this function operate the model when the user clicks the 'recommend' button:

// Simple functionality placeholder: simply add up the three names
function recommendWhisky() {
    const whisky1 = document.getElementById("whisky1").value;
    const whisky2 = document.getElementById("whisky2").value;
    const whisky3 = document.getElementById("whisky3").value;

    // Replace this logic with your whisky recommender model
    // For this example, we'll just concatenate the whisky names.
    const recommendedWhisky = whisky1 + " " + whisky2 + " " + whisky3;

    document.getElementById("recommendedWhisky").textContent = `Recommended Whisky: ${recommendedWhisky}`;
}


// Modify the recommendWhisky function to send a POST request to your backend API endpoint
async function recommendWhisky() {
    const whisky1 = document.getElementById("whisky1").value;
    const whisky2 = document.getElementById("whisky2").value;
    const whisky3 = document.getElementById("whisky3").value;

    const data = { whisky_names: [whisky1, whisky2, whisky3] };

    try {
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Failed to fetch recommendation');

        const result = await response.json();
        document.getElementById("recommendedWhisky").textContent = `Recommended Whisky: ${result.recommended_whisky}`;
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to fetch recommendation. Please try again.');
    }
}




// Add this function to toggle the display of rating or reason based on the selected feedback
function toggleFeedbackOptions() {
    const feedbackOption = document.querySelector('input[name="feedback1"]:checked').value;
    const ratingSection = document.getElementById('ratingSection');
    const reasonSection = document.getElementById('reasonSection');

    if (feedbackOption === "I know this whisky") {
        ratingSection.style.display = 'block';
        reasonSection.style.display = 'none';
    } else if (feedbackOption === "I don't know this whisky") {
        ratingSection.style.display = 'none';
        reasonSection.style.display = 'block';
    }
}


// Function to submit feedback
function submitFeedback() {
    const feedbackForm = document.getElementById('feedbackForm');
    const feedback1 = document.querySelector('input[name="feedback1"]:checked').value;
    let feedback2;

    if (feedback1 === "I know this whisky") {
        feedback2 = document.querySelector('input[name="feedback2"]').value;
    } else if (feedback1 === "I don't know this whisky") {
        feedback2 = document.querySelector('select[name="feedback2"]').value;
    }

    // You can now send this feedback data to your backend or save it to a CSV file
    // Example: Send feedback data to the backend for processing
    const feedbackData = {
        whisky1: document.getElementById('whisky1').value,
        recommendedWhisky: document.getElementById('recommendedWhisky').textContent,
        feedback1: feedback1,
        feedback2: feedback2
    };

    fetch('/submitFeedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
    })
    .then(response => {
        if (response.ok) {
            alert('Feedback submitted successfully!');
            // Clear form or perform any other necessary actions
            feedbackForm.reset();
        } else {
            alert('Failed to submit feedback. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


// Get references to the select elements
const distillerySelects = document.querySelectorAll('.distillery-select');
const whiskySelects = document.querySelectorAll('.whisky-select');

// Call the loadDistilleryOptions function to populate distillery dropdowns initially
loadDistilleryOptions();

// Attach event listeners to distillery select elements
const distillerySelect1 = document.getElementById('distillery1');
const whiskySelect1Id = 'whisky1'; // ID of the corresponding whisky select element
distillerySelect1.addEventListener('change', function() {
    updateWhiskyDropdown(distillerySelect1, whiskySelect1Id);
});

const distillerySelect2 = document.getElementById('distillery2');
const whiskySelect2Id = 'whisky2'; // ID of the corresponding whisky select element
distillerySelect2.addEventListener('change', function() {
    updateWhiskyDropdown(distillerySelect2, whiskySelect2Id);
});

const distillerySelect3 = document.getElementById('distillery3');
const whiskySelect3Id = 'whisky3'; // ID of the corresponding whisky select element
distillerySelect3.addEventListener('change', function() {
    updateWhiskyDropdown(distillerySelect3, whiskySelect3Id);
});

// Add an event listener to call the toggleFeedbackOptions function when a radio button is clicked
const feedbackRadios = document.querySelectorAll('input[name="feedback1"]');
feedbackRadios.forEach(radio => {
    radio.addEventListener('click', toggleFeedbackOptions);
});


// Call the updateWhiskyDropdown function initially to populate the whisky dropdown with the default distillery
updateWhiskyDropdown();
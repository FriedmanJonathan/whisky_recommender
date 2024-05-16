// Add this JavaScript code to dynamically load unique distillery options from the CSV file

// Function to load distillery options from the CSV file
async function loadDistilleryOptions() {
    try {
        const response = await fetch('distillery_data.csv');
        if (!response.ok) throw new Error('Failed to load CSV data');

        const data = await response.text();
        const distilleries = new Set(); // Use a Set to store unique distilleries

        // Parse the CSV data and extract distilleries
        const rows = data.split('\n').slice(1); // Skip the header
        rows.forEach(row => {
            const [distillery] = row.split(','); // Only get the first column
            if (distillery) distilleries.add(distillery.trim());
        });

        // Populate distillery dropdowns
        const distillerySelects = document.querySelectorAll('.distillery-select');
        distillerySelects.forEach((select) => {
            distilleries.forEach((distillery) => {
                const option = document.createElement("option");
                option.value = distillery;
                option.textContent = distillery;
                select.appendChild(option);
            });
        });
    } catch (error) {
        console.error('Error loading distillery data:', error);
    }
}

// Function to update the whisky dropdown based on distillery selection
async function updateWhiskyDropdown(selectedDistillerySelect, whiskySelectId) {
    const selectedDistillery = selectedDistillerySelect.value;
    const whiskySelect = document.getElementById(whiskySelectId);

    try {
        // Fetch the CSV data
        const response = await fetch('distillery_data.csv');
        if (!response.ok) throw new Error('Failed to load CSV data');

        const data = await response.text();

        // Parse the CSV data into an object mapping distilleries to whiskies
        const distilleryWhiskies = {};
        const rows = data.split('\n');

        for (let i = 1; i < rows.length; i++) {
            const [distillery, whiskyName] = rows[i].split(',').map(str => str.trim());
            if (!distilleryWhiskies[distillery]) {
                distilleryWhiskies[distillery] = [];
            }
            distilleryWhiskies[distillery].push(whiskyName);
        }

        // Update the whisky dropdown based on the selected distillery
        whiskySelect.innerHTML = ""; // Clear the current options

        // Add a default "Select a whisky" option
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Select a whisky";
        defaultOption.disabled = true;
        defaultOption.selected = true;
        whiskySelect.appendChild(defaultOption);

        const whiskies = distilleryWhiskies[selectedDistillery] || [];
        if (whiskies.length === 0) {
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "No whiskies available for this distillery";
            option.disabled = true;
            whiskySelect.appendChild(option);
        } else {
            whiskies.forEach(whiskyName => {
                const option = document.createElement("option");
                option.value = whiskyName;
                option.textContent = whiskyName;
                whiskySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading or processing distillery data:', error);
        alert('Failed to load distillery data. Please try again.');
    }
}

// Model operation: this function operate the model when the user clicks the 'recommend' button:
// Simple functionality placeholder: simply add up the three names
// Modify the recommendWhisky function to send a POST request to your backend API endpoint
async function recommendWhisky() {
    // Collect whisky and distillery values
    const distillery1 = document.getElementById("distillery1").value;
    const whisky1 = document.getElementById("whisky1").value;
    const distillery2 = document.getElementById("distillery2").value;
    const whisky2 = document.getElementById("whisky2").value;
    const distillery3 = document.getElementById("distillery3").value;
    const whisky3 = document.getElementById("whisky3").value;

    // Concatenate distillery and whisky values
    const whiskyWithDistillery1 = `${distillery1} ${whisky1}`;
    const whiskyWithDistillery2 = `${distillery2} ${whisky2}`;
    const whiskyWithDistillery3 = `${distillery3} ${whisky3}`;

    // Log these values to verify correct data collection
    console.log("Whisky with Distillery 1:", whiskyWithDistillery1);
    console.log("Whisky with Distillery 2:", whiskyWithDistillery2);
    console.log("Whisky with Distillery 3:", whiskyWithDistillery3);

    // Prepare the data to send to the backend
    const data = {
        whisky_names: [whiskyWithDistillery1, whiskyWithDistillery2, whiskyWithDistillery3]
    };

    console.log("whisky names", data);
    console.log("Stringified", JSON.stringify(data));

    try {
        // Send the data to the backend for recommendations
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error(`Failed to fetch recommendation, status: ${response.status}`);

        // Process the server's response
        const result = await response.json();
        console.log("Recommendation Result:", result);
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

    if (feedbackOption === "know") {
        ratingSection.style.display = 'block';
    } else {
        ratingSection.style.display = 'none';
    }
}

// Function to submit feedback
function submitFeedback() {
    const feedbackForm = document.getElementById('feedbackForm');
    const feedback1 = document.querySelector('input[name="feedback1"]:checked').value;
    let rating = null;
    if (feedback1 === "know") {
        rating = document.getElementById('rating').value || null;
    }
    const feedback2 = document.getElementById('feedback2').value || "";

    // You can now send this feedback data to your backend or save it to a CSV file
    // Example: Send feedback data to the backend for processing
    const feedbackData = {
        whisky1: document.getElementById('whisky1').value,
        recommendedWhisky: document.getElementById('recommendedWhisky').textContent,
        feedback1: feedback1,
        rating: rating,
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

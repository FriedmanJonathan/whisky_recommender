// script.js
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


// Call the updateWhiskyDropdown function initially to populate the whisky dropdown with the default distillery
updateWhiskyDropdown();
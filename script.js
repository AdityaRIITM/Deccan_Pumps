// Data for pump type descriptions
const pumpTypeDescriptions = {
    'A': 'Slurry Pump, end suction',
    'B': 'Solid-handling, end suction',
    'C': 'Submersible Sewage',
    'F': 'ASME B73, API End Section-small',
    'G': 'End Section Large',
    'J': 'Double Section',
    'V': 'Vertical Turbine, Mixed flow and propeller, single and multistage diffuser type'
};

document.addEventListener('DOMContentLoaded', () => {
    const pumpTypeSelect = document.getElementById('pumpType');
    const pumpTypeDescriptionElem = document.getElementById('pumpTypeDescription');
    const calculateBtn = document.getElementById('calculateBtn');

    // Function to update pump type description
    function updatePumpTypeDescription() {
        const selectedType = pumpTypeSelect.value;
        pumpTypeDescriptionElem.textContent = pumpTypeDescriptions[selectedType] || 'Select a pump type to see description.';
    }

    // Event listener for pump type selection change
    pumpTypeSelect.addEventListener('change', updatePumpTypeDescription);

    // Initial description display
    updatePumpTypeDescription();

    // Event listener for the calculate button
    calculateBtn.addEventListener('click', async () => {
        const pumpFlowValue = parseFloat(document.getElementById('pumpFlowValue').value);
        const selectedFlowUnit = document.querySelector('input[name="flowUnit"]:checked').value;
        const specificSpeed = parseFloat(document.getElementById('specificSpeed').value);
        const pumpType = document.getElementById('pumpType').value;

        // Basic validation
        if (isNaN(pumpFlowValue) || isNaN(specificSpeed) || !pumpType) {
            alert('Please enter valid numbers for Pump Flow and Specific Speed, and select a Pump Type.');
            return;
        }

        // Prepare data to send to backend
        const data = {
            C5: parseInt(selectedFlowUnit),
            C6: pumpFlowValue,
            F5: specificSpeed,
            F6: pumpType
        };

        try {
            // Placeholder for the backend API endpoint
            // We will set up this backend later. For now, this will simulate.
            // When you have a Flask/Node.js backend, replace this URL:
            const response = await fetch('https://deccan-pumps-2.onrender.com/calculate', { // Adjust port if your backend uses a different one
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                // If the response is not OK (e.g., 400 Bad Request, 500 Internal Server Error)
                const errorData = await response.json(); // Assuming backend sends error details as JSON
                throw new Error(`errorData.error || HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // Update the display with the calculated results
            document.getElementById('efficiencyOptimum').textContent = result.efficiencyOptimum.toFixed(2);
            document.getElementById('efficiencyCorrection').textContent = result.efficiencyCorrection.toFixed(2);
            document.getElementById('efficiencyDeviation').textContent = result.efficiencyDeviation.toFixed(2);
            document.getElementById('actualEfficiency').innerHTML = result.actualEfficiency; // Use innerHTML for ± symbol and %
            
        } catch (error) {
            console.error('Error calculating efficiencies:', error);
            alert('An error occurred during calculation. Please check your inputs. Error: ' + error.message);
            // Optionally clear results or show error message on UI
            document.getElementById('efficiencyOptimum').textContent = '--';
            document.getElementById('efficiencyCorrection').textContent = '--';
            document.getElementById('efficiencyDeviation').textContent = '--';
            document.getElementById('actualEfficiency').textContent = '--';
        }
    });
});
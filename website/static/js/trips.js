window.addEventListener('DOMContentLoaded', function() {
   // Put in the search boxes for the "Add Trip" modal
   $('#trip_type').select2({
       theme: "bootstrap-5",
       dropdownParent: $('#addTripModal')
   });

   // Put in the search boxes for the "Remove Trip" modal
   $('#removeTripSelect').select2({
       theme: "bootstrap-5",
       dropdownParent: $('#removeTripModal')
   });

   // When the "Next" button in the first remove modal is clicked
   $('#openConfirmTripModalBtn').on('click', function() {
       // Get the selected trip's ID and Name
       const tripId = $('#removeTripSelect').val();
       const tripName = $('#removeTripSelect option:selected').text().trim();

       // Make sure a trip was actually selected
       if (tripId) {
           // Pass the data to the confirmation modal
           $('#tripNameToRemove').text(tripName);
           $('#tripIdToRemove').val(tripId);

           // Hide the first modal and show the second one
           $('#removeTripModal').modal('hide');
           $('#confirmRemoveTripModal').modal('show');
       } else {
           // If they didn't select anyone, just do nothing (or show an alert)
           alert("Please select a trip to remove.");
       }
   });

   // Initialize Select2 for Add/Edit Trip modal dropdowns
   $('#trip_type').select2({
        theme: "bootstrap-5",
        dropdownParent: $('#addTripModal'),
        placeholder: "Select an option...",
        allowClear: true
    });

    // Handle Add Trip button click - clear form for new trip
    $('button[data-bs-target="#addTripModal"]').not('.edit-trip-btn').on('click', function() {
        // Clear all form fields
        $('#tripForm')[0].reset();
        $('#trip_db_id').val('');
        $('#tripForm').attr('action', '/add-trip');
        $('#addTripModalLabel').text('Add New Trip');
        $('#tripSubmitBtn').text('Save Trip');

        // Clear Select2 dropdown
        $('#trip_type').val(null).trigger('change');
    });

    // Handle Edit Trip button click
    $(document).on('click', '.edit-trip-btn', function() {
        const tripId = String($(this).data('trip-id')); // Convert to string for JSON key lookup

        // Get trip data from global tripsData object (loaded from JSON)
        const tripData = window.tripsData && window.tripsData[tripId];

        if (!tripData) {
            console.error('Trip data not found for ID:', tripId);
            return;
        }

        // Change form to edit mode
        $('#tripForm').attr('action', '/edit-trip');
        $('#addTripModalLabel').text('Edit Trip');
        $('#tripSubmitBtn').text('Save Changes');

        // Set hidden database ID field
        $('#trip_db_id').val(tripData.id);

        // Populate the modal fields with the trip data
        $('#trip_name').val(tripData.trip_name || '');
        $('#trip_type').val(tripData.trip_type || '').trigger('change');
        $('#capacity').val(tripData.capacity || '');
        $('#address').val(tripData.address || '');
        $('#water').prop('checked', tripData.water === true || tripData.water === 'true');
        $('#tent').prop('checked', tripData.tent === true || tripData.tent === 'true');
    });

    // CSV Column Matching Script for Trips
    const tripDbFields = [
        { value: '', label: '-- Skip Column --' },
        { value: 'trip_name', label: 'Trip Name' },
        { value: 'trip_type', label: 'Trip Type' },
        { value: 'capacity', label: 'Capacity' },
        { value: 'address', label: 'Address' },
        { value: 'water', label: 'Water' },
        { value: 'tent', label: 'Tent' }
    ];

    document.getElementById('csv_file').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(event) {
            const text = event.target.result;
            parseCSV(text);
        };
        reader.readAsText(file);
    });

    function parseCSV(text) {
        const lines = text.split('\n').filter(line => line.trim());
        if (lines.length === 0) return;

        function parseCSVLine(line) {
            const result = [];
            let current = '';
            let inQuotes = false;
            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                    result.push(current.trim());
                    current = '';
                } else {
                    current += char;
                }
            }
            result.push(current.trim());
            return result;
        }

        const headerLine = parseCSVLine(lines[0]);
        const csvColumns = headerLine.map(col => col.replace(/^"|"$/g, '').trim());

        showColumnMatching(csvColumns);
    }

    function showColumnMatching(csvColumns) {
        const container = document.getElementById('matchingRows');
        container.innerHTML = '';

        csvColumns.forEach((csvCol, index) => {
            const row = document.createElement('div');
            row.className = 'mb-3';

            const label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = csvCol;

            const select = document.createElement('select');
            select.className = 'form-select';
            select.name = csvCol;
            select.id = `match_${index}`;

            let autoMatch = '';
            const csvLower = csvCol.toLowerCase().replace(/[^a-z0-9]/g, '_');
            if (csvLower.includes('trip') && csvLower.includes('name')) autoMatch = 'trip_name';
            else if (csvLower.includes('trip') && csvLower.includes('type')) autoMatch = 'trip_type';
            else if (csvLower.includes('capacity')) autoMatch = 'capacity';
            else if (csvLower.includes('address')) autoMatch = 'address';
            else if (csvLower.includes('water')) autoMatch = 'water';
            else if (csvLower.includes('tent')) autoMatch = 'tent';

            tripDbFields.forEach(field => {
                const option = document.createElement('option');
                option.value = field.value;
                option.textContent = field.label;
                if (field.value === autoMatch) {
                    option.selected = true;
                }
                select.appendChild(option);
            });

            row.appendChild(label);
            row.appendChild(select);
            container.appendChild(row);
        });

        // Add Action dropdown at the end
        const actionRow = document.createElement('div');
        actionRow.className = 'mb-3';

        const actionLabel = document.createElement('label');
        actionLabel.className = 'form-label';
        actionLabel.innerHTML = '<strong>Action</strong>';

        const actionSelect = document.createElement('select');
        actionSelect.className = 'form-select';
        actionSelect.name = 'importMode';
        actionSelect.id = 'importMode';
        actionSelect.required = true;

        const addOption = document.createElement('option');
        addOption.value = 'add';
        addOption.textContent = 'Add New Trips';
        actionSelect.appendChild(addOption);

        const updateOption = document.createElement('option');
        updateOption.value = 'update';
        updateOption.textContent = 'Update Existing Trips';
        actionSelect.appendChild(updateOption);

        actionRow.appendChild(actionLabel);
        actionRow.appendChild(actionSelect);
        container.appendChild(actionRow);

        document.getElementById('columnMatchingContainer').style.display = 'block';
        document.getElementById('submitBtn').style.display = 'inline-block';
    }

    document.getElementById('csvMatchingForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Uploading...';

        fetch(this.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`CSV uploaded successfully!\nAdded: ${data.added}, Updated: ${data.updated}, Skipped: ${data.skipped}`);
                if (data.errors && data.errors.length > 0) {
                    console.warn('Errors:', data.errors);
                }
                const modal = bootstrap.Modal.getInstance(document.getElementById('uploadCSVModal'));
                modal.hide();
                window.location.reload();
            } else {
                alert('Error: ' + (data.message || 'Failed to upload CSV'));
                submitBtn.disabled = false;
                submitBtn.textContent = 'Upload CSV';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error uploading CSV: ' + error.message);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Upload CSV';
        });
    });

    document.getElementById('uploadCSVModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('csv_file').value = '';
        document.getElementById('columnMatchingContainer').style.display = 'none';
        document.getElementById('submitBtn').style.display = 'none';
    });
});


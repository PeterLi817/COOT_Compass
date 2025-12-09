window.addEventListener('DOMContentLoaded', function() {
   // Put in the search boxes for the "Add Student" modal
   $('#trip_select').select2({
       theme: "bootstrap-5",
       dropdownParent: $('#addStudentModal')
   });

   // Put in the search boxes for the "Remove Student" modal
   $('#removeStudentSelect').select2({
       theme: "bootstrap-5",
       dropdownParent: $('#removeStudentModal')
   });


    // Initialize Select2 for move student dropdown
    $(document).ready(function() {
        $('#student_name').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#moveStudentModal'),
            placeholder: "Select a student...",
            allowClear: true
        });

        // Initialize Select2 for swap student dropdowns
        $('#student1_name').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#swapStudentsModal'),
            placeholder: "Select a student...",
            allowClear: true
        });

        $('#student2_name').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#swapStudentsModal'),
            placeholder: "Select a student...",
            allowClear: true
        });

        // Initialize Select2 for add/edit student modal dropdowns (using addStudentModal)
        $('#trip_pref_1').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#addStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#trip_pref_2').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#addStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#trip_pref_3').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#addStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#assigned-trip').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#addStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#water-comfort').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#addStudentModal .modal-content'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#tent-comfort').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#addStudentModal .modal-content'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#gender').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#addStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });
    });

    // Re-initialize select2 when the modal is shown so position is calculated while visible
    $('#addStudentModal').on('shown.bs.modal', function () {
        // Destroy and re-init to ensure correct positioning
        ['#trip_pref_1','#trip_pref_2','#trip_pref_3','#assigned-trip','#water-comfort','#tent-comfort','#gender'].forEach(function(sel){
            if ($(sel).hasClass('select2-hidden-accessible')) {
                $(sel).select2('destroy');
            }
            $(sel).select2({
                theme: "bootstrap-5",
                dropdownParent: $('#addStudentModal .modal-content'),
                placeholder: "Select an option...",
                allowClear: true
            });
        });
    });

   // When the "Next" button in the first remove modal is clicked
   $('#openConfirmModalBtn').on('click', function() {
       // Get the selected student's ID and Name
       const studentId = $('#removeStudentSelect').val();
       const studentName = $('#removeStudentSelect option:selected').text().trim();

       // Make sure a student was actually selected
       if (studentId) {
           // Pass the data to the confirmation modal
           $('#studentNameToRemove').text(studentName);
           $('#studentIdToRemove').val(studentId);

           // Hide the first modal and show the second one
           $('#removeStudentModal').modal('hide');
           $('#confirmRemoveModal').modal('show');
       } else {
           // If they didn't select anyone, just do nothing (or show an alert)
           alert("Please select a student to remove.");
       }
   });

    // Handle Add Student button click - clear form for new student
    $('button[data-bs-target="#addStudentModal"]').not('.edit-student-btn').on('click', function() {
        // Clear all form fields
        $('#studentForm')[0].reset();
        $('#student_db_id').val('');
        $('#studentForm').attr('action', '/add-student');
        $('#addStudentModalLabel').text('Add New Student');
        $('#studentSubmitBtn').text('Save Student');

        // Clear Select2 dropdowns
        $('#trip_pref_1, #trip_pref_2, #trip_pref_3, #assigned-trip, #water-comfort, #tent-comfort, #gender').val(null).trigger('change');

        // Change visible student_id field name back to student_id for add mode
        $('#student_id').attr('name', 'student_id');
    });

    // Handle Edit Student button click
    $(document).on('click', '.edit-student-btn', function() {
        const studentId = String($(this).data('student-id')); // Convert to string for JSON key lookup

        // Get student data from global studentsData object (loaded from JSON)
        const studentData = window.studentsData && window.studentsData[studentId];

        if (!studentData) {
            console.error('Student data not found for ID:', studentId);
            return;
        }

        // Change form to edit mode
        $('#studentForm').attr('action', '/edit-student');
        $('#addStudentModalLabel').text('Edit Student');
        $('#studentSubmitBtn').text('Save Changes');

        // Set hidden database ID field
        $('#student_db_id').val(studentData.id);

        // Change visible student_id field name to student_id_field for edit mode
        $('#student_id').attr('name', 'student_id_field');

        // Populate the form with student data
        $('#student_id').val(studentData.student_id);
        $('#email').val(studentData.email);
        $('#first_name').val(studentData.first_name);
        $('#last_name').val(studentData.last_name);
        $('#dorm').val(studentData.dorm || '');
        $('#athletic_team').val(studentData.athletic_team || '');
        $('#hometown').val(studentData.hometown || '');
        $('#notes').val(studentData.notes || '');
        $('#allergies_dietary_restrictions').val(studentData.allergies_dietary_restrictions || '');

        // Set checkboxes
        $('#poc').prop('checked', studentData.poc === true || studentData.poc === 'true');
        $('#fli_international').prop('checked', studentData.fli_international === true || studentData.fli_international === 'true');

        // Set select dropdowns
        $('#trip_pref_1').val(studentData.trip_pref_1 || '').trigger('change');
        $('#trip_pref_2').val(studentData.trip_pref_2 || '').trigger('change');
        $('#trip_pref_3').val(studentData.trip_pref_3 || '').trigger('change');
        $('#gender').val(studentData.gender || '').trigger('change');
        $('#water-comfort').val(studentData.water_comfort || '').trigger('change');
        $('#tent-comfort').val(studentData.tent_comfort || '').trigger('change');
        $('#assigned-trip').val(studentData.trip_id ? String(studentData.trip_id) : '').trigger('change');
    });

    // CSV Column Matching Script for First Years
    const dbFields = [
        { value: '', label: '-- Skip Column --' },
        { value: 'student_id', label: 'Student ID' },
        { value: 'first_name', label: 'First Name' },
        { value: 'last_name', label: 'Last Name' },
        { value: 'email', label: 'Email' },
        { value: 'gender', label: 'Gender' },
        { value: 'athletic_team', label: 'Athletic Team' },
        { value: 'hometown', label: 'Hometown' },
        { value: 'dorm', label: 'Dorm' },
        { value: 'water_comfort', label: 'Water Comfort' },
        { value: 'tent_comfort', label: 'Tent Comfort' },
        { value: 'trip_name', label: 'Trip Name' },
        { value: 'trip_type', label: 'Trip Type' },
        { value: 'trip_pref_1', label: 'Trip Preference 1' },
        { value: 'trip_pref_2', label: 'Trip Preference 2' },
        { value: 'trip_pref_3', label: 'Trip Preference 3' },
        { value: 'poc', label: 'POC' },
        { value: 'fli_international', label: 'FLI/International' },
        { value: 'notes', label: 'Notes' }
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
            if (csvLower.includes('student') && csvLower.includes('id')) autoMatch = 'student_id';
            else if (csvLower.includes('first') && csvLower.includes('name')) autoMatch = 'first_name';
            else if (csvLower.includes('last') && csvLower.includes('name')) autoMatch = 'last_name';
            else if (csvLower.includes('email')) autoMatch = 'email';
            else if (csvLower.includes('gender') || csvLower.includes('sex')) autoMatch = 'gender';
            else if (csvLower.includes('athletic') || csvLower.includes('team') || csvLower.includes('sport')) autoMatch = 'athletic_team';
            else if (csvLower.includes('hometown') || csvLower.includes('city')) autoMatch = 'hometown';
            else if (csvLower.includes('dorm') || csvLower.includes('residence')) autoMatch = 'dorm';
            else if (csvLower.includes('water') && csvLower.includes('comfort')) autoMatch = 'water_comfort';
            else if (csvLower.includes('tent') && csvLower.includes('comfort')) autoMatch = 'tent_comfort';
            else if (csvLower.includes('trip') && csvLower.includes('name')) autoMatch = 'trip_name';
            else if (csvLower.includes('trip') && csvLower.includes('type')) autoMatch = 'trip_type';
            else if (csvLower.includes('pref') && csvLower.includes('1')) autoMatch = 'trip_pref_1';
            else if (csvLower.includes('pref') && csvLower.includes('2')) autoMatch = 'trip_pref_2';
            else if (csvLower.includes('pref') && csvLower.includes('3')) autoMatch = 'trip_pref_3';
            else if (csvLower.includes('poc')) autoMatch = 'poc';
            else if (csvLower.includes('fli') || csvLower.includes('international')) autoMatch = 'fli_international';
            else if (csvLower.includes('note')) autoMatch = 'notes';

            dbFields.forEach(field => {
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
        addOption.textContent = 'Add New Students';
        actionSelect.appendChild(addOption);

        const updateOption = document.createElement('option');
        updateOption.value = 'update';
        updateOption.textContent = 'Update Existing Students';
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
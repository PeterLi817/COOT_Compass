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
});
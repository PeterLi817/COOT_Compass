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

        // Initialize Select2 for edit student modal dropdowns
        $('#edit_trip_pref_1').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#editStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#edit_trip_pref_2').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#editStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#edit_trip_pref_3').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#editStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#edit_assigned-trip').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#editStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#edit_water-comfort').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#editStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#edit_tent-comfort').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#editStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
        });

        $('#edit_gender').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#editStudentModal'),
            placeholder: "Select an option...",
            allowClear: true
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

    // Handle Edit Student button click
    $(document).on('click', '.edit-student-btn', function() {
        const studentId = String($(this).data('student-id')); // Convert to string for JSON key lookup

        // Get student data from global studentsData object (loaded from JSON)
        const studentData = window.studentsData && window.studentsData[studentId];

        if (!studentData) {
            console.error('Student data not found for ID:', studentId);
            return;
        }

        // Populate the edit form with student data
        $('#edit_student_id').val(studentData.id);
        $('#edit_student_id_field').val(studentData.student_id);
        $('#edit_email').val(studentData.email);
        $('#edit_first_name').val(studentData.first_name);
        $('#edit_last_name').val(studentData.last_name);
        $('#edit_dorm').val(studentData.dorm || '');
        $('#edit_athletic_team').val(studentData.athletic_team || '');
        $('#edit_hometown').val(studentData.hometown || '');
        $('#edit_notes').val(studentData.notes || '');

        // Set checkboxes
        $('#edit_poc').prop('checked', studentData.poc === true || studentData.poc === 'true');
        $('#edit_fli_international').prop('checked', studentData.fli_international === true || studentData.fli_international === 'true');

        // Set select dropdowns
        $('#edit_trip_pref_1').val(studentData.trip_pref_1 || '').trigger('change');
        $('#edit_trip_pref_2').val(studentData.trip_pref_2 || '').trigger('change');
        $('#edit_trip_pref_3').val(studentData.trip_pref_3 || '').trigger('change');
        $('#edit_gender').val(studentData.gender || '').trigger('change');
        $('#edit_water-comfort').val(studentData.water_comfort || '').trigger('change');
        $('#edit_tent-comfort').val(studentData.tent_comfort || '').trigger('change');
        $('#edit_assigned-trip').val(studentData.trip_id ? String(studentData.trip_id) : '').trigger('change');
    });
});
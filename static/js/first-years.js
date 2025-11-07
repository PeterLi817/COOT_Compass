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
});
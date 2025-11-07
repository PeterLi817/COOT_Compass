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
});


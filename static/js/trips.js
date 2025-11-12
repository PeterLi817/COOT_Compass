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

   // Initialize Select2 for Edit Trip modal dropdowns
   $('#edit_trip_type').select2({
        theme: "bootstrap-5",
        dropdownParent: $('#editTripModal'),
        placeholder: "Select an option...",
        allowClear: true
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

        // Populate the modal fields with the trip data
        $('#edit_trip_id').val(tripData.id);
        $('#edit_trip_name').val(tripData.trip_name || '');
        $('#edit_trip_type').val(tripData.trip_type || '').trigger('change');
        $('#edit_capacity').val(tripData.capacity || '');
        $('#edit_address').val(tripData.address || '');
        $('#edit_water').prop('checked', tripData.water === true || tripData.water === 'true');
        $('#edit_tent').prop('checked', tripData.tent === true || tripData.tent === 'true');
    });
});


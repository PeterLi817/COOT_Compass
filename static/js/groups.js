window.addEventListener('DOMContentLoaded', event => {
    // Initialize all tables with class 'datatables-table'
    const tables = document.querySelectorAll('.datatables-table');
    tables.forEach(table => {
        new simpleDatatables.DataTable(table);
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

    // Search and filter functionality for groups
    const searchInput = document.getElementById('groupSearch');
    const clearSearchBtn = document.getElementById('clearSearch');
    const filterTripType = document.getElementById('filterTripType');
    const filterWater = document.getElementById('filterWater');
    const filterTent = document.getElementById('filterTent');
    const filterOpenSlots = document.getElementById('filterOpenSlots');
    const filterValidity = document.getElementById('filterValidity');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const groupBoxes = document.querySelectorAll('.group-box');

    // Function to filter groups based on search and filters
    function filterGroups() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const tripTypeFilter = filterTripType.value.toLowerCase();
        const waterFilter = filterWater.value;
        const tentFilter = filterTent.value;
        const openSlotsFilter = filterOpenSlots.value;
        const validityFilter = filterValidity.value;

        // Show/hide clear search button
        clearSearchBtn.style.display = searchTerm ? 'block' : 'none';

        let visibleCount = 0;
        groupBoxes.forEach(box => {
            let matches = true;

            // Search filter
            if (searchTerm) {
                const searchText = box.getAttribute('data-search-text') || '';
                if (!searchText.includes(searchTerm)) {
                    matches = false;
                }
            }

            // Trip type filter
            if (matches && tripTypeFilter) {
                const tripType = box.getAttribute('data-trip-type') || '';
                if (tripType !== tripTypeFilter) {
                    matches = false;
                }
            }

            // Water filter
            if (matches && waterFilter) {
                const water = box.getAttribute('data-water') || '';
                if (water !== waterFilter) {
                    matches = false;
                }
            }

            // Tent filter
            if (matches && tentFilter) {
                const tent = box.getAttribute('data-tent') || '';
                if (tent !== tentFilter) {
                    matches = false;
                }
            }

            // Open slots filter
            if (matches && openSlotsFilter) {
                const openSlots = box.getAttribute('data-open-slots') || '';
                if (openSlots !== openSlotsFilter) {
                    matches = false;
                }
            }

            // Validity filter
            if (matches && validityFilter) {
                const valid = box.getAttribute('data-valid') || '';
                if (valid !== validityFilter) {
                    matches = false;
                }
            }

            // Show or hide the box
            box.style.display = matches ? '' : 'none';
            if (matches) {
                visibleCount++;
            }
        });

        // Toggle "no filtered trips" message if applicable
        const noFilteredMsg = document.getElementById('noFilteredTripsMessage');
        if (noFilteredMsg) {
            if (groupBoxes.length > 0 && visibleCount === 0) {
                noFilteredMsg.style.display = '';
            } else {
                noFilteredMsg.style.display = 'none';
            }
        }
    }

    // Search input events
    searchInput.addEventListener('input', filterGroups);

    // Clear search button
    clearSearchBtn.addEventListener('click', function() {
        searchInput.value = '';
        filterGroups();
        searchInput.focus();
    });

    // Filter dropdown events
    filterTripType.addEventListener('change', filterGroups);
    filterWater.addEventListener('change', filterGroups);
    filterTent.addEventListener('change', filterGroups);
    filterOpenSlots.addEventListener('change', filterGroups);
    filterValidity.addEventListener('change', filterGroups);

    // Clear all filters button
    clearFiltersBtn.addEventListener('click', function() {
        searchInput.value = '';
        filterTripType.value = '';
        filterWater.value = '';
        filterTent.value = '';
        filterOpenSlots.value = '';
        filterValidity.value = '';
        filterGroups();
    });

    // Clear search on Escape key
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            searchInput.value = '';
            filterGroups();
            searchInput.blur();
        }
    });
});


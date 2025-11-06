window.addEventListener('DOMContentLoaded', event => {
    // Initialize all tables with class 'datatables-table'
    const tables = document.querySelectorAll('.datatables-table');
    tables.forEach(table => {
        new simpleDatatables.DataTable(table);
    });

    // Search and filter functionality for groups
    const searchInput = document.getElementById('groupSearch');
    const clearSearchBtn = document.getElementById('clearSearch');
    const filterTripType = document.getElementById('filterTripType');
    const filterWater = document.getElementById('filterWater');
    const filterTent = document.getElementById('filterTent');
    const filterOpenSlots = document.getElementById('filterOpenSlots');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const groupBoxes = document.querySelectorAll('.group-box');

    // Function to filter groups based on search and filters
    function filterGroups() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const tripTypeFilter = filterTripType.value.toLowerCase();
        const waterFilter = filterWater.value;
        const tentFilter = filterTent.value;
        const openSlotsFilter = filterOpenSlots.value;

        // Show/hide clear search button
        clearSearchBtn.style.display = searchTerm ? 'block' : 'none';

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

            // Show or hide the box
            box.style.display = matches ? '' : 'none';
        });
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

    // Clear all filters button
    clearFiltersBtn.addEventListener('click', function() {
        searchInput.value = '';
        filterTripType.value = '';
        filterWater.value = '';
        filterTent.value = '';
        filterOpenSlots.value = '';
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


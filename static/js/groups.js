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
    const applyFiltersBtn = document.getElementById('applyFilters');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const filterToggle = document.getElementById('filterToggle');
    const filterModal = document.getElementById('filterModal');
    const closeFilterModal = document.getElementById('closeFilterModal');
    const groupBoxes = document.querySelectorAll('.group-box');

    // Track active filters
    let activeFilters = {
        tripType: '',
        water: '',
        tent: '',
        openSlots: '',
        validity: ''
    };

    // Modal functions
    function openFilterModal() {
        filterModal.style.display = 'flex';
        setTimeout(() => {
            filterModal.classList.add('show');
        }, 10);
        
        // Set current filter values in the modal
        filterTripType.value = activeFilters.tripType;
        filterWater.value = activeFilters.water;
        filterTent.value = activeFilters.tent;
        filterOpenSlots.value = activeFilters.openSlots;
        filterValidity.value = activeFilters.validity;
    }

    function closeFilterModalFunc() {
        filterModal.classList.remove('show');
        setTimeout(() => {
            filterModal.style.display = 'none';
        }, 300);
    }

    // Update filter button text based on active filters
    function updateFilterButtonText() {
        const activeCount = Object.values(activeFilters).filter(val => val !== '').length;
        
        if (activeCount > 0) {
            filterToggle.innerHTML = `<i class="fas fa-filter"></i><span class="badge bg-white text-primary ms-1" style="font-size: 0.7em;">${activeCount}</span>`;
            filterToggle.classList.remove('btn-outline-primary');
            filterToggle.classList.add('btn-primary');
            filterToggle.classList.add('text-white');
        } else {
            filterToggle.innerHTML = `<i class="fas fa-filter"></i>`;
            filterToggle.classList.remove('btn-primary', 'text-white');
            filterToggle.classList.add('btn-outline-primary');
        }
    }

    // Function to filter groups based on search and filters
    function filterGroups() {
        const searchTerm = searchInput.value.toLowerCase().trim();

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
            if (matches && activeFilters.tripType) {
                const tripType = box.getAttribute('data-trip-type') || '';
                if (tripType !== activeFilters.tripType) {
                    matches = false;
                }
            }

            // Water filter
            if (matches && activeFilters.water) {
                const water = box.getAttribute('data-water') || '';
                if (water !== activeFilters.water) {
                    matches = false;
                }
            }

            // Tent filter
            if (matches && activeFilters.tent) {
                const tent = box.getAttribute('data-tent') || '';
                if (tent !== activeFilters.tent) {
                    matches = false;
                }
            }

            // Open slots filter
            if (matches && activeFilters.openSlots) {
                const openSlots = box.getAttribute('data-open-slots') || '';
                if (openSlots !== activeFilters.openSlots) {
                    matches = false;
                }
            }

            // Validity filter
            if (matches && activeFilters.validity) {
                const valid = box.getAttribute('data-valid') || '';
                if (valid !== activeFilters.validity) {
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

    // Event listeners
    // Filter toggle button
    filterToggle.addEventListener('click', openFilterModal);
    
    // Close modal buttons
    closeFilterModal.addEventListener('click', closeFilterModalFunc);
    
    // Close modal when clicking outside
    filterModal.addEventListener('click', function(e) {
        if (e.target === filterModal) {
            closeFilterModalFunc();
        }
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && filterModal.classList.contains('show')) {
            closeFilterModalFunc();
        }
    });

    // Search input events (real-time search)
    searchInput.addEventListener('input', filterGroups);

    // Clear search button
    clearSearchBtn.addEventListener('click', function() {
        searchInput.value = '';
        filterGroups();
        searchInput.focus();
    });

    // Apply filters button
    applyFiltersBtn.addEventListener('click', function() {
        activeFilters.tripType = filterTripType.value.toLowerCase();
        activeFilters.water = filterWater.value;
        activeFilters.tent = filterTent.value;
        activeFilters.openSlots = filterOpenSlots.value;
        activeFilters.validity = filterValidity.value;
        
        updateFilterButtonText();
        filterGroups();
        closeFilterModalFunc();
    });

    // Reset filters button (in modal)
    resetFiltersBtn.addEventListener('click', function() {
        filterTripType.value = '';
        filterWater.value = '';
        filterTent.value = '';
        filterOpenSlots.value = '';
        filterValidity.value = '';
    });

    // Clear all filters button (main page)
    clearFiltersBtn.addEventListener('click', function() {
        searchInput.value = '';
        filterTripType.value = '';
        filterWater.value = '';
        filterTent.value = '';
        filterOpenSlots.value = '';
        filterValidity.value = '';
        
        activeFilters = {
            tripType: '',
            water: '',
            tent: '',
            openSlots: '',
            validity: ''
        };
        
        updateFilterButtonText();
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


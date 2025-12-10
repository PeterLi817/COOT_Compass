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

    // API Integration - Initialize API client
    setupAPIIntegration();

    // CSV Column Matching Script for Groups
    setupCSVMatching();

    // API Integration Script
    setupAPIIntegrationScript();
});

// API Integration Functions
function setupAPIIntegration() {
    // Test API connection when page loads
    if (window.cootAPI) {
        window.cootAPI.healthCheck().then(result => {
            console.log('API Status:', result.message);
        }).catch(error => {
            console.warn('API not available:', error);
        });
    }

    // Remove legacy confirm dialog and direct API call for sort button
    const sortButton = document.querySelector('button[data-bs-target="#confirmSortStudentsModal"]');
    // No custom click handler needed; let Bootstrap open the modal and handle via modal form

    // Override move student form submission
    const moveForm = document.querySelector('#moveStudentModal form');
    if (moveForm) {
        moveForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const studentId = document.getElementById('student_name').value;
            const tripId = document.getElementById('new_trip_id').value;

            if (studentId && tripId) {
                moveStudentWithAPI(studentId, tripId);
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('moveStudentModal'));
                if (modal) modal.hide();
            } else {
                showMessage('Please select both a student and a trip.', 'error');
            }
        });
    }

    // Override swap students form submission
    const swapForm = document.querySelector('#swapStudentsModal form');
    if (swapForm) {
        swapForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const student1Id = document.getElementById('student1_name').value;
            const student2Id = document.getElementById('student2_name').value;

            if (student1Id && student2Id) {
                if (student1Id === student2Id) {
                    showMessage('Please select two different students.', 'error');
                    return;
                }
                swapStudentsWithAPI(student1Id, student2Id);
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('swapStudentsModal'));
                if (modal) modal.hide();
            } else {
                showMessage('Please select both students.', 'error');
            }
        });
    }

    // --- Custom Sort Criteria Logic ---
    // Handler for the Sort Students modal (custom criteria)
    const sortModal = document.getElementById('confirmSortStudentsModal');
    if (sortModal) {
        const sortForm = sortModal.querySelector('form');
        if (sortForm) {
            sortForm.addEventListener('submit', function(e) {
                e.preventDefault();
                // Collect custom sort criteria from the modal
                const selects = sortForm.querySelectorAll('.sort-criteria-select');
                const criteria = [];
                const used = new Set();
                selects.forEach((sel, idx) => {
                    if (sel.value && !used.has(sel.value)) {
                        criteria.push({
                            type: sel.value,
                            priority: idx + 1
                        });
                        used.add(sel.value);
                    }
                });
                if (criteria.length < selects.length) {
                    alert('Please select a unique sort criterion for each priority.');
                    return;
                }

                // Show loading state
                showSortingLoadingState();

                // Use the global API client if available
                if (window.cootAPI && window.cootAPI.sortStudents) {
                    window.cootAPI.sortStudents(criteria)
                        .then(data => {
                            if (data.success) {
                                window.location.reload();
                            } else {
                                hideSortingLoadingState();
                                alert('Sort failed: ' + (data.message || 'Unknown error'));
                            }
                        })
                        .catch(err => {
                            hideSortingLoadingState();
                            alert('Sort failed: ' + err.message);
                        });
                } else {
                    // Fallback to direct fetch
                    fetch('/api/sort-students', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': (document.querySelector('input[name=csrf_token]') || {}).value || ''
                        },
                        body: JSON.stringify({ criteria })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            hideSortingLoadingState();
                            alert('Sort failed: ' + (data.message || 'Unknown error'));
                        }
                    })
                    .catch(err => {
                        hideSortingLoadingState();
                        alert('Sort failed: ' + err.message);
                    });
                }
            });
        }
    }
}

// Loading state functions for sort button
function showSortingLoadingState() {
    const sortBtn = document.getElementById('sortStudentsBtn');
    const sortBtnText = document.getElementById('sortBtnText');
    const modal = bootstrap.Modal.getInstance(document.getElementById('confirmSortStudentsModal'));

    if (sortBtn) {
        sortBtn.disabled = true;
        sortBtn.classList.add('disabled');
    }
    if (sortBtnText) {
        sortBtnText.textContent = 'Sorting...';
    }

    // Close the modal
    if (modal) {
        modal.hide();
    }
}

function hideSortingLoadingState() {
    const sortBtn = document.getElementById('sortStudentsBtn');
    const sortBtnText = document.getElementById('sortBtnText');

    if (sortBtn) {
        sortBtn.disabled = false;
        sortBtn.classList.remove('disabled');
    }
    if (sortBtnText) {
        sortBtnText.textContent = 'Sort Students';
    }
}

// CSV Column Matching Functions
function setupCSVMatching() {
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

    const csvFileInput = document.getElementById('csv_file');
    if (csvFileInput) {
        csvFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(event) {
                const text = event.target.result;
                parseCSV(text);
            };
            reader.readAsText(file);
        });
    }

    function parseCSV(text) {
        const lines = text.split('\n').filter(line => line.trim());
        if (lines.length === 0) return;

        // Parse CSV (handling quoted fields)
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
        if (!container) return;

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

            // Auto-match common column names
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
        actionLabel.textContent = 'Action';

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

        // Show the container and submit button
        const columnMatchingContainer = document.getElementById('columnMatchingContainer');
        const submitBtn = document.getElementById('submitBtn');
        if (columnMatchingContainer) columnMatchingContainer.style.display = 'block';
        if (submitBtn) submitBtn.style.display = 'inline-block';
    }

    // Handle form submission with AJAX
    const csvMatchingForm = document.getElementById('csvMatchingForm');
    if (csvMatchingForm) {
        csvMatchingForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const submitBtn = document.getElementById('submitBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Uploading...';
            }

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
                    // Close modal and reload page
                    const uploadCSVModal = document.getElementById('uploadCSVModal');
                    if (uploadCSVModal) {
                        const modal = bootstrap.Modal.getInstance(uploadCSVModal);
                        if (modal) modal.hide();
                    }
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.message || 'Failed to upload CSV'));
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Upload CSV';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error uploading CSV: ' + error.message);
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Upload CSV';
                }
            });
        });
    }

    // Reset modal when closed
    const uploadCSVModal = document.getElementById('uploadCSVModal');
    if (uploadCSVModal) {
        uploadCSVModal.addEventListener('hidden.bs.modal', function() {
            const csvFile = document.getElementById('csv_file');
            const columnMatchingContainer = document.getElementById('columnMatchingContainer');
            const submitBtn = document.getElementById('submitBtn');

            if (csvFile) csvFile.value = '';
            if (columnMatchingContainer) columnMatchingContainer.style.display = 'none';
            if (submitBtn) submitBtn.style.display = 'none';
        });
    }
}

// API Integration Script
function setupAPIIntegrationScript() {
    // Initialize API when page loads
    document.addEventListener('DOMContentLoaded', function() {
        // Test API connection
        if (window.cootAPI) {
            window.cootAPI.healthCheck().then(result => {
                console.log('✓ API Connected:', result.message);
            }).catch(error => {
                console.error('✗ API Connection Failed:', error);
            });
        }

        console.log('REST API Backend Available - Frontend-Backend Separation Complete');
    });
}


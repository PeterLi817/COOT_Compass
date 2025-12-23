$(document).ready(function() {
    // Store fetched users for filtering
    let allUsers = [];
    let usersDataTable = null;

    // Render users applying admin filter checkbox
    function renderUsers() {
        console.log('Rendering users with filter applied');

        // Destroy DataTable first if it exists
        if (usersDataTable) {
            try {
                usersDataTable.destroy();
                usersDataTable = null;
            } catch (e) {
                console.log('Error destroying datatable:', e);
            }
        }

        const tbody = $('#usersTableBody');
        tbody.empty();
        const onlyAdmins = $('#adminFilterCheckbox').is(':checked');
        const toRender = onlyAdmins ? allUsers.filter(u => u.role === 'admin' || u.role === 'admin_manager') : allUsers;
        console.log('Filtered users count:', toRender.length, 'Total users:', allUsers.length);

        toRender.forEach(user => {
            const roleClass = user.role === 'admin_manager' ? 'bg-danger text-white' :
                             user.role === 'admin' ? 'bg-info text-dark' :
                             user.role === 'student' ? 'bg-success text-white' : 'bg-secondary text-white';
            const displayRole = user.role ? user.role.replace('_', ' ') : 'No role';
            const row = `
                <tr data-role="${user.role || 'none'}">
                    <td>${user.email}</td>
                    <td>${user.first_name}</td>
                    <td>${user.last_name}</td>
                    <td><span class="badge ${roleClass}">${displayRole}</span></td>
                    <td>
                        <button type="button" class="btn btn-sm btn-link p-0 me-2 edit-user-btn" title="Edit"
                            data-email="${user.email}" data-firstname="${user.first_name}" data-lastname="${user.last_name}" data-role="${user.role || 'None'}">
                            <i class="fas fa-pen-to-square"></i>
                        </button>
                    </td>
                </tr>`;
            tbody.append(row);
        });

        // Re-init DataTable with fresh data
        const datatablesSimple = document.getElementById('datatablesSimple');
        if (datatablesSimple) {
            usersDataTable = new simpleDatatables.DataTable(datatablesSimple);
        }
    }

    // Check if user has manager permissions
    const userRole = $('#userRole').data('role');
    const isManager = userRole === 'admin_manager';

    // Handle Edit Access Permissions button click
    $('#editPermissionsBtn').on('click', function(e) {
        e.preventDefault();

        if (!isManager) {
            // Show permission denied modal
            $('#permissionDeniedModal').modal('show');
        } else {
            // If manager, show users modal
            // Reset modal state
            $('#usersLoadingSpinner').show();
            $('#usersTableContainer').hide();
            $('#usersErrorMessage').hide();
            $('#usersTableBody').empty();

            // Show the modal
            $('#viewUsersModal').modal('show');

            // Fetch users from the backend
            fetch('/api/get-users')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch users');
                    }
                    return response.json();
                })
                .then(data => {
                    // Hide loading spinner
                    $('#usersLoadingSpinner').hide();

                    if (data.users && data.users.length > 0) {
                        allUsers = data.users;
                        $('#adminFilterContainer').show();
                        $('#usersTableContainer').show();
                        renderUsers();
                    } else {
                        // No users found
                        $('#usersErrorText').text('No users found.');
                        $('#usersErrorMessage').removeClass('alert-danger').addClass('alert-info');
                        $('#usersErrorMessage').show();
                    }
                })
                .catch(error => {
                    console.error('Error fetching users:', error);
                    $('#usersLoadingSpinner').hide();
                    $('#usersErrorText').text('Failed to load users. Please try again.');
                    $('#usersErrorMessage').show();
                });
        }
    });

    // Handle Clear Databases button click
    $('#clearDatabaseBtn').on('click', function(e) {
        e.preventDefault();

        if (!isManager) {
            // Show permission denied modal
            $('#permissionDeniedModal').modal('show');
        } else {
            // If manager, show confirmation modal and reset input
            $('#confirmTextInput').val('');
            $('#confirmClearDB').prop('disabled', true);
            $('#confirmClearDBModal').modal('show');
        }
    });

    // Handle input validation for Clear DB confirmation
    $('#confirmTextInput').on('keyup', function() {
        const inputValue = $(this).val();
        if (inputValue.toUpperCase() === 'CONFIRM') {
            $('#confirmClearDB').prop('disabled', false);
        } else {
            $('#confirmClearDB').prop('disabled', true);
        }
    });

    // Handle Clear DB confirmation
    $('#confirmClearDB').on('click', function() {
        const inputValue = $('#confirmTextInput').val();
        if (inputValue.toUpperCase() === 'CONFIRM') {
            // Use form submission to properly preserve flash messages on redirect
            const form = $('<form>', {
                'method': 'POST',
                'action': '/clear-databases'
            });
            $('body').append(form);
            form.submit();
        }
    });

    // Handle Edit User button click (delegated event for dynamically added buttons)
    $(document).on('click', '.edit-user-btn', function() {
        const email = $(this).data('email');
        const firstName = $(this).data('firstname');
        const lastName = $(this).data('lastname');
        const role = $(this).data('role');

        // Populate the modal
        $('#editUserName').text(`${firstName} ${lastName}`);
        $('#editUserEmail').text(email);
        $('#roleSelect').val(role === 'None' || !role ? 'none' : role);

        // Store email in the save button for later use
        $('#saveRoleBtn').data('email', email);

        // Show the modal
        $('#editUserRoleModal').modal('show');
    });

    // Handle Save Role button click
    $('#saveRoleBtn').on('click', function() {
        const email = $(this).data('email');
        const newRole = $('#roleSelect').val();

        // Send update request to backend
        fetch('/api/update-user-role', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                role: newRole
            })
        })
        .then(response => response.json())
        .then(data => {
            // Redirect to settings page to show flash message
            window.location.href = '/settings';
        })
        .catch(error => {
            console.error('Error updating user role:', error);
            window.location.href = '/settings';
        });
    });

    // Admin filter checkbox change
    $(document).on('change', '#adminFilterCheckbox', function() {
        console.log('Admin filter checkbox changed');
        renderUsers();
    });

    // Handle Toggle Trip Visibility button click
    $('#toggleTripsVisibilityBtn').on('click', function(e) {
        e.preventDefault();

        if (!isManager) {
            // Show permission denied modal
            $('#permissionDeniedModal').modal('show');
        } else {
            // Show the toggle trips visibility modal
            $('#toggleTripsVisibilityModal').modal('show');
        }
    });

    // Show Trips switch handling
    const $showTripsSwitch = $('#showTripsSwitch');

    if ($showTripsSwitch.length) {
        // Initialize switch state from backend when modal is shown
        $('#toggleTripsVisibilityModal').on('show.bs.modal', function() {
            fetch('/api/settings/show_trips')
                .then(resp => resp.json())
                .then(data => {
                    const isOn = !!data.show_trips_to_students;
                    $showTripsSwitch.prop('checked', isOn);
                    $showTripsSwitch.attr('aria-checked', !!isOn);
                })
                .catch(err => {
                    console.error('Error fetching show_trips setting:', err);
                });
        });

        // Toggle handler
        $showTripsSwitch.on('change', function() {
            const checked = $(this).is(':checked');

            fetch('/api/settings/toggle_show_trips', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value: checked })
            })
            .then(resp => resp.json())
            .then(data => {
                if (!data.success) {
                    // Revert on failure
                    $showTripsSwitch.prop('checked', !checked);
                    alert('Failed to save setting');
                    return;
                }
                $showTripsSwitch.attr('aria-checked', !!data.show_trips_to_students);
            })
            .catch(err => {
                console.error('Error toggling show_trips setting:', err);
                $showTripsSwitch.prop('checked', !checked);
                alert('Network error saving setting');
            });
        });
    }
});

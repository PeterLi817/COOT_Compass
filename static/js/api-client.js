// REST API client for COOT Compass with dynamic updates
class COOTAPI {
    constructor() {
        this.baseURL = '/api';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // API methods
    async getStudents() {
        return this.request('/students');
    }

    async getTrips() {
        return this.request('/trips');
    }

    async moveStudent(studentId, newTripId) {
        return this.request('/move-student', {
            method: 'POST',
            body: JSON.stringify({
                student_id: studentId,
                new_trip_id: newTripId
            })
        });
    }

    async swapStudents(student1Id, student2Id) {
        return this.request('/swap-students', {
            method: 'POST',
            body: JSON.stringify({
                student1_id: student1Id,
                student2_id: student2Id
            })
        });
    }

    async sortStudents() {
        return this.request('/sort-students', {
            method: 'POST'
        });
    }

    async healthCheck() {
        return this.request('/health');
    }
}

// Make API available globally
window.cootAPI = new COOTAPI();

// Simple message display without loading spinners
function showMessage(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert after the main title
    const title = document.querySelector('h1');
    if (title) {
        title.insertAdjacentHTML('afterend', alertHTML);
    }
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) alert.remove();
    }, 3000);
}

// API-powered functions with dynamic updates (no page reload)
async function sortStudentsWithAPI() {
    try {
        const result = await window.cootAPI.sortStudents();
        showMessage(result.message);
        
        // Dynamically refresh the groups display
        await refreshGroupsDisplay();
        
    } catch (error) {
        showMessage(`Sort failed: ${error.message}`, 'error');
    }
}

async function moveStudentWithAPI(studentId, newTripId) {
    try {
        const result = await window.cootAPI.moveStudent(studentId, newTripId);
        showMessage(result.message);
        
        // Dynamically refresh the groups display
        await refreshGroupsDisplay();
        
    } catch (error) {
        showMessage(`Move failed: ${error.message}`, 'error');
    }
}

async function swapStudentsWithAPI(student1Id, student2Id) {
    try {
        const result = await window.cootAPI.swapStudents(student1Id, student2Id);
        showMessage(result.message);
        
        // Dynamically refresh the groups display
        await refreshGroupsDisplay();
        
    } catch (error) {
        showMessage(`Swap failed: ${error.message}`, 'error');
    }
}

// Helper function to dynamically refresh the groups display without page reload
async function refreshGroupsDisplay() {
    try {
        const response = await fetch(window.location.href, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const html = await response.text();
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');
            
            // Find the groups list container
            const newGroupsList = newDoc.querySelector('.groups-list');
            const currentGroupsList = document.querySelector('.groups-list');
            
            if (newGroupsList && currentGroupsList) {
                // Replace the content but preserve event listeners by re-initializing
                currentGroupsList.innerHTML = newGroupsList.innerHTML;
                
                // Re-initialize any JavaScript functionality for the new content
                reinitializeGroupsEventListeners();
            }
        }
    } catch (error) {
        console.error('Failed to refresh groups display:', error);
        // Fallback to page reload if dynamic update fails
        showMessage('Refreshing page to show updated groups...', 'success');
        setTimeout(() => location.reload(), 1000);
    }
}

// Helper function to re-initialize event listeners after dynamic content update
function reinitializeGroupsEventListeners() {
    // Re-initialize DataTables for any new student tables
    const tables = document.querySelectorAll('.datatables-table');
    tables.forEach(table => {
        if (!table.classList.contains('dataTable')) {
            // Only initialize if not already initialized
            try {
                new simpleDatatables.DataTable(table, {
                    searchable: true,
                    sortable: true,
                    fixedHeight: false,
                    perPage: 50
                });
            } catch (e) {
                console.warn('Could not initialize DataTable:', e);
            }
        }
    });
    
    // Re-apply any other event listeners that might be needed
    // This would include move/swap form handlers if they're not already set up globally
}

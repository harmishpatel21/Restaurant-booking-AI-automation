document.addEventListener('DOMContentLoaded', function() {
    // Initialize date range pickers
    const bookingDateFilter = document.getElementById('booking-date-filter');
    if (bookingDateFilter) {
        flatpickr(bookingDateFilter, {
            mode: 'range',
            dateFormat: 'Y-m-d',
            onChange: function(selectedDates, dateStr) {
                if (selectedDates.length === 2) {
                    filterBookings();
                }
            }
        });
    }
    
    // Event listeners for filters
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterBookings);
    }
    
    // Booking action buttons (confirm, cancel, etc.)
    document.querySelectorAll('.booking-action').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.dataset.action;
            const bookingId = this.dataset.id;
            
            if (action && bookingId) {
                updateBookingStatus(bookingId, action);
            }
        });
    });
    
    // Export to CSV functionality
    const exportCsvBtn = document.getElementById('export-csv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            window.location.href = '/dashboard/export-csv';
        });
    }
    
    // Chart initialization (if chart canvas exists)
    const bookingStatsChart = document.getElementById('booking-stats-chart');
    if (bookingStatsChart) {
        initializeBookingStatsChart();
    }
    
    // Export audit logs to CSV
    const exportAuditLogsBtn = document.getElementById('export-audit-logs');
    if (exportAuditLogsBtn) {
        exportAuditLogsBtn.addEventListener('click', function() {
            window.location.href = '/dashboard/export-audit-logs';
        });
    }
    
    // Filter audit logs by action
    const auditActionFilter = document.getElementById('audit-action-filter');
    if (auditActionFilter) {
        auditActionFilter.addEventListener('change', filterAuditLogs);
    }
    
    // Filter audit logs by date
    const auditDateFilter = document.getElementById('audit-date-filter');
    if (auditDateFilter) {
        flatpickr(auditDateFilter, {
            mode: 'range',
            dateFormat: 'Y-m-d',
            onChange: function(selectedDates, dateStr) {
                if (selectedDates.length === 2) {
                    filterAuditLogs();
                }
            }
        });
    }
    
    // Functions
    function filterBookings() {
        const statusValue = statusFilter ? statusFilter.value : '';
        const dateRange = bookingDateFilter && bookingDateFilter._flatpickr ? 
                        bookingDateFilter._flatpickr.selectedDates : [];
        
        let params = new URLSearchParams();
        if (statusValue) {
            params.append('status', statusValue);
        }
        
        if (dateRange.length === 2) {
            params.append('start_date', formatDate(dateRange[0]));
            params.append('end_date', formatDate(dateRange[1]));
        }
        
        // Reload page with filters
        window.location.href = '/dashboard?' + params.toString();
    }
    
    function filterAuditLogs() {
        const actionValue = auditActionFilter ? auditActionFilter.value : '';
        const dateRange = auditDateFilter && auditDateFilter._flatpickr ? 
                        auditDateFilter._flatpickr.selectedDates : [];
        
        let params = new URLSearchParams();
        if (actionValue) {
            params.append('action', actionValue);
        }
        
        if (dateRange.length === 2) {
            params.append('start_date', formatDate(dateRange[0]));
            params.append('end_date', formatDate(dateRange[1]));
        }
        
        // Reload page with filters
        window.location.href = '/dashboard/audit-logs?' + params.toString();
    }
    
    function updateBookingStatus(bookingId, action) {
        const url = `/booking/${action}/${bookingId}`;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Reload the page to show updated data
                window.location.reload();
            } else {
                showAlert('danger', data.message || 'Failed to update booking');
            }
        })
        .catch(error => {
            showAlert('danger', 'Error updating booking: ' + error.message);
            console.error('Error updating booking:', error);
        });
    }
    
    function initializeBookingStatsChart() {
        fetch('/dashboard/booking-stats')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const ctx = bookingStatsChart.getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Bookings per day',
                            data: data.values,
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    precision: 0
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error loading booking stats:', error);
            });
    }
    
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    function showAlert(type, message) {
        const alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertsContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alertsContainer.removeChild(alert);
            }, 150);
        }, 5000);
    }
});

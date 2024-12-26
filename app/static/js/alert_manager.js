class AlertManager {
    constructor() {
        this.alertContainer = document.querySelector('.alert-container');
        this.setupEventListeners();
        this.alertRefreshInterval = 30000; // 30 seconds
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Setup filter handlers
        document.getElementById('severityFilter').addEventListener('change', (e) => {
            this.filterAlerts({ severity: e.target.value });
        });

        document.getElementById('searchFilter').addEventListener('input', (e) => {
            this.filterAlerts({ search: e.target.value });
        });
    }

    async fetchAlerts() {
        try {
            const response = await fetch('/api/v1/alerts');
            if (!response.ok) throw new Error('Failed to fetch alerts');
            const alerts = await response.json();
            this.renderAlerts(alerts);
        } catch (error) {
            console.error('Error fetching alerts:', error);
            showAlert('Failed to fetch alerts', 'error');
        }
    }

    async acknowledgeAlert(alertId) {
        try {
            const response = await fetch(`/api/v1/alerts/${alertId}/acknowledge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) throw new Error('Failed to acknowledge alert');
            
            const alertElement = document.querySelector(`[data-alert-id="${alertId}"]`);
            alertElement.classList.add('acknowledged');
            showAlert('Alert acknowledged', 'success');
        } catch (error) {
            console.error('Error acknowledging alert:', error);
            showAlert('Failed to acknowledge alert', 'error');
        }
    }

    filterAlerts(filters) {
        const alerts = document.querySelectorAll('.alert-item');
        alerts.forEach(alert => {
            let visible = true;
            
            if (filters.severity && alert.dataset.severity !== filters.severity) {
                visible = false;
            }
            
            if (filters.search) {
                const searchText = filters.search.toLowerCase();
                const alertText = alert.textContent.toLowerCase();
                if (!alertText.includes(searchText)) {
                    visible = false;
                }
            }
            
            alert.style.display = visible ? 'block' : 'none';
        });
    }

    startAutoRefresh() {
        setInterval(() => this.fetchAlerts(), this.alertRefreshInterval);
    }
} 
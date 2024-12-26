// Global Accessibility Enhancements
document.addEventListener('DOMContentLoaded', () => {
    initAccessibilityFeatures();
});

function initAccessibilityFeatures() {
    handleKeyboardNavigation();
    enhanceFormAccessibility();
    setupLiveRegions();
    initModalAccessibility();
}

// Keyboard Navigation
function handleKeyboardNavigation() {
    // Add visible focus indicators
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });

    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });
}

// Form Accessibility
function enhanceFormAccessibility() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add error handling
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                announceFormErrors();
            }
        });

        // Add aria-invalid when validation fails
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('invalid', () => {
                input.setAttribute('aria-invalid', 'true');
            });
            
            input.addEventListener('input', () => {
                input.setAttribute('aria-invalid', 'false');
            });
        });
    });
}

// Live Regions
function setupLiveRegions() {
    // Create status message region if it doesn't exist
    if (!document.getElementById('status-messages')) {
        const statusRegion = document.createElement('div');
        statusRegion.id = 'status-messages';
        statusRegion.setAttribute('role', 'status');
        statusRegion.setAttribute('aria-live', 'polite');
        statusRegion.className = 'visually-hidden';
        document.body.appendChild(statusRegion);
    }
}

// Modal Accessibility
function initModalAccessibility() {
    const modals = document.querySelectorAll('dialog');
    
    modals.forEach(modal => {
        setupModalFocusTrap(modal);
        setupModalKeyboardControls(modal);
    });
}

// Helper Functions
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required], [aria-required="true"]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.setAttribute('aria-invalid', 'true');
        }
    });
    
    return isValid;
}

function announceFormErrors() {
    const errorFields = document.querySelectorAll('[aria-invalid="true"]');
    if (errorFields.length > 0) {
        const errorMessage = `${errorFields.length} form fields require attention. Please review the form.`;
        showAlert(errorMessage, 'error');
    }
}

function showAlert(message, type = 'info') {
    const statusContainer = document.getElementById('status-messages');
    statusContainer.textContent = message;
    statusContainer.className = `alert alert-${type}`;
    
    // Clear message after 5 seconds
    setTimeout(() => {
        statusContainer.textContent = '';
        statusContainer.className = 'visually-hidden';
    }, 5000);
} 
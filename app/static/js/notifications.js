// Notification Management
function saveNotificationSettings(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    fetch('/api/v1/notifications/settings', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('Settings saved successfully');
        }
    })
    .catch(error => showAlert('Error saving settings', 'error'));
}

function testTelegramConnection() {
    fetch('/api/v1/notifications/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            channel: 'telegram'
        })
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.status === 'success' ? 
                 'Test message sent successfully' : 
                 'Failed to send test message');
    });
}

function addNewRule() {
    // Show rule creation modal
    const modal = document.getElementById('ruleModal');
    modal.style.display = 'block';
}

function editRule(ruleId) {
    fetch(`/api/v1/notifications/rules/${ruleId}`)
        .then(response => response.json())
        .then(rule => {
            // Populate and show edit modal
            populateRuleForm(rule);
        });
}

function deleteRule(ruleId) {
    if (confirm('Are you sure you want to delete this rule?')) {
        fetch(`/api/v1/notifications/rules/${ruleId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.querySelector(`[data-rule-id="${ruleId}"]`).remove();
            }
        });
    }
}

// Add keyboard support and ARIA updates
function initAccessibility() {
    // Handle modal focus trap
    const modal = document.getElementById('ruleModal');
    const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    modal.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
        
        if (e.key === 'Tab') {
            const firstFocusable = focusableElements[0];
            const lastFocusable = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey && document.activeElement === firstFocusable) {
                e.preventDefault();
                lastFocusable.focus();
            } else if (!e.shiftKey && document.activeElement === lastFocusable) {
                e.preventDefault();
                firstFocusable.focus();
            }
        }
    });
}

// Enhanced status messages
function showAlert(message, type = 'success') {
    const statusContainer = document.getElementById('status-messages');
    statusContainer.textContent = message;
    statusContainer.className = `alert alert-${type}`;
    
    // Clear message after 5 seconds
    setTimeout(() => {
        statusContainer.textContent = '';
        statusContainer.className = 'visually-hidden';
    }, 5000);
}

// Form validation with accessibility
function validateForm(form) {
    const errors = [];
    const requiredFields = form.querySelectorAll('[aria-required="true"]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            const label = document.querySelector(`label[for="${field.id}"]`).textContent;
            errors.push(`${label} is required`);
            field.setAttribute('aria-invalid', 'true');
        } else {
            field.setAttribute('aria-invalid', 'false');
        }
    });
    
    if (errors.length > 0) {
        const errorList = document.createElement('ul');
        errorList.setAttribute('role', 'alert');
        errorList.setAttribute('aria-label', 'Form errors');
        
        errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            errorList.appendChild(li);
        });
        
        const errorContainer = document.getElementById('form-errors');
        errorContainer.innerHTML = '';
        errorContainer.appendChild(errorList);
        return false;
    }
    
    return true;
} 
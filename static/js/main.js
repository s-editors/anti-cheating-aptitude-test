// Main JavaScript for Aptitude Test Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    initBootstrapComponents();
    
    // Auto-dismiss alerts after 5 seconds
    autoDismissAlerts();
    
    // Initialize password strength meter if present
    initPasswordStrengthMeter();
});

// Initialize Bootstrap components
function initBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Auto-dismiss alerts
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    
    alerts.forEach(function(alert) {
        // Skip alerts with data-auto-dismiss="false"
        if (alert.dataset.autoDismiss === 'false') return;
        
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Password strength meter
function initPasswordStrengthMeter() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;
    
    const strengthBar = document.getElementById('password-strength');
    const strengthFeedback = document.getElementById('password-feedback');
    
    if (!strengthBar || !strengthFeedback) return;
    
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        let strength = 0;
        
        if (password.length >= 8) strength += 25;
        if (password.match(/[a-z]+/)) strength += 25;
        if (password.match(/[A-Z]+/)) strength += 25;
        if (password.match(/[0-9]+/) || password.match(/[^a-zA-Z0-9]+/)) strength += 25;
        
        strengthBar.style.width = strength + '%';
        strengthBar.setAttribute('aria-valuenow', strength);
        
        if (strength < 25) {
            strengthBar.className = 'progress-bar bg-danger';
            strengthFeedback.textContent = 'Very Weak';
            strengthFeedback.className = 'form-text text-danger';
        } else if (strength < 50) {
            strengthBar.className = 'progress-bar bg-warning';
            strengthFeedback.textContent = 'Weak';
            strengthFeedback.className = 'form-text text-warning';
        } else if (strength < 75) {
            strengthBar.className = 'progress-bar bg-info';
            strengthFeedback.textContent = 'Moderate';
            strengthFeedback.className = 'form-text text-info';
        } else {
            strengthBar.className = 'progress-bar bg-success';
            strengthFeedback.textContent = 'Strong';
            strengthFeedback.className = 'form-text text-success';
        }
    });
}

// Global anti-cheating functions
function recordWarning(testId, warningType, warningCount) {
    // Send warning to server
    fetch('/record_warning', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            test_id: testId,
            warning_type: warningType,
            warning_count: warningCount
        }),
    });
}

function displayWarning(container, message, warningCount, maxWarnings) {
    // Create warning message
    const warningElement = document.createElement('div');
    warningElement.className = 'alert alert-danger alert-dismissible fade show';
    warningElement.innerHTML = `
        <strong>Warning ${warningCount}/${maxWarnings}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    container.appendChild(warningElement);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(warningElement);
        bsAlert.close();
    }, 5000);
}
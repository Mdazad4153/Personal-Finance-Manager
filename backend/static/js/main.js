// Main JavaScript file for enhanced functionality

// Initialize all tooltips
document.addEventListener('DOMContentLoaded', function() {
    'use strict'
    
    // Fetch all forms that need validation
    var forms = document.querySelectorAll('.needs-validation')
    
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    })
    
    // Password visibility toggle
    var passwordToggles = document.querySelectorAll('[data-toggle="password"]')
    Array.prototype.slice.call(passwordToggles).forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            var target = document.querySelector(this.dataset.target)
            if (target.type === 'password') {
                target.type = 'text'
                this.querySelector('i').classList.remove('fa-eye')
                this.querySelector('i').classList.add('fa-eye-slash')
            } else {
                target.type = 'password'
                this.querySelector('i').classList.remove('fa-eye-slash')
                this.querySelector('i').classList.add('fa-eye')
            }
        })
    })
    
    // Password strength checker
    var passwordInputs = document.querySelectorAll('[data-password-strength]')
    Array.prototype.slice.call(passwordInputs).forEach(function(input) {
        input.addEventListener('input', function() {
            var strength = 0
            var value = this.value
            
            if (value.length >= 8) strength++
            if (value.match(/[a-z]+/)) strength++
            if (value.match(/[A-Z]+/)) strength++
            if (value.match(/[0-9]+/)) strength++
            if (value.match(/[$@#&!]+/)) strength++
            
            var strengthBar = document.querySelector(this.dataset.passwordStrength)
            if (strengthBar) {
                switch (strength) {
                    case 0:
                        strengthBar.innerHTML = ''
                        break
                    case 1:
                        strengthBar.innerHTML = '<div class="progress"><div class="progress-bar bg-danger" style="width: 20%">Very Weak</div></div>'
                        break
                    case 2:
                        strengthBar.innerHTML = '<div class="progress"><div class="progress-bar bg-warning" style="width: 40%">Weak</div></div>'
                        break
                    case 3:
                        strengthBar.innerHTML = '<div class="progress"><div class="progress-bar bg-info" style="width: 60%">Medium</div></div>'
                        break
                    case 4:
                        strengthBar.innerHTML = '<div class="progress"><div class="progress-bar bg-primary" style="width: 80%">Strong</div></div>'
                        break
                    case 5:
                        strengthBar.innerHTML = '<div class="progress"><div class="progress-bar bg-success" style="width: 100%">Very Strong</div></div>'
                        break
                }
            }
        })
    })
    
    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)')
    Array.prototype.slice.call(alerts).forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert)
            bsAlert.close()
        }, 5000)
    })
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    })
    
    // Add animation class to elements with data-animate attribute
    var animatedElements = document.querySelectorAll('[data-animate]')
    Array.prototype.slice.call(animatedElements).forEach(function(element) {
        element.classList.add('animate__animated')
        element.classList.add('animate__' + element.dataset.animate)
    })
    
    // Add animation classes to elements
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('animate-slide');
    });

    // Initialize all charts if they exist
    initializeCharts();
});

// Function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Function to format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Function to format percentage
function formatPercentage(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

// Function to initialize charts
function initializeCharts() {
    // Expense by Category Chart
    const expenseCategoryChart = document.getElementById('expenseCategoryChart');
    if (expenseCategoryChart) {
        new Chart(expenseCategoryChart, {
            type: 'doughnut',
            data: expenseCategoryData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // Income vs Expense Chart
    const incomeExpenseChart = document.getElementById('incomeExpenseChart');
    if (incomeExpenseChart) {
        new Chart(incomeExpenseChart, {
            type: 'bar',
            data: incomeExpenseData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Function to confirm delete
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Function to copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!');
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
    });
}

// Function to show toast notification
function showToast(message, type = 'success') {
    var toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    var container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }

    container.appendChild(toast);
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Function to handle file upload preview
function handleFileUpload(input, previewElement) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function(e) {
            if (previewElement.tagName === 'IMG') {
                previewElement.src = e.target.result;
            } else {
                previewElement.style.backgroundImage = `url(${e.target.result})`;
            }
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// Function to export table to CSV
function exportTableToCSV(tableId, filename) {
    var table = document.getElementById(tableId);
    var rows = table.querySelectorAll('tr');
    var csv = [];

    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll('td, th');

        for (var j = 0; j < cols.length; j++) {
            var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            data = data.replace(/"/g, '""');
            row.push('"' + data + '"');
        }

        csv.push(row.join(','));
    }

    var csvFile = new Blob([csv.join('\n')], {type: 'text/csv'});
    var downloadLink = document.createElement('a');

    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Add loading animation
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-overlay';
    loadingDiv.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    const loadingDiv = document.querySelector('.loading-overlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    form.querySelectorAll('input[required], select[required]').forEach(input => {
        if (!input.value) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Add transaction form handling
const transactionForm = document.getElementById('transactionForm');
if (transactionForm) {
    transactionForm.addEventListener('submit', function(e) {
        if (!validateForm('transactionForm')) {
            e.preventDefault();
            return false;
        }
        showLoading();
    });
}

// Add loan form handling
const loanForm = document.getElementById('loanForm');
if (loanForm) {
    loanForm.addEventListener('submit', function(e) {
        if (!validateForm('loanForm')) {
            e.preventDefault();
            return false;
        }
        showLoading();
    });
}

// Dark mode toggle
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Check for saved dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

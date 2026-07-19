// Credit Risk Prediction System - Main JavaScript File (Upgraded)

// Theme Toggler Logic (Dark/Light mode persistence)
document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("themeToggleBtn");
    
    // Check local storage or system preferences
    if (localStorage.getItem("theme") === "dark" || 
        (!localStorage.getItem("theme") && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
        document.documentElement.classList.add("dark");
        if (themeToggle) themeToggle.checked = true;
    } else {
        document.documentElement.classList.remove("dark");
        if (themeToggle) themeToggle.checked = false;
    }

    if (themeToggle) {
        themeToggle.addEventListener("change", function () {
            if (this.checked) {
                document.documentElement.classList.add("dark");
                localStorage.setItem("theme", "dark");
                showToast("Theme switched to Dark Mode", "info");
            } else {
                document.documentElement.classList.remove("dark");
                localStorage.setItem("theme", "light");
                showToast("Theme switched to Light Mode", "info");
            }
        });
    }
});

// Collapsible Mobile Sidebar Toggle
function toggleSidebar() {
    const sidebar = document.getElementById("sidebarPanel");
    if (sidebar) {
        sidebar.classList.toggle("show");
    }
}

// ----------------------------------------------------
// Toast Notification Class System
// ----------------------------------------------------
function showToast(message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container-custom";
        document.body.appendChild(container);
    }
    
    const toast = document.createElement("div");
    toast.className = `toast-custom toast-custom-${type}`;
    
    let iconClass = "bi-info-circle-fill";
    if (type === "success") iconClass = "bi-check-circle-fill text-success";
    if (type === "danger") iconClass = "bi-exclamation-triangle-fill text-danger";
    if (type === "warning") iconClass = "bi-exclamation-circle-fill text-warning";
    
    toast.innerHTML = `
        <i class="bi ${iconClass}"></i>
        <div>${message}</div>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.classList.add("fade-out");
        toast.addEventListener("animationend", () => {
            toast.remove();
        });
    }, 4000);
}

// ----------------------------------------------------
// Quick Autofill Profiles Mappings
// ----------------------------------------------------
const mockProfiles = {
    low: {
        applicant_name: "Jane Harrison", age: 42, gender: "Female", annual_income: 98000,
        years_employment: 12, education: "Master", marital_status: "Married",
        loan_amount: 15000, loan_purpose: "Home Improvement", interest_rate: 5.5,
        loan_term: 36, credit_score: 810, dti: 0.12, existing_loans: 0,
        credit_cards: 4, previous_defaults: 0, savings_balance: 45000,
        monthly_expenses: 2200, property_ownership: "Own", dependents: 1
    },
    medium: {
        applicant_name: "Marcus Brody", age: 29, gender: "Male", annual_income: 54000,
        years_employment: 3.5, education: "Bachelor", marital_status: "Single",
        loan_amount: 20000, loan_purpose: "Debt Consolidation", interest_rate: 12.5,
        loan_term: 60, credit_score: 640, dti: 0.36, existing_loans: 1,
        credit_cards: 5, previous_defaults: 0, savings_balance: 3500,
        monthly_expenses: 1600, property_ownership: "Rent", dependents: 0
    },
    high: {
        applicant_name: "Victor Vance", age: 36, gender: "Male", annual_income: 28000,
        years_employment: 0.5, education: "High School", marital_status: "Divorced",
        loan_amount: 40000, loan_purpose: "Business", interest_rate: 21.0,
        loan_term: 60, credit_score: 480, dti: 0.62, existing_loans: 3,
        credit_cards: 8, previous_defaults: 2, savings_balance: 200,
        monthly_expenses: 2100, property_ownership: "Rent", dependents: 3
    }
};

function autofillForm(profileKey) {
    const profile = mockProfiles[profileKey];
    if (!profile) return;
    
    Object.keys(profile).forEach(key => {
        const input = document.getElementById(key) || document.getElementsByName(key)[0];
        if (input) {
            input.value = profile[key];
            input.dispatchEvent(new Event('change'));
        }
    });
    showToast(`Autofilled profile: ${profile.applicant_name}`, "success");
}

// ----------------------------------------------------
// History Log Actions & Verification Popups
// ----------------------------------------------------
function deleteRecord(id, rowElementId) {
    if (!confirm("Are you sure you want to permanently delete this prediction record?")) return;
    
    fetch(`/history/delete/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast("Record successfully deleted", "success");
                const row = document.getElementById(rowElementId);
                if (row) {
                    row.style.transition = "all 0.5s ease";
                    row.style.opacity = 0;
                    row.style.transform = "translateX(-20px)";
                    setTimeout(() => row.remove(), 500);
                }
            } else {
                showToast(data.message || "Failed to delete record", "danger");
            }
        })
        .catch(err => {
            showToast("Failed to connect to server", "danger");
            console.error(err);
        });
}

function viewRecordDetails(id) {
    fetch(`/history/details/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modalBody = document.getElementById("detailsModalBody");
                const d = data.data;
                
                // Format values for UI readability
                const riskBadge = d.risk_level === 'Low Risk' ? 'badge-risk-low' : (d.risk_level === 'Medium Risk' ? 'badge-risk-medium' : 'badge-risk-high');
                const recColor = d.recommendation === 'Approve' ? 'text-success' : (d.recommendation === 'Manual Review' ? 'text-warning' : 'text-danger');
                
                modalBody.innerHTML = `
                    <div class="row g-3">
                        <div class="col-md-6">
                            <small class="text-muted d-block">APPLICANT NAME</small>
                            <strong class="fs-5">${d.applicant_name}</strong>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <small class="text-muted d-block">ASSESSMENT DATE</small>
                            <strong>${d.prediction_date}</strong>
                        </div>
                        <hr class="my-2 border-secondary border-opacity-10">
                        <div class="col-6 col-md-3">
                            <small class="text-muted d-block">RISK LEVEL</small>
                            <span class="badge-custom ${riskBadge}">${d.risk_level}</span>
                        </div>
                        <div class="col-6 col-md-3">
                            <small class="text-muted d-block">RECOMMENDATION</small>
                            <strong class="${recColor}">${d.recommendation}</strong>
                        </div>
                        <div class="col-6 col-md-3">
                            <small class="text-muted d-block">DEFAULT PROBABILITY</small>
                            <strong class="text-danger">${d.default_probability}%</strong>
                        </div>
                        <div class="col-6 col-md-3">
                            <small class="text-muted d-block">MODEL USED</small>
                            <span class="badge bg-secondary bg-opacity-10 text-secondary">${d.model_used.toUpperCase().replace('_', ' ')}</span>
                        </div>
                        <hr class="my-2 border-secondary border-opacity-10">
                        <div class="col-md-6">
                            <h6 class="text-primary mb-2">Financial Ratios</h6>
                            <ul class="list-group list-group-flush small" style="background:transparent;">
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Annual Income:</span><strong>$${d.annual_income.toLocaleString()}</strong></li>
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Debt-to-Income (DTI):</span><strong>${d.dti.toFixed(2)}</strong></li>
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Savings Balance:</span><strong>$${d.savings_balance.toLocaleString()}</strong></li>
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Monthly Expenses:</span><strong>$${d.monthly_expenses.toLocaleString()}</strong></li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-primary mb-2">Credit History & Loan</h6>
                            <ul class="list-group list-group-flush small" style="background:transparent;">
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Credit Score (FICO):</span><strong>${d.credit_score}</strong></li>
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Loan Amount Requested:</span><strong>$${d.loan_amount.toLocaleString()} (${d.loan_purpose})</strong></li>
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Term / Interest Rate:</span><strong>${d.loan_term} mos @ ${d.interest_rate}%</strong></li>
                                <li class="list-group-item d-flex justify-content-between px-0" style="background:transparent;"><span class="text-muted">Previous Defaults:</span><strong>${d.previous_defaults}</strong></li>
                            </ul>
                        </div>
                    </div>
                `;
                
                // Show modal using Bootstrap API
                const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
                modal.show();
            } else {
                showToast(data.message || "Failed to load record details", "danger");
            }
        })
        .catch(err => {
            showToast("Error retrieving data", "danger");
            console.error(err);
        });
}

// ----------------------------------------------------
// Selective Checkbox Export Routine
// ----------------------------------------------------
function exportSelectedRecords() {
    const checkboxes = document.querySelectorAll(".record-checkbox:checked");
    if (checkboxes.length === 0) {
        showToast("Please select at least one record to export.", "warning");
        return;
    }
    
    const selectedIds = Array.from(checkboxes).map(cb => cb.value).join(",");
    window.location.href = `/export/csv?ids=${selectedIds}`;
    showToast(`Exported ${checkboxes.length} selected records`, "success");
}

// Toggle select all checkboxes
function toggleSelectAll(masterCb) {
    const checkboxes = document.querySelectorAll(".record-checkbox");
    checkboxes.forEach(cb => {
        cb.checked = masterCb.checked;
    });
}

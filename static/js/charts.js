// Credit Risk Prediction System - Chart.js Visualizations (White & Harlequin Green Theme)

// Theme aware colors helper
const getThemeTextColor = () => {
    return "#000000";
};

const getThemeGridColor = () => {
    return "rgba(57, 255, 20, 0.15)";
};

const getThemeTooltipConfig = () => {
    return {
        backgroundColor: "#ffffff",
        titleColor: "#000000",
        bodyColor: "#000000",
        borderColor: "rgba(57, 255, 20, 0.3)",
        borderWidth: 1.5,
        boxPadding: 5,
        usePointStyle: true
    };
};

// ----------------------------------------------------
// 1. Dashboard Visualizations
// ----------------------------------------------------
function initDashboardVisualizations(data) {
    const textColor = getThemeTextColor();
    const gridColor = getThemeGridColor();
    const tooltipConfig = getThemeTooltipConfig();

    // A. Risk Distribution Doughnut Chart (High contrast Harlequin Green shades)
    const ctxRisk = document.getElementById('riskDoughnutChart');
    if (ctxRisk && data.riskDist) {
        new Chart(ctxRisk, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.riskDist),
                datasets: [{
                    data: Object.values(data.riskDist),
                    backgroundColor: [
                        '#39FF14',                    // Low Risk: Harlequin Green
                        '#f59e0b',                    // Medium Risk: Amber
                        '#ef4444'                     // High Risk: Rose Red
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 2,
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' } }
                    },
                    tooltip: tooltipConfig
                },
                cutout: '72%'
            }
        });
    }

    // B. Monthly Predictions Volume Line Chart
    const ctxTrend = document.getElementById('predictionsLineChart');
    if (ctxTrend && data.monthlyStats) {
        new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: Object.keys(data.monthlyStats),
                datasets: [{
                    data: Object.values(data.monthlyStats),
                    fill: true,
                    backgroundColor: 'rgba(37, 99, 235, 0.05)',
                    borderColor: '#2563eb', // Royal Blue
                    borderWidth: 3,
                    tension: 0.4,
                    pointBackgroundColor: '#2563eb',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: tooltipConfig
                },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' } } },
                    y: { grid: { color: gridColor }, ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' }, precision: 0 } }
                }
            }
        });
    }

    // C. Income vs. Loan Amount Scatter
    const ctxScatter = document.getElementById('incomeLoanScatterChart');
    if (ctxScatter && data.scatterData) {
        const datasets = { 'Low Risk': [], 'Medium Risk': [], 'High Risk': [] };
        data.scatterData.forEach(item => {
            if (datasets[item.risk]) {
                datasets[item.risk].push({ x: item.income, y: item.loan });
            }
        });

        new Chart(ctxScatter, {
            type: 'scatter',
            data: {
                datasets: [
                    { label: 'Low Risk', data: datasets['Low Risk'], backgroundColor: '#39FF14', pointRadius: 5 },
                    { label: 'Medium Risk', data: datasets['Medium Risk'], backgroundColor: '#f59e0b', pointRadius: 5 },
                    { label: 'High Risk', data: datasets['High Risk'], backgroundColor: '#ef4444', pointRadius: 5 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { color: textColor } },
                    tooltip: {
                        ...tooltipConfig,
                        callbacks: {
                            label: (context) => `Income: $${context.raw.x.toLocaleString()} | Loan: $${context.raw.y.toLocaleString()}`
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Annual Income ($)', color: textColor }, grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { title: { display: true, text: 'Loan Amount Requested ($)', color: textColor }, grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });
    }

    // D. Loan Purpose Pie Chart (Varying colors)
    const ctxPurpose = document.getElementById('purposePieChart');
    if (ctxPurpose && data.purposeStats) {
        new Chart(ctxPurpose, {
            type: 'pie',
            data: {
                labels: Object.keys(data.purposeStats),
                datasets: [{
                    data: Object.values(data.purposeStats),
                    backgroundColor: [
                        '#2563eb', // Royal Blue
                        '#39FF14', // Harlequin Green
                        '#f59e0b', // Amber
                        '#ef4444', // Rose Red
                        '#8b5cf6', // Purple
                        '#06b6d4'  // Cyan
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 1.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: textColor, boxWidth: 12 } },
                    tooltip: tooltipConfig
                }
            }
        });
    }

    // E. Employment Status Doughnut Chart
    const ctxEmp = document.getElementById('empStatusChart');
    if (ctxEmp && data.employmentStats) {
        new Chart(ctxEmp, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.employmentStats),
                datasets: [{
                    data: Object.values(data.employmentStats),
                    backgroundColor: [
                        '#39FF14',
                        'rgba(57, 255, 20, 0.7)',
                        'rgba(57, 255, 20, 0.4)',
                        'rgba(57, 255, 20, 0.15)'
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 1.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: textColor, boxWidth: 10 } },
                    tooltip: tooltipConfig
                },
                cutout: '70%'
            }
        });
    }

    // F. Credit Score Distribution Bar Chart
    const ctxScoreDist = document.getElementById('creditScoreDistChart');
    if (ctxScoreDist && data.scoreRanges) {
        new Chart(ctxScoreDist, {
            type: 'bar',
            data: {
                labels: Object.keys(data.scoreRanges),
                datasets: [{
                    data: Object.values(data.scoreRanges),
                    backgroundColor: 'rgba(57, 255, 20, 0.75)',
                    borderRadius: 4,
                    borderColor: '#39FF14',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: tooltipConfig },
                scales: {
                    x: { title: { display: true, text: 'FICO Range', color: textColor }, grid: { display: false }, ticks: { color: textColor } },
                    y: { title: { display: true, text: 'Count', color: textColor }, grid: { color: gridColor }, ticks: { color: textColor, precision: 0 } }
                }
            }
        });
    }
}

// ----------------------------------------------------
// 2. Local XAI / SHAP Attributions Bar Chart
// ----------------------------------------------------
function initXAIChart(contributions) {
    const ctxXAI = document.getElementById('xaiBarChart');
    if (!ctxXAI) return;
    
    const sortedContribs = [...contributions].sort((a, b) => b.contribution - a.contribution);
    const labels = sortedContribs.map(c => `${c.feature} (${c.value})`);
    const dataValues = sortedContribs.map(c => c.contribution);
    
    const backgroundColors = dataValues.map(val => val >= 0 ? '#39FF14' : 'rgba(57, 255, 20, 0.3)');
    const borderColors = dataValues.map(() => '#39FF14');
    
    new Chart(ctxXAI, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1.5,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    ...getThemeTooltipConfig(),
                    callbacks: {
                        label: (context) => {
                            const val = context.raw;
                            return val >= 0 ? ` Increases risk by ${val.toFixed(1)}%` : ` Decreases risk by ${Math.abs(val).toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: 'Attribution Impact (%)', color: getThemeTextColor() }, grid: { color: getThemeGridColor() }, ticks: { color: getThemeTextColor() } },
                y: { grid: { display: false }, ticks: { color: getThemeTextColor(), font: { weight: '600' } } }
            }
        }
    });
}

// ----------------------------------------------------
// 3. Customer Profile Timelines (Historical tracking)
// ----------------------------------------------------
function initCustomerTimelineCharts(dates, scores, risks) {
    const textColor = getThemeTextColor();
    const gridColor = getThemeGridColor();
    const tooltipConfig = getThemeTooltipConfig();

    // A. Credit Score Timeline
    const ctxScore = document.getElementById('scoreTimelineChart');
    if (ctxScore) {
        new Chart(ctxScore, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Credit Score',
                    data: scores,
                    borderColor: '#39FF14',
                    backgroundColor: 'rgba(57, 255, 20, 0.08)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: '#39FF14'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: tooltipConfig },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { min: 300, max: 850, grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });
    }

    // B. Default Risk Trend
    const ctxRisk = document.getElementById('riskTrendChart');
    if (ctxRisk) {
        new Chart(ctxRisk, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Default Prob (%)',
                    data: risks,
                    borderColor: '#39FF14',
                    backgroundColor: 'rgba(57, 255, 20, 0.04)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: '#39FF14'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: tooltipConfig },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { min: 0, max: 100, grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });
    }
}

// ----------------------------------------------------
// 4. Loan Calculator Visualizations
// ----------------------------------------------------
let emiPieChartInstance = null;
function updateEMIPieChart(principal, totalInterest) {
    const ctx = document.getElementById('emiPieChart');
    if (!ctx) return;
    
    if (emiPieChartInstance) {
        emiPieChartInstance.destroy();
    }
    
    emiPieChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Principal Amount', 'Total Interest'],
            datasets: [{
                data: [principal, totalInterest],
                backgroundColor: ['#2563eb', '#f59e0b'],
                borderColor: '#ffffff',
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: getThemeTextColor() } },
                tooltip: getThemeTooltipConfig()
            }
        }
    });
}

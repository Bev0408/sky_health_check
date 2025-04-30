/**
 * charts.js - Analytics Dashboard Charts
 * 
 * This file contains JavaScript for initializing and managing charts
 * on the analytics dashboard using Chart.js library.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if elements exist
    if (document.getElementById('trend-chart')) {
        initTrendsChart();
    }
    
    if (document.getElementById('category-chart')) {
        initCategoryHealthChart();
    }
    
    if (document.getElementById('team-comparison-chart')) {
        initTeamComparisonChart();
    }
});

/**
 * Initialize the Health Check Trends Chart
 */
function initTrendsChart() {
    const ctx = document.getElementById('trend-chart').getContext('2d');
    
    // Get data from the canvas element attributes
    const chartElement = document.getElementById('trend-chart');
    if (!chartElement) return;
    
    const labels = JSON.parse(chartElement.getAttribute('data-labels'));
    const redData = JSON.parse(chartElement.getAttribute('data-red'));
    const yellowData = JSON.parse(chartElement.getAttribute('data-yellow'));
    const greenData = JSON.parse(chartElement.getAttribute('data-green'));
    
    const trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Red Responses',
                    data: redData,
                    borderColor: '#DC3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: 'Yellow Responses',
                    data: yellowData,
                    borderColor: '#FFD700',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: 'Green Responses',
                    data: greenData,
                    borderColor: '#32CD32',
                    backgroundColor: 'rgba(50, 205, 50, 0.1)',
                    borderWidth: 2,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Health Check Trends Over Time'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Initialize the Category Health Chart
 */
function initCategoryHealthChart() {
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // Get data from the canvas element attributes
    const chartElement = document.getElementById('category-chart');
    if (!chartElement) return;
    
    const categories = JSON.parse(chartElement.getAttribute('data-categories'));
    const redData = JSON.parse(chartElement.getAttribute('data-red'));
    const yellowData = JSON.parse(chartElement.getAttribute('data-yellow'));
    const greenData = JSON.parse(chartElement.getAttribute('data-green'));
    
    const categoryHealthChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'Red Responses',
                    data: redData,
                    backgroundColor: '#DC3545',
                    borderColor: '#DC3545',
                    borderWidth: 1
                },
                {
                    label: 'Yellow Responses',
                    data: yellowData,
                    backgroundColor: '#FFD700',
                    borderColor: '#FFD700',
                    borderWidth: 1
                },
                {
                    label: 'Green Responses',
                    data: greenData,
                    backgroundColor: '#32CD32',
                    borderColor: '#32CD32',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Health by Category'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Initialize the Team Comparison Chart
 */
function initTeamComparisonChart() {
    const ctx = document.getElementById('teamComparisonChart').getContext('2d');
    
    // Get data from the data attributes
    const chartDataElement = document.getElementById('team-comparison-data');
    if (!chartDataElement) return;
    
    const teams = JSON.parse(chartDataElement.getAttribute('data-teams'));
    const healthScores = JSON.parse(chartDataElement.getAttribute('data-scores'));
    
    // Create background colors with varying opacity
    const backgroundColors = healthScores.map(score => {
        if (score < 33) {
            return 'rgba(220, 53, 69, 0.7)'; // Red
        } else if (score < 66) {
            return 'rgba(255, 215, 0, 0.7)'; // Yellow
        } else {
            return 'rgba(50, 205, 50, 0.7)'; // Green
        }
    });
    
    const teamComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: teams,
            datasets: [{
                label: 'Overall Health Score',
                data: healthScores,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Health Score (%)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Team Health Comparison'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const score = context.raw;
                            let status = '';
                            if (score < 33) {
                                status = 'Needs Improvement';
                            } else if (score < 66) {
                                status = 'Average';
                            } else {
                                status = 'Healthy';
                            }
                            return `Health Score: ${score}% (${status})`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update charts when date filters change
 */
function updateChartsWithDateFilter() {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    
    if (startDate && endDate) {
        window.location.href = `?start_date=${startDate}&end_date=${endDate}`;
    }
}

// Add event listeners to date filters
document.addEventListener('DOMContentLoaded', function() {
    const applyFilterBtn = document.getElementById('apply-filter');
    if (applyFilterBtn) {
        applyFilterBtn.addEventListener('click', updateChartsWithDateFilter);
    }
});
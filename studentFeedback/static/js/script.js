// Handle form submission
document.getElementById('feedbackForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent the form from submitting and refreshing the page

    // Get selected teacher
    const teacher = document.getElementById('teacher').value;

    // Gather ratings from all questions
    const ratings = {};
    document.querySelectorAll('.stars').forEach((starContainer) => {
        const questionId = starContainer.getAttribute('data-question');
        const rating = starContainer.getAttribute('data-rating');
        ratings[questionId] = rating || 0; // Default to 0 if no rating selected
    });

    // Send feedback data to the backend
    const response = await fetch('/submit_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ teacher, ratings })
    });

    const result = await response.json();
    alert(result.message); // Display feedback submission status

    loadRankings(); // Refresh rankings after feedback submission
});

// Function to load and display rankings (Teacher's average rating)
async function loadRankings() {
    const response = await fetch('/get_rankings');
    const data = await response.json();
    if (data.length === 0) {
        document.getElementById('rankingsChart').innerHTML = '<p>No rankings available</p>';
        return;
    }

    // Prepare labels (teacher names) and values (average ratings)
    const labels = data.map((item) => item[0]); // Teacher names
    const values = data.map((item) => item[1]); // Average ratings
    // Get the canvas context
    const ctx = document.getElementById('rankingsChart').getContext('2d');

    // Clear existing chart instance (if any)
    // if (window.rankingsChart && window.rankingsChart.destroy()) {
    //     window.rankingsChart.destroy();
    // }

    // Create a new animated chart
    window.rankingsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Average Rating',
                    data: values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            animation: {
                duration: 2000,
                easing: 'easeOutBounce'
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#fff',
                        font: {
                            size: 14,
                            family: 'Arial'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.7)',
                    titleFont: {
                        size: 16
                    },
                    bodyFont: {
                        size: 14
                    },
                    displayColors: true,
                    borderColor: 'rgba(255, 255, 255, 0.8)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#fff',
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)'
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff',
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)'
                    }
                }
            }
        }
    });
}

// Load rankings when the page loads
window.onload = loadRankings;

// Handle star rating selection
document.querySelectorAll('.stars').forEach((starContainer) => {
    starContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('star')) {
            const stars = starContainer.querySelectorAll('.star');
            stars.forEach((star) => star.classList.remove('selected'));
            const rating = e.target.getAttribute('data-value');
            for (let i = 0; i < rating; i++) {
                stars[i].classList.add('selected');
            }
            // Store the rating for this question
            starContainer.setAttribute('data-rating', rating);
        }
    });
});

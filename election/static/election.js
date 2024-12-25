document.getElementById("prediction-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Gather input values
    const party1 = document.getElementById("party1").value;
    const party2 = document.getElementById("party2").value;
    const subreddit = document.getElementById("subreddit").value || "news";
    const commentLimit = document.getElementById("comment-limit").value;

    // Display loading state
    const resultsSection = document.getElementById("results-section");
    resultsSection.style.display = "block";
    resultsSection.innerHTML = "<p>Loading sentiment analysis results...</p>";

    try {
        // Call the backend API
        const sentimentData = await fetchSentimentAnalysis(party1, party2, subreddit, commentLimit);

        // Clear loading state and render charts, summary, and sentiment scores
        resultsSection.innerHTML = `
            <h2>Results</h2>
            <div id="charts">
                <canvas id="chart-party1"></canvas>
                <canvas id="chart-party2"></canvas>
            </div>
            <div id="summary">
                <p>${sentimentData.summary}</p>
            </div>
            <div id="sentiment-scores">
                <h3>Sentiment Scores:</h3>
                <p><strong>${party1} Sentiment:</strong> Positive: ${sentimentData.party1.Positive}, Negative: ${sentimentData.party1.Negative}, Neutral: ${sentimentData.party1.Neutral}</p>
                <p><strong>${party2} Sentiment:</strong> Positive: ${sentimentData.party2.Positive}, Negative: ${sentimentData.party2.Negative}, Neutral: ${sentimentData.party2.Neutral}</p>
            </div>
        `;

        // Render charts
        renderChart("chart-party1", `${party1} Sentiment`, sentimentData.party1);
        renderChart("chart-party2", `${party2} Sentiment`, sentimentData.party2);
    } catch (error) {
        resultsSection.innerHTML = `<p>Error fetching sentiment analysis results: ${error.message}</p>`;
    }
});

// Function to fetch API response
async function fetchSentimentAnalysis(party1, party2, subreddit, limit) {
    const response = await fetch("http://127.0.0.1:5000/api/sentiment-analysis", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ party1, party2, subreddit, limit }),
    });
    if (!response.ok) {
        throw new Error("Failed to fetch sentiment analysis results");
    }
    return await response.json();
}

// Function to render chart
function renderChart(canvasId, label, sentimentData) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(sentimentData),
            datasets: [
                {
                    label: label,
                    data: Object.values(sentimentData),
                    backgroundColor: ["green", "red", "blue"],
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                },
                title: {
                    display: true,
                    text: label,
                },
            },
        },
    });
}

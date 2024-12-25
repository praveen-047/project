from flask import Flask, request, jsonify, render_template
import praw
from textblob import TextBlob
import pandas as pd

app = Flask(__name__)

# Serve the election.html page
@app.route('/')
def index():
    return render_template('election.html')  # This will render your HTML file

# Reddit API Authentication
def authenticate_reddit():
    reddit = praw.Reddit(
        client_id="waLAhLLqesQteGq2bQbUcQ",  # Replace with your Reddit app's client ID
        client_secret="woitJOQJQCzuodMIjiWlXLwFDO5nXQ",  # Replace with your Reddit app's client secret
        user_agent="ElectionSentimentAnalysisBot"
    )
    return reddit

# Fetch comments from Reddit
def fetch_comments(reddit, subreddit, query, limit):
    comments = []
    count = 0
    for submission in reddit.subreddit(subreddit).search(query, limit=500):
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if count < limit:
                comments.append(comment.body)
                count += 1
            else:
                break
        if count >= limit:
            break
    return pd.DataFrame(comments, columns=["Comment"])

# Sentiment Analysis
def sentiment_analysis(df):
    sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for comment in df["Comment"]:
        analysis = TextBlob(comment)
        polarity = analysis.sentiment.polarity
        if polarity > 0:
            sentiments["Positive"] += 1
        elif polarity < 0:
            sentiments["Negative"] += 1
        else:
            sentiments["Neutral"] += 1
    return sentiments

# Flask API Endpoint for sentiment analysis
@app.route('/api/sentiment-analysis', methods=['POST'])
def sentiment_analysis_endpoint():
    data = request.json
    party1 = data.get("party1")
    party2 = data.get("party2")
    subreddit = data.get("subreddit", "news")
    limit = int(data.get("limit", 100))

    reddit = authenticate_reddit()

    # Fetch and analyze comments for Party 1
    df_party1 = fetch_comments(reddit, subreddit, party1, limit)
    sentiments_party1 = sentiment_analysis(df_party1)

    # Fetch and analyze comments for Party 2
    df_party2 = fetch_comments(reddit, subreddit, party2, limit)
    sentiments_party2 = sentiment_analysis(df_party2)

    # Generate summary
    summary = f"{party1} has higher positive sentiment compared to {party2}." if sentiments_party1["Positive"] > sentiments_party2["Positive"] else f"{party2} has higher positive sentiment compared to {party1}."

    return jsonify({
        "party1": sentiments_party1,
        "party2": sentiments_party2,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(debug=True)

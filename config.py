"""
Configuration file for Twitter Sentiment Analysis System
Add your Twitter API credentials here
"""

# Twitter API Credentials (Get from https://developer.twitter.com/)
TWITTER_API_KEY = "..."
TWITTER_API_SECRET = "..."
TWITTER_ACCESS_TOKEN = "..."
TWITTER_ACCESS_TOKEN_SECRET = "..."
TWITTER_BEARER_TOKEN = "..."

STREAM_KEYWORDS = ["#python", "#AI", "#MachineLearning", "#DataScience"]
TWEET_LANGUAGE = "en"

SPARK_MASTER = "local[*]"
SOCKET_HOST = "localhost"
SOCKET_PORT = 9999

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

OUTPUT_JSON_PATH = "./output/sentiment_counts.json"
MODEL_PATH = "./models/model.pkl"
VECTORIZER_PATH = "./models/vectorizer.pkl"


# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/sentiment_analysis.log"

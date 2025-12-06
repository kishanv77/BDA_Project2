"""
Configuration file for Twitter Sentiment Analysis System.
DO NOT hardcode real credentials. Use environment variables instead.
"""

import os

# Twitter API Credentials (get from https://developer.twitter.com/)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Bearer Token for Twitter API v2
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Streaming Configuration
STREAM_KEYWORDS = ["#python", "#AI", "#MachineLearning", "#DataScience"]
TWEET_LANGUAGE = "en"
MAX_TWEETS_PER_BATCH = 100

# Spark Configuration
SPARK_MASTER = "local[*]"
BATCH_INTERVAL = 10
CHECKPOINT_DIR = "./checkpoints"

# Socket Configuration
SOCKET_HOST = "localhost"
SOCKET_PORT = 9999

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Output Configuration
OUTPUT_JSON_PATH = "./output/sentiment_counts.json"
MODEL_PATH = "./models/model.pkl"
VECTORIZER_PATH = "./models/vectorizer.pkl"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/sentiment_analysis.log"

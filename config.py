"""
Configuration file for Twitter Sentiment Analysis System
Add your Twitter API credentials here
"""

# Twitter API Credentials (Get from https://developer.twitter.com/)
TWITTER_API_KEY = "CuGq8tkRICfX4Svabvx2cJuNu"
TWITTER_API_SECRET = "tK7RF6orMi2x8UHI87dCivZxAfAEIccjR8licwP7BZ5BcJ8X0B"
TWITTER_ACCESS_TOKEN = "1268173343577870336-U1ODrlOh2eFF41k9j0amHG34a8UWz9"
TWITTER_ACCESS_TOKEN_SECRET = "zH8PI2iwdEBV42tLd6fOV7WWKsNjLu96xU7etmFnIVYBb"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKkU5AEAAAAAU3CIULTGuRn1pxpOWrPOGeWuCjU%3DOTbhiefl24Z4Gr9v727ek3Z80wmxlELBPQwYOGuaoOT3pQMZQU"

# Streaming Configuration
STREAM_KEYWORDS = ["#python", "#AI", "#MachineLearning", "#DataScience"]  # Keywords to track
TWEET_LANGUAGE = "en"  # Language filter
MAX_TWEETS_PER_BATCH = 100  # Tweets to buffer before sending

# Spark Configuration
SPARK_MASTER = "local[*]"  # Use all available cores
BATCH_INTERVAL = 10  # Seconds
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

"""
PySpark Streaming application for real-time sentiment analysis
Reads tweets from socket, classifies sentiment, and saves results
"""

import sys
import os
import json
import logging
import re
from datetime import datetime
from pathlib import Path

# PySpark imports
try:
    from pyspark.sql import SparkSession
    from pyspark.streaming import StreamingContext
    from pyspark.sql.types import StructType, StructField, StringType
except ImportError:
    print("Error: PySpark not installed. Run: pip install pyspark")
    sys.exit(1)

# ML imports
try:
    import joblib
except ImportError:
    print("Error: joblib not installed. Run: pip install joblib")
    sys.exit(1)

from config import (
    SPARK_MASTER, BATCH_INTERVAL, CHECKPOINT_DIR,
    SOCKET_HOST, SOCKET_PORT, OUTPUT_JSON_PATH,
    MODEL_PATH, VECTORIZER_PATH
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/spark_streaming.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Load and use pre-trained sentiment model"""

    def __init__(self, model_path, vectorizer_path):
        self.model = None
        self.vectorizer = None
        self.load_model(model_path, vectorizer_path)

    def load_model(self, model_path, vectorizer_path):
        """Load saved model and vectorizer"""
        try:
            if not os.path.exists(model_path):
                logger.warning(f"Model not found at {model_path}")
                logger.info("Run train_model.py first to train the sentiment model")
                raise FileNotFoundError(f"Model not found at {model_path}")

            if not os.path.exists(vectorizer_path):
                raise FileNotFoundError(f"Vectorizer not found at {vectorizer_path}")

            logger.info(f"Loading model from {model_path}")
            self.model = joblib.load(model_path)

            logger.info(f"Loading vectorizer from {vectorizer_path}")
            self.vectorizer = joblib.load(vectorizer_path)

            logger.info("✓ Model and vectorizer loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def clean_tweet(self, tweet):
        """Clean tweet text"""
        # Remove URLs
        tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
        # Remove email addresses
        tweet = re.sub(r'\S+@\S+', '', tweet)
        # Remove mentions
        tweet = re.sub(r'@\w+', '', tweet)
        # Remove hashtags
        tweet = re.sub(r'#\w+', '', tweet)
        # Remove special characters and digits
        tweet = re.sub(r'[^a-zA-Z\s]', '', tweet)
        # Remove extra whitespace
        tweet = ' '.join(tweet.split())
        # Convert to lowercase
        tweet = tweet.lower()
        return tweet

    def predict(self, tweet):
        """Predict sentiment for a tweet"""
        try:
            cleaned = self.clean_tweet(tweet)
            if not cleaned or len(cleaned.strip()) == 0:
                return 1  # Default to neutral for empty tweets

            vectorized = self.vectorizer.transform([cleaned])
            prediction = self.model.predict(vectorized)[0]
            return int(prediction)
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return 1  # Default to neutral on error

class RealTimeSentimentDashboard:
    """Manage sentiment statistics for dashboard"""

    def __init__(self, output_path=OUTPUT_JSON_PATH):
        self.output_path = output_path
        self.stats = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'total_tweets': 0,
            'last_updated': datetime.now().isoformat(),
            'batches_processed': 0
        }

    def update(self, sentiment_counts):
        """Update statistics"""
        self.stats['positive'] += sentiment_counts.get(2, 0)
        self.stats['negative'] += sentiment_counts.get(0, 0)
        self.stats['neutral'] += sentiment_counts.get(1, 0)
        self.stats['total_tweets'] += sum(sentiment_counts.values())
        self.stats['batches_processed'] += 1
        self.stats['last_updated'] = datetime.now().isoformat()

    def save(self):
        """Save to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.output_path) or '.', exist_ok=True)
            with open(self.output_path, 'w') as f:
                json.dump(self.stats, f, indent=2)
            logger.info(f"Stats saved: {self.stats}")
        except Exception as e:
            logger.error(f"Error saving stats: {str(e)}")

def process_tweets(batch_data):
    """Process a batch of tweets"""
    try:
        if not batch_data or batch_data.isEmpty():
            return

        # Get data from RDD
        tweets = batch_data.collect()

        if not tweets:
            return

        logger.info(f"Processing batch with {len(tweets)} tweets")

        # Count sentiments
        sentiment_counts = {0: 0, 1: 0, 2: 0}

        for tweet in tweets:
            try:
                text = tweet if isinstance(tweet, str) else tweet[0]
                if text and len(text.strip()) > 0:
                    sentiment = analyzer.predict(text)
                    sentiment_counts[sentiment] += 1
                    logger.debug(f"Tweet: {text[:50]}... -> Sentiment: {sentiment}")
            except Exception as e:
                logger.error(f"Error processing tweet: {str(e)}")

        # Update dashboard
        dashboard.update(sentiment_counts)
        dashboard.save()

    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")

def create_streaming_context():
    """Create Spark Streaming context"""
    try:
        logger.info("Creating Spark Streaming context...")

        # Create Spark session
        spark = SparkSession.builder \
            .master(SPARK_MASTER) \
            .appName("TwitterSentimentAnalysis") \
            .config("spark.streaming.stopGracefullyOnShutdown", "true") \
            .getOrCreate()

        # Suppress verbose logging
        spark.sparkContext.setLogLevel("WARN")

        # Create streaming context
        ssc = StreamingContext(spark.sparkContext, BATCH_INTERVAL)

        # Set checkpoint directory
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        ssc.checkpoint(CHECKPOINT_DIR)

        logger.info(f"✓ Streaming context created (batch interval: {BATCH_INTERVAL}s)")
        return ssc

    except Exception as e:
        logger.error(f"Error creating streaming context: {str(e)}")
        raise

def main():
    """Main entry point"""
    global analyzer, dashboard

    logger.info("="*60)
    logger.info("Twitter Sentiment Analysis - Spark Streaming Component")
    logger.info("="*60)

    try:
        # Check if model exists
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model not found at {MODEL_PATH}")
            logger.info("Please run train_model.py first")
            return

        # Load sentiment analyzer
        logger.info("Loading sentiment model...")
        analyzer = SentimentAnalyzer(MODEL_PATH, VECTORIZER_PATH)

        # Initialize dashboard
        dashboard = RealTimeSentimentDashboard()

        # Create streaming context
        ssc = create_streaming_context()

        # Create socket stream
        logger.info(f"Listening for tweets on {SOCKET_HOST}:{SOCKET_PORT}")
        socket_stream = ssc.socketTextStream(SOCKET_HOST, int(SOCKET_PORT))

        # Process tweets
        socket_stream.foreachRDD(process_tweets)

        # Start streaming
        logger.info("Starting Spark Streaming...")
        logger.info("Press Ctrl+C to stop")
        logger.info(f"Dashboard will be updated in {BATCH_INTERVAL}s batches")

        ssc.start()
        ssc.awaitTermination()

    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        if 'ssc' in locals():
            ssc.stop(stopSparkContext=True, stopGracefully=True)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        if 'ssc' in locals():
            ssc.stop(stopSparkContext=True, stopGracefully=False)
    finally:
        logger.info("✓ Spark Streaming stopped")

if __name__ == "__main__":
    main()

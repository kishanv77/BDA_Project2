"""
Stream tweets from Twitter API and send to socket server
Connects to Twitter API v2 and sends tweets to localhost:9999
"""

import socket
import json
import time
import logging
import sys
import threading
from datetime import datetime
from collections import deque
from queue import Queue

try:
    import tweepy
except ImportError:
    print("Error: tweepy not installed. Run: pip install tweepy")
    sys.exit(1)

from config import (
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN,
    STREAM_KEYWORDS, TWEET_LANGUAGE,
    SOCKET_HOST, SOCKET_PORT, MAX_TWEETS_PER_BATCH
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/twitter_stream.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterStreamListener:
    """Listen to tweets and buffer them for socket transmission"""

    def __init__(self, buffer_size=MAX_TWEETS_PER_BATCH):
        self.tweet_buffer = deque(maxlen=buffer_size)
        self.tweet_count = 0
        self.error_count = 0
        self.lock = threading.Lock()

    def add_tweet(self, tweet_text):
        """Add tweet to buffer"""
        with self.lock:
            self.tweet_buffer.append(tweet_text)
            self.tweet_count += 1

    def get_batch(self):
        """Get all tweets from buffer"""
        with self.lock:
            batch = list(self.tweet_buffer)
            self.tweet_buffer.clear()
            return batch

    def increment_error(self):
        """Track errors"""
        self.error_count += 1

class TwitterStreamClient:
    """Handle Twitter API connection and streaming using Tweepy v2 StreamingClient"""

    class StreamingListener(tweepy.StreamingClient):
        def __init__(self, bearer_token, listener):
            super().__init__(bearer_token)
            self.listener = listener

        def on_tweet(self, tweet):
            try:
                # tweet.text is available on Tweet object
                self.listener.add_tweet(tweet.text)
                logger.debug(f"Tweet received: {tweet.text[:50]}...")
            except Exception as e:
                logger.error(f"Error processing tweet: {e}")
                self.listener.increment_error()

        def on_connection_error(self):
            logger.error("Streaming connection error")
            self.listener.increment_error()

        def on_request_error(self, status_code):
            logger.error(f"Streaming request error: {status_code}")
            self.listener.increment_error()

    def __init__(self):
        self.listener = TwitterStreamListener()
        self.streaming_client = None
        self.running = False

    def authenticate(self):
        """Authenticate with Twitter API v2 (requires bearer token)"""
        try:
            logger.info("Authenticating with Twitter API v2...")
            if not TWITTER_BEARER_TOKEN or TWITTER_BEARER_TOKEN.startswith("AAAA"):
                raise ValueError("Twitter Bearer Token not configured in config.py")
            self.streaming_client = self.StreamingListener(TWITTER_BEARER_TOKEN, self.listener)
            logger.info("✓ Authentication successful")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self.streaming_client = None
            return False

    def stream_tweets(self):
        """Stream tweets in a separate thread by adding rules and calling filter()."""
        try:
            if self.streaming_client is None:
                logger.error("StreamingClient not initialized; cannot start stream")
                return

            logger.info(f"Starting to stream tweets with keywords: {STREAM_KEYWORDS}")

            # Remove existing rules if any
            rules_resp = self.streaming_client.get_rules()
            existing_rules = getattr(rules_resp, 'data', None)
            if existing_rules:
                ids = [r.id for r in existing_rules]
                self.streaming_client.delete_rules(ids)

            # Build query string
            query = " OR ".join(STREAM_KEYWORDS)
            if TWEET_LANGUAGE:
                query += f" lang:{TWEET_LANGUAGE}"
            logger.info(f"Query: {query}")

            # Add new rule
            self.streaming_client.add_rules(tweepy.StreamRule(value=query))

            # Start streaming (this call blocks until stopped)
            self.streaming_client.filter(tweet_fields=["created_at", "text"])

        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            self.listener.increment_error()

class SocketServer:
    """Send tweets to socket server"""

    def __init__(self, host=SOCKET_HOST, port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        """Connect to socket server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"✓ Connected to socket server at {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            logger.error(f"Socket server not running at {self.host}:{self.port}")
            logger.info("Make sure spark_streaming_app.py is running first")
            return False
        except Exception as e:
            logger.error(f"Socket connection error: {str(e)}")
            return False

    def send_tweets(self, tweets):
        """Send tweets to socket server"""
        if not tweets:
            logger.debug("No tweets to send.")
            return False

        if not self.connected or self.socket is None:
            logger.error("Socket is not connected. Cannot send tweets.")
            return False

        try:
            for tweet in tweets:
                message = tweet.encode('utf-8') + b'\n'
                self.socket.sendall(message)

            logger.info(f"Sent {len(tweets)} tweets to socket")
            return True
        except Exception as e:
            logger.error(f"Error sending tweets: {str(e)}")
            self.connected = False
            try:
                if self.socket:
                    self.socket.close()
            except Exception:
                pass
            self.socket = None
            return False

    def close(self):
        """Close socket connection"""
        if self.socket:
            self.socket.close()
            self.connected = False

class TwitterSentimentStreamer:
    """Main coordinator"""

    def __init__(self):
        self.twitter_client = TwitterStreamClient()
        self.socket_server = SocketServer()
        self.running = False

    def start(self):
        """Start streaming"""
        try:
            # Authenticate
            if not self.twitter_client.authenticate():
                logger.error("Failed to authenticate with Twitter API")
                return False

            # Connect to socket
            if not self.socket_server.connect():
                logger.error("Failed to connect to socket server")
                logger.info("\nMake sure to run spark_streaming_app.py first!")
                return False

            self.running = True
            logger.info("Starting tweet stream...")

            # Start streaming in separate thread
            stream_thread = threading.Thread(
                target=self.twitter_client.stream_tweets,
                daemon=True
            )
            stream_thread.start()

            # Send tweets in batches
            logger.info(f"Batching tweets every {MAX_TWEETS_PER_BATCH} tweets or on interval...")

            while self.running:
                try:
                    tweets = self.twitter_client.listener.get_batch()
                    if tweets:
                        self.socket_server.send_tweets(tweets)

                    time.sleep(2)  # Check buffer every 2 seconds

                except KeyboardInterrupt:
                    logger.info("\nShutting down...")
                    self.running = False
                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}")
                    time.sleep(5)

            return True

        except KeyboardInterrupt:
            logger.info("Stream interrupted by user")
            return True
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            return False
        finally:
            self.socket_server.close()
            logger.info("✓ Twitter stream stopped")

def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("Twitter Sentiment Analysis - Stream Component")
    logger.info("="*60)

    # Check API credentials
    if TWITTER_BEARER_TOKEN == "AAAAAAAAAAAAAAAAAAAAAKkU5AEAAAAA0NQeR8jmpsur1Cvm05aOfSzy7QA%3DEmeXe2mA465572LkM4I8I5u0VTWTUD6pzfDQEttsNPXegPHWQn":
        logger.error("ERROR: Twitter API credentials not configured!")
        logger.info("\nSteps to configure:")
        logger.info("1. Go to https://developer.twitter.com/")
        logger.info("2. Create a project and app")
        logger.info("3. Get your Bearer Token")
        logger.info("4. Add it to config.py: TWITTER_BEARER_TOKEN = 'your_token'")
        return

    streamer = TwitterSentimentStreamer()
    streamer.start()

if __name__ == "__main__":
    main()

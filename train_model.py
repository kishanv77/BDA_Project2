"""
Train sentiment classification model using Logistic Regression
Saves model.pkl and vectorizer.pkl for use in Spark Streaming
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import re

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SentimentModelTrainer:
    """Train and save sentiment classification model"""

    def __init__(self, model_path="./models/model.pkl", vectorizer_path="./models/vectorizer.pkl"):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.vectorizer = None
        self.model = None

    def clean_tweet(self, tweet):
        """Clean tweet text for model training"""
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

    def load_dataset(self, csv_path):
        """Load and validate dataset"""
        logger.info(f"Loading dataset from {csv_path}")
        try:
            df = pd.read_csv(csv_path)

            # Validate columns
            if 'text' not in df.columns or 'label' not in df.columns:
                raise ValueError("Dataset must contain 'text' and 'label' columns")

            logger.info(f"Dataset loaded: {len(df)} samples")
            logger.info(f"Label distribution:\n{df['label'].value_counts()}")

            return df
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise

    def preprocess_data(self, df):
        """Preprocess and clean tweets"""
        logger.info("Preprocessing tweets...")
        df['cleaned_text'] = df['text'].apply(self.clean_tweet)

        # Remove empty tweets
        df = df[df['cleaned_text'].str.len() > 0]
        logger.info(f"After preprocessing: {len(df)} samples")

        return df

    def train(self, csv_path, test_size=0.2, random_state=42):
        """Train sentiment model"""
        try:
            # Load data
            df = self.load_dataset(csv_path)

            # Preprocess
            df = self.preprocess_data(df)

            # Validate labels (0=negative, 1=neutral, 2=positive)
            unique_labels = set(df['label'].unique())
            expected_labels = {0, 1, 2}
            if not unique_labels.issubset(expected_labels):
                logger.warning(f"Unexpected labels: {unique_labels}. Expected: {expected_labels}")

            # Split data
            logger.info("Splitting dataset...")
            X_train, X_test, y_train, y_test = train_test_split(
                df['cleaned_text'],
                df['label'],
                test_size=test_size,
                random_state=random_state,
                stratify=df['label']
            )

            # Vectorize text
            logger.info("Vectorizing text using TF-IDF...")
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8,
                lowercase=True
            )
            X_train_vec = self.vectorizer.fit_transform(X_train)
            X_test_vec = self.vectorizer.transform(X_test)

            logger.info(f"TF-IDF features created: {X_train_vec.shape[1]} features")

            # Train model
            logger.info("Training Logistic Regression model...")
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                n_jobs=-1,
                solver='lbfgs'
            )
            self.model.fit(X_train_vec, y_train)

            # Evaluate
            logger.info("Evaluating model...")
            y_pred = self.model.predict(X_test_vec)
            accuracy = accuracy_score(y_test, y_pred)

            logger.info(f"\nModel Accuracy: {accuracy:.4f}")
            logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=['Negative', 'Neutral', 'Positive'])}")

            # Save model and vectorizer
            logger.info(f"Saving model to {self.model_path}")
            joblib.dump(self.model, self.model_path)

            logger.info(f"Saving vectorizer to {self.vectorizer_path}")
            joblib.dump(self.vectorizer, self.vectorizer_path)

            logger.info("✓ Model training completed successfully!")
            return accuracy

        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise

def main():
    """Main entry point"""
    # Check if sample dataset exists
    csv_path = "./data/tweets.csv"

    if not os.path.exists(csv_path):
        logger.warning(f"Dataset not found at {csv_path}")
        logger.info("Creating sample dataset for demonstration...")

        # Create sample dataset
        sample_data = {
            'text': [
                'I love this product! It\'s amazing',
                'This is terrible and not worth it',
                'It\'s okay, nothing special',
                'Python is great for data science',
                'I hate waiting in long queues',
                'Machine learning is interesting',
                'This movie was average',
                'Fantastic experience!',
                'Worst service ever',
                'Could be better'
            ] * 10,  # Repeat for more samples
            'label': [2, 0, 1, 2, 0, 2, 1, 2, 0, 1] * 10
        }

        df = pd.DataFrame(sample_data)
        os.makedirs('./data', exist_ok=True)
        df.to_csv(csv_path, index=False)
        logger.info(f"Sample dataset created: {csv_path}")

    # Train model
    trainer = SentimentModelTrainer()
    trainer.train(csv_path)

if __name__ == "__main__":
    main()

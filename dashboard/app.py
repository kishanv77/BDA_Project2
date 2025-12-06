"""
Flask dashboard for real-time sentiment analysis visualization
Reads sentiment_counts.json and displays interactive charts
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, jsonify
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, OUTPUT_JSON_PATH

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

class SentimentDataManager:
    """Manage sentiment data from JSON file"""

    def __init__(self, data_file=OUTPUT_JSON_PATH):
        self.data_file = data_file

    def get_data(self):
        """Read sentiment data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default data if file doesn't exist
                return {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total_tweets': 0,
                    'last_updated': datetime.now().isoformat(),
                    'batches_processed': 0
                }
        except Exception as e:
            logger.error(f"Error reading data: {str(e)}")
            return {}

data_manager = SentimentDataManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/sentiment-data')
def get_sentiment_data():
    """Get current sentiment data"""
    data = data_manager.get_data()
    return jsonify(data)

@app.route('/api/sentiment-summary')
def get_sentiment_summary():
    """Get sentiment summary for charts"""
    data = data_manager.get_data()

    total = data.get('total_tweets', 0)
    if total == 0:
        positive_pct = negative_pct = neutral_pct = 0
    else:
        positive_pct = (data.get('positive', 0) / total * 100)
        negative_pct = (data.get('negative', 0) / total * 100)
        neutral_pct = (data.get('neutral', 0) / total * 100)

    return jsonify({
        'labels': ['Positive', 'Negative', 'Neutral'],
        'data': [
            data.get('positive', 0),
            data.get('negative', 0),
            data.get('neutral', 0)
        ],
        'percentages': [positive_pct, negative_pct, neutral_pct],
        'total': total,
        'last_updated': data.get('last_updated'),
        'batches': data.get('batches_processed', 0)
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

def main():
    """Run Flask app"""
    logger.info("="*60)
    logger.info("Starting Sentiment Analysis Dashboard")
    logger.info("="*60)
    logger.info(f"Dashboard running at http://{FLASK_HOST}:{FLASK_PORT}")
    logger.info("Press Ctrl+C to stop")

    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG,
        use_reloader=False  # Disable reloader to avoid port conflicts
    )

if __name__ == '__main__':
    main()

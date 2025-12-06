# Real-Time Twitter Sentiment Analysis - Execution Guide

## Quick Start (5 minutes)

If you've already set up the environment, follow these steps:

### Terminal 1: Start Spark Streaming
```bash
cd TwitterSentimentAnalysis
venv\Scripts\activate
python spark_streaming_app.py
```

### Terminal 2: Start Twitter Stream
```bash
cd TwitterSentimentAnalysis
venv\Scripts\activate
python twitter_stream.py
```

### Terminal 3: Start Dashboard
```bash
cd TwitterSentimentAnalysis\dashboard
python app.py
```

### Open Dashboard
```
http://localhost:5000
```

---

## Detailed Execution Steps

### Step 0: Prerequisites

✅ Java installed and JAVA_HOME set  
✅ Python 3.9+ installed  
✅ Virtual environment created: `venv\Scripts\activate`  
✅ Dependencies installed: `pip install -r requirements.txt`  
✅ Model trained: `python train_model.py`  
✅ Twitter API credentials in `config.py`  

---

### Step 1: Start Spark Streaming (Terminal 1)

**This must be started FIRST**

```bash
# Navigate to project
cd TwitterSentimentAnalysis

# Activate virtual environment
venv\Scripts\activate

# Start Spark Streaming
python spark_streaming_app.py
```

**Expected Output:**
```
============================================================
Twitter Sentiment Analysis - Spark Streaming Component
============================================================
Loading sentiment model...
✓ Model and vectorizer loaded successfully
Creating Spark Streaming context...
✓ Streaming context created (batch interval: 10s)
Listening for tweets on localhost:9999
Starting Spark Streaming...
Press Ctrl+C to stop
```

**Important:** Keep this window open. This is your streaming engine.

---

### Step 2: Start Twitter Stream (Terminal 2)

**After Spark is running, start this**

```bash
# New Terminal Window
cd TwitterSentimentAnalysis

# Activate virtual environment
venv\Scripts\activate

# Start Twitter Stream
python twitter_stream.py
```

**Expected Output:**
```
============================================================
Twitter Sentiment Analysis - Stream Component
============================================================
Authenticating with Twitter API v2...
✓ Authentication successful
✓ Connected to socket server at localhost:9999
Starting tweet stream...
Query: #python OR #AI OR #MachineLearning OR #DataScience lang:en
Batching tweets every 100 tweets or on interval...
Tweet received: "Just learned Python for data science..."
Sent 5 tweets to socket
```

**Important:** Keep this window open. This streams tweets from Twitter.

---

### Step 3: Start Dashboard (Terminal 3)

**After Spark and Stream are running, start this**

```bash
# New Terminal Window
cd TwitterSentimentAnalysis\dashboard

# Start Flask Dashboard
python app.py
```

**Expected Output:**
```
============================================================
Starting Sentiment Analysis Dashboard
============================================================
Dashboard running at http://0.0.0.0:5000
Press Ctrl+C to stop
```

**Important:** Keep this window open. This serves the web interface.

---

### Step 4: View Dashboard (Browser)

**After all three services are running:**

1. Open your web browser
2. Go to: `http://localhost:5000`
3. You should see:
   - 📊 Real-time sentiment statistics
   - 📈 Bar chart with counts
   - 🎯 Pie chart with percentages
   - 🔄 Auto-refreshing every 2 seconds

---

## Data Flow Diagram

```
┌──────────────────┐
│  Twitter API     │
│  Stream #AI      │
│  #DataScience    │
└────────┬─────────┘
         │
         ↓
┌──────────────────────────────┐
│  twitter_stream.py           │
│  - Collect tweets            │
│  - Buffer them               │
│  - Send to socket            │
└────────┬─────────────────────┘
         │
         ↓ (localhost:9999)
┌──────────────────────────────┐
│  Socket Server               │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│  spark_streaming_app.py              │
│  - Receive tweet batch               │
│  - Clean & preprocess                │
│  - Load ML model                     │
│  - Predict sentiment (0,1,2)         │
│  - Count sentiments                  │
│  - Save to JSON                      │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│  output/sentiment_counts.json        │
│  {                                   │
│    "positive": 45,                   │
│    "negative": 12,                   │
│    "neutral": 33,                    │
│    "total_tweets": 90,               │
│    "batches_processed": 9            │
│  }                                   │
└────────┬─────────────────────────────┘
         │
         ↓ (Auto-refresh 2s)
┌──────────────────────────────────────┐
│  dashboard/app.py (Flask)            │
│  - Read JSON                         │
│  - Serve API endpoints               │
└────────┬─────────────────────────────┘
         │
         ↓ (http://localhost:5000)
┌──────────────────────────────────────┐
│  Browser Dashboard                   │
│  - Display charts                    │
│  - Show statistics                   │
│  - Real-time updates                 │
└──────────────────────────────────────┘
```

---

## Monitoring & Logs

### Check Sentiment Counts (Real-time)
```bash
# View current statistics
type output\sentiment_counts.json
```

### View Logs

**Spark Streaming:**
```bash
type logs\spark_streaming.log
```

**Twitter Stream:**
```bash
type logs\twitter_stream.log
```

**Model Training:**
```bash
type logs\sentiment_analysis.log
```

---

## Troubleshooting During Execution

### Terminal 1 (Spark): "Model not found"
**Issue:** `FileNotFoundError: Model not found`

**Solution:**
```bash
# Run in new terminal
python train_model.py
```

### Terminal 2 (Stream): "Socket connection refused"
**Issue:** `ConnectionRefusedError: Socket server not running`

**Solution:**
- Ensure Terminal 1 (Spark) is running
- Check if spark_streaming_app.py shows "Listening for tweets on localhost:9999"
- Wait 5 seconds for socket to initialize

### Terminal 2 (Stream): "Twitter API authentication failed"
**Issue:** `tweepy.errors.Unauthorized`

**Solution:**
- Verify Twitter API credentials in `config.py`
- Check TWITTER_BEARER_TOKEN is not "your_bearer_token_here"
- Get new Bearer Token from Twitter Developer Dashboard

### Terminal 3 (Dashboard): "Port 5000 already in use"
**Issue:** `Address already in use`

**Solution:**
Option A: Change port in `config.py`
```python
FLASK_PORT = 5001  # Change from 5000
```

Option B: Kill process using port 5000
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Browser: "Connection refused" at localhost:5000
**Issue:** Cannot connect to dashboard

**Solution:**
- Ensure Terminal 3 (Flask) is running
- Check if output shows "Dashboard running at http://0.0.0.0:5000"
- Try: `http://127.0.0.1:5000` instead of `localhost:5000`
- Wait 5 seconds for Flask to fully initialize

### Dashboard shows "0" for all counts
**Issue:** No data being processed

**Possible causes:**
1. Spark is running but not receiving tweets
   - Check if Twitter Stream (Terminal 2) is running
   - Verify Twitter API credentials

2. Tweets are not being classified
   - Check Spark logs: `type logs\spark_streaming.log`
   - Ensure model.pkl exists

3. JSON not being updated
   - Check permissions on `output/` folder
   - Verify Spark process has write access

**Solution:**
- Wait 30+ seconds for tweets to arrive and be processed
- Check all three terminals are running
- Review logs for error messages

---

## Expected Output Progression

### T = 0-10 seconds
```
Status: All services starting
Spark: Listening for tweets
Stream: Connecting to Twitter
Dashboard: Loading...
```

### T = 10-30 seconds
```
Stream: Connected, waiting for tweets
Spark: Waiting for batch
Dashboard: Showing 0 tweets
```

### T = 30-60 seconds
```
Stream: "Sent 5 tweets to socket"
Spark: "Processing batch with 5 tweets"
Dashboard: Showing counts update
```

### T = 60+ seconds
```
Stream: "Sent 10 tweets to socket"
Spark: "Processing batch with 10 tweets"
Dashboard: Real-time chart updates every 2s
```

---

## Performance Metrics

| Metric | Expected | Units |
|--------|----------|-------|
| Model Loading | 1-2 | seconds |
| Batch Processing | 5-15 | tweets per batch |
| Batch Interval | 10 | seconds |
| Dashboard Refresh | 2 | seconds |
| Flask Startup | 2-3 | seconds |
| API Response Time | 50-200 | milliseconds |

---

## System Requirements During Execution

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Spark Streaming | 1-2 cores | 500-800 MB | - |
| Twitter Stream | 0.1 cores | 50-100 MB | - |
| Flask Dashboard | 0.1 cores | 50-100 MB | - |
| **Total** | 1-3 cores | 600-1000 MB | - |

---

## Stopping the System

### Proper Shutdown Sequence

1. **Terminal 3 (Dashboard):**
   ```
   Press Ctrl+C
   ```

2. **Terminal 2 (Stream):**
   ```
   Press Ctrl+C
   ```

3. **Terminal 1 (Spark):**
   ```
   Press Ctrl+C
   ```

Expected messages:
```
Shutting down gracefully...
✓ Service stopped
```

---

## Testing Without Live Twitter

For testing without Twitter API:

### Create Mock Data
```bash
python train_model.py  # Creates sample tweets in data/tweets.csv
```

### Modify twitter_stream.py
Add test tweets to mock streaming:
```python
# Replace live stream with sample tweets
test_tweets = [
    "I love this amazing product",
    "This is terrible",
    "It's okay"
]
```

### Expected Dashboard Updates
- Every 10 seconds: sentiment counts update
- Charts update in real-time
- 2-second refresh rate works

---

## Dashboard Features

### Real-Time Statistics
- **Positive Count**: Number of positive tweets
- **Negative Count**: Number of negative tweets
- **Neutral Count**: Number of neutral tweets
- **Total Count**: All tweets processed

### Charts
- **Bar Chart**: Sentiment distribution by count
- **Pie Chart**: Sentiment distribution by percentage

### Auto-Refresh
- Updates every 2 seconds
- Shows last update time
- Displays batch count

### Status Indicators
- 🟢 Connected: System active
- 🔴 Disconnected: System idle
- Last updated timestamp

---

## Advanced Configuration

### Change Batch Interval
Edit `config.py`:
```python
BATCH_INTERVAL = 5  # 5 seconds (default 10)
```

### Change Keywords
Edit `config.py`:
```python
STREAM_KEYWORDS = ["#Python", "#AI", "#ML"]
```

### Change Dashboard Port
Edit `config.py`:
```python
FLASK_PORT = 8080  # Port (default 5000)
```

---

## Example Console Output

### Terminal 1: Spark Streaming
```
============================================================
Twitter Sentiment Analysis - Spark Streaming Component
============================================================
[2024-01-15 10:30:45] Loading sentiment model...
[2024-01-15 10:30:46] ✓ Model and vectorizer loaded successfully
[2024-01-15 10:30:47] Creating Spark Streaming context...
[2024-01-15 10:30:48] ✓ Streaming context created (batch interval: 10s)
[2024-01-15 10:30:48] Listening for tweets on localhost:9999
[2024-01-15 10:30:49] Starting Spark Streaming...
[2024-01-15 10:30:49] Press Ctrl+C to stop
[2024-01-15 10:31:00] Processing batch with 15 tweets
[2024-01-15 10:31:00] Tweet: "I love Python..." -> Sentiment: 2
[2024-01-15 10:31:00] Tweet: "Terrible bug..." -> Sentiment: 0
[2024-01-15 10:31:00] Stats saved: {'positive': 8, 'negative': 4, 'neutral': 3, ...}
```

### Terminal 2: Twitter Stream
```
============================================================
Twitter Sentiment Analysis - Stream Component
============================================================
[2024-01-15 10:30:45] Authenticating with Twitter API v2...
[2024-01-15 10:30:46] ✓ Authentication successful
[2024-01-15 10:30:47] ✓ Connected to socket server at localhost:9999
[2024-01-15 10:30:48] Starting tweet stream...
[2024-01-15 10:30:48] Query: #python OR #AI... lang:en
[2024-01-15 10:30:50] Tweet received: "Just learning Python..."
[2024-01-15 10:30:55] Sent 15 tweets to socket
```

### Terminal 3: Flask Dashboard
```
============================================================
Starting Sentiment Analysis Dashboard
============================================================
[2024-01-15 10:30:45] * Running on http://0.0.0.0:5000
[2024-01-15 10:30:46] * WARNING: This is a development server...
[2024-01-15 10:30:50] 127.0.0.1 - - [15/Jan/2024 10:30:50] "GET / HTTP/1.1" 200 -
[2024-01-15 10:30:51] 127.0.0.1 - - [15/Jan/2024 10:30:51] "GET /api/sentiment-summary HTTP/1.1" 200 -
```

---

## Next Steps After Getting It Running

1. ✅ Customize keywords in `config.py`
2. ✅ Train with your own dataset
3. ✅ Deploy to cloud (AWS, Azure, GCP)
4. ✅ Add database storage (PostgreSQL, MongoDB)
5. ✅ Implement WebSockets for live updates
6. ✅ Add sentiment history & trends
7. ✅ Create alerts for sentiment spikes

---

## Performance Optimization Tips

1. **Increase Batch Interval** if CPU usage is high
   ```python
   BATCH_INTERVAL = 20  # Process less frequently
   ```

2. **Reduce Stream Keywords** to get fewer tweets
   ```python
   STREAM_KEYWORDS = ["#AI"]  # Fewer matches
   ```

3. **Optimize Model** for faster predictions
   - Use fewer TF-IDF features
   - Use simpler model (Naive Bayes)

4. **Monitor Resources**
   - Check Task Manager
   - Close other applications
   - Ensure adequate RAM

---

**Total Execution Time:** 5-10 minutes after setup  
**Dashboard Response Time:** <1 second  
**Tweet Processing Latency:** 10-30 seconds  

Good luck! 🚀

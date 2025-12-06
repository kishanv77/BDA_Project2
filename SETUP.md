# Windows Installation & Setup Guide

## Complete Step-by-Step Setup for Windows 10/11

### ✅ Prerequisites Checklist

- [ ] Windows 10/11 (64-bit)
- [ ] Administrator access
- [ ] Internet connection
- [ ] ~5GB free disk space

---

## Phase 1: Install Java (Required)

### Step 1.1: Download Java JDK

1. Go to [https://www.oracle.com/java/technologies/downloads/](https://www.oracle.com/java/technologies/downloads/)
2. Select "Java SE 11" or newer
3. Download "Windows x64 Installer"
4. **Save and note the file path**

### Step 1.2: Install Java

1. Run the installer (`.exe` file)
2. Click "Next" through the installation wizard
3. Keep the default installation path: `C:\Program Files\Java\jdk-XX`
4. Complete installation

### Step 1.3: Set Java Environment Variable

1. **Open Environment Variables:**
   - Right-click "This PC" or "My Computer"
   - Select "Properties"
   - Click "Advanced system settings" (left panel)
   - Click "Environment Variables" button

2. **Add JAVA_HOME:**
   - Under "System variables" section, click "New"
   - Variable name: `JAVA_HOME`
   - Variable value: `C:\Program Files\Java\jdk-11` (adjust version number)
   - Click "OK"

3. **Add Java to PATH:**
   - Select "Path" variable
   - Click "Edit"
   - Click "New"
   - Add: `%JAVA_HOME%\bin`
   - Click "OK" → "OK" → "OK"

4. **Restart your computer**

### Step 1.4: Verify Java Installation

Open Command Prompt and run:
```bash
java -version
```

**Expected output:**
```
java version "11.0.XX" 2024-XX-XX
Java(TM) SE Runtime Environment (build 11.0.XX)
Java HotSpot(TM) 64-Bit Server VM (build 11.0.XX, mixed mode)
```

---

## Phase 2: Install Python & Dependencies

### Step 2.1: Download Python

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download Python 3.9 or newer (64-bit)
3. **Note: Download the latest stable version**

### Step 2.2: Install Python

1. Run the Python installer
2. **✅ IMPORTANT: Check "Add Python to PATH"**
3. Click "Install Now"
4. Wait for installation to complete

### Step 2.3: Verify Python Installation

Open Command Prompt and run:
```bash
python --version
pip --version
```

**Expected output:**
```
Python 3.11.X
pip XX.X from C:\Users\...\AppData\Local\Programs\Python\Python311\lib\site-packages\pip
```

---

## Phase 3: Project Setup

### Step 3.1: Prepare Project Directory

1. Extract/Download the project
2. Open Command Prompt
3. Navigate to project directory:
   ```bash
   cd path\to\TwitterSentimentAnalysis
   ```

### Step 3.2: Create Virtual Environment

```bash
python -m venv venv
```

This creates an isolated Python environment.

### Step 3.3: Activate Virtual Environment

```bash
venv\Scripts\activate
```

**You should see `(venv)` at the start of each command line.**

### Step 3.4: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 3.5: Install Dependencies

```bash
pip install -r requirements.txt
```

**Wait for all packages to install (5-10 minutes)**

---

## Phase 4: Configure Twitter API

### Step 4.1: Create Twitter Developer Account

1. Go to [https://developer.twitter.com/](https://developer.twitter.com/)
2. Sign up or log in with Twitter account
3. Create a new app in Developer Portal

### Step 4.2: Get API Credentials

After app creation, go to "Keys and tokens" and get:
- **API Key**
- **API Secret**
- **Access Token**
- **Access Token Secret**
- **Bearer Token** (Regenerate if needed)

### Step 4.3: Add Credentials to config.py

1. Open `config.py` in a text editor
2. Find these lines:
   ```python
   TWITTER_BEARER_TOKEN = "your_bearer_token_here"
   TWITTER_API_KEY = "your_api_key_here"
   TWITTER_API_SECRET = "your_api_secret_here"
   TWITTER_ACCESS_TOKEN = "your_access_token_here"
   TWITTER_ACCESS_TOKEN_SECRET = "your_access_token_secret_here"
   ```
3. Replace with your actual credentials
4. **Save the file**

---

## Phase 5: Train the Model

### Step 5.1: Run Training Script

In Command Prompt (with virtual environment activated):

```bash
python train_model.py
```

### Step 5.2: Expected Output

```
Loading dataset from ./data/tweets.csv
Dataset loaded: 50 samples
Preprocessing tweets...
Vectorizing text using TF-IDF...
Training Logistic Regression model...

Model Accuracy: 0.85

Saving model to ./models/model.pkl
Saving vectorizer to ./models/vectorizer.pkl
✓ Model training completed successfully!
```

**Files created:**
- `models/model.pkl`
- `models/vectorizer.pkl`

---

## Phase 6: Run the System

### Option A: Run All Components Manually

**Terminal 1 - Spark Streaming:**
```bash
python spark_streaming_app.py
```

**Terminal 2 - Twitter Stream:**
```bash
python twitter_stream.py
```

**Terminal 3 - Dashboard:**
```bash
cd dashboard
python app.py
```

**Browser:**
Open: `http://localhost:5000`

### Option B: Quick Start Batch Script (Windows)

Create `run_all.bat`:

```batch
@echo off
echo Starting Twitter Sentiment Analysis System...
echo.

start "Spark Streaming" python spark_streaming_app.py
timeout /t 3
start "Twitter Stream" python twitter_stream.py
timeout /t 3
cd dashboard
start "Dashboard" python app.py

echo.
echo All services started! Open browser to http://localhost:5000
pause
```

Then run: `run_all.bat`

---

## 🔍 Verification Checklist

After setup, verify each component:

### ✅ Java Installed
```bash
java -version
```
Should show Java version 11+

### ✅ Python Installed
```bash
python --version
```
Should show Python 3.9+

### ✅ Virtual Environment Active
Command prompt should show `(venv)` prefix

### ✅ Dependencies Installed
```bash
pip list
```
Should show: pyspark, tweepy, flask, scikit-learn, etc.

### ✅ Model Trained
Check if these files exist:
- `models/model.pkl`
- `models/vectorizer.pkl`

### ✅ Config Updated
Open `config.py` and verify:
- Twitter API credentials are added
- Not showing "your_XXX_here" placeholders

---

## 🚀 Running the System

### Complete Execution Flow

```
1. Open Command Prompt
   ↓
2. Activate virtual environment: venv\Scripts\activate
   ↓
3. Terminal 1: python spark_streaming_app.py
   (Wait for "Listening for tweets..." message)
   ↓
4. Terminal 2: python twitter_stream.py
   (Wait for "Connected to socket server..." message)
   ↓
5. Terminal 3: cd dashboard && python app.py
   (Wait for "Dashboard running at..." message)
   ↓
6. Open browser: http://localhost:5000
   ↓
7. Watch real-time sentiment analysis!
```

---

## ⚡ Performance Tips for Windows

1. **Close unnecessary programs** to free RAM
2. **Use Command Prompt**, not PowerShell (faster)
3. **Disable antivirus scanning** on project folder (optional)
4. **Run as Administrator** if you encounter permission errors
5. **Monitor Task Manager** to check resource usage

---

## 🐛 Common Windows Issues & Solutions

### Issue: "Python is not recognized"
**Solution:**
- Python not in PATH
- Restart computer after installation
- Reinstall Python with "Add to PATH" checked

### Issue: "java is not recognized"
**Solution:**
- JAVA_HOME not set
- Restart Command Prompt after setting environment variable
- Restart computer

### Issue: "Permission denied" errors
**Solution:**
- Run Command Prompt as Administrator
- Check file permissions in folder properties
- Try: `icacls "C:\path\to\project" /grant:r %USERNAME%:F`

### Issue: "Port 5000 already in use"
**Solution:**
- Change port in `config.py`
- Or find process: `netstat -ano | findstr :5000`
- Kill process: `taskkill /PID <PID> /F`

### Issue: "Module not found" errors
**Solution:**
- Ensure virtual environment is activated: `(venv)` should show
- Reinstall: `pip install -r requirements.txt`
- Check Python version: `python --version`

### Issue: "JAVA_HOME not found"
**Solution:**
- Set in environment variables (see Phase 1)
- Verify path exists: `C:\Program Files\Java\jdk-11`
- Restart computer after setting

---

## 📁 Final Project Structure

After setup, your folder should look like:

```
TwitterSentimentAnalysis/
├── venv/                    # Virtual environment (auto-created)
├── config.py               # ✅ Configured with your API keys
├── train_model.py
├── twitter_stream.py
├── spark_streaming_app.py
├── requirements.txt
│
├── data/
│   └── tweets.csv         # ✅ Sample data (auto-created)
│
├── models/
│   ├── model.pkl          # ✅ Created by train_model.py
│   └── vectorizer.pkl     # ✅ Created by train_model.py
│
├── logs/
│   ├── sentiment_analysis.log
│   ├── spark_streaming.log
│   └── twitter_stream.log
│
├── output/
│   └── sentiment_counts.json  # ✅ Created during streaming
│
├── dashboard/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── style.css
│       └── dashboard.js
│
└── README.md
```

---

## 📞 Support

If stuck at any point:

1. **Check logs** in `logs/` directory
2. **Run individual scripts** to isolate issues
3. **Verify all files exist** after each step
4. **Check environment variables** in System Properties
5. **Restart computer** after major changes

---

## ✨ Next Steps After Setup

1. ✅ Run `python train_model.py`
2. ✅ Start `spark_streaming_app.py`
3. ✅ Start `twitter_stream.py`
4. ✅ Start `dashboard/app.py`
5. ✅ Open `http://localhost:5000` in browser
6. ✅ Watch real-time sentiment analysis!

---

**Estimated Total Setup Time: 30-45 minutes**

Good luck! 🚀

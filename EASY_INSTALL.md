# Easy Installation Guide for Non-Programmers

**For psychology/counseling students who just want to practice diagnosis!**

No coding experience needed. Follow these step-by-step instructions with screenshots.

---

## 📋 **Before You Start - Do You Have These?**

### Check if you already have Python and Node:

**On Mac:**
1. Open "Terminal" (search in Spotlight)
2. Type: `python3 --version` and press Enter
3. Type: `node --version` and press Enter

**On Windows:**
1. Open "Command Prompt" (search in Start menu)
2. Type: `python --version` and press Enter
3. Type: `node --version` and press Enter

**What you need:**
- Python 3.8 or higher (e.g., "Python 3.12.3" ✅)
- Node.js 14 or higher (e.g., "v25.0.0" ✅)

### Don't have them? Install here:
- **Python**: Download from https://www.python.org/downloads/
  - Click "Download Python 3.x" (big yellow button)
  - Run the installer
  - ⚠️ **Windows**: Check "Add Python to PATH" during installation!

- **Node.js**: Download from https://nodejs.org/
  - Click "Download" (LTS version recommended)
  - Run the installer

---

## 📥 **Step 1: Download the App**

### Option A: Direct Download (Easiest)
1. Go to: https://github.com/endrawes0/diagnosis-quiz-tool
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the file to your Desktop or Documents folder

### Option B: Using Git (If you know how)
```bash
git clone https://github.com/endrawes0/diagnosis-quiz-tool.git
cd diagnosis-quiz-tool
```

---

## ⚙️ **Step 2: First-Time Setup** (Only needed once!)

### On Mac/Linux:

Open Terminal and navigate to the folder:
```bash
cd ~/Desktop/diagnosis-quiz-tool-master
```

Run this setup script (copy and paste all at once):
```bash
# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

echo "✅ Setup complete! You're ready to go."
```

### On Windows:

Open Command Prompt and navigate to the folder:
```cmd
cd %USERPROFILE%\Desktop\diagnosis-quiz-tool-master
```

Run this setup script (copy and paste all at once):
```cmd
REM Install Python dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM Install frontend dependencies
cd frontend
npm install
cd ..

echo Setup complete! You're ready to go.
```

**This will take 2-5 minutes.** You'll see lots of text - that's normal!

---

## 🚀 **Step 3: Starting the App**

### The Easy Way (Recommended):

**We'll create a simple startup script for you!**

#### On Mac/Linux:
Create a file called `START_APP.sh` in the main folder with this content:
```bash
#!/bin/bash
echo "🚀 Starting Diagnosis Quiz Tool..."
echo ""
echo "📍 The app will open at: http://localhost:3000"
echo "   (Your browser will open automatically)"
echo ""
echo "⚠️  Keep this window open while using the app"
echo "   Press Ctrl+C to stop"
echo ""

# Start backend
source venv/bin/activate
python3 -m flask run --host=0.0.0.0 --port=5000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd frontend
npm start

# Cleanup
kill $BACKEND_PID
```

Then make it executable and run:
```bash
chmod +x START_APP.sh
./START_APP.sh
```

#### On Windows:
Create a file called `START_APP.bat` with this content:
```batch
@echo off
echo Starting Diagnosis Quiz Tool...
echo.
echo The app will open at: http://localhost:3000
echo (Your browser will open automatically)
echo.
echo Keep this window open while using the app
echo Press Ctrl+C to stop
echo.

REM Start backend
call venv\Scripts\activate
start /B python -m flask run --host=0.0.0.0 --port=5000

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start frontend
cd frontend
npm start
```

Then just double-click `START_APP.bat` to start!

---

## 🎓 **Step 4: Using the App**

1. Your web browser will automatically open to http://localhost:3000
2. If it doesn't, manually open your browser and go to: `http://localhost:3000`

3. You'll see the Diagnosis Quiz Tool homepage!

4. Click **"Start Quiz"** to begin

5. Configure your quiz:
   - Choose difficulty (Easy, Medium, Hard)
   - Select diagnostic categories (Depression, Anxiety, etc.)
   - Set number of questions
   - Click "Generate Quiz"

6. Take the quiz and see your results!

---

## 🛑 **Step 5: Stopping the App**

When you're done:
- Go back to the terminal/command prompt window
- Press **Ctrl+C** (hold Control and press C)
- Close the terminal window

---

## 🆘 **Common Problems & Solutions**

### "Command not found" or "Python not recognized"
**Solution**: Python/Node.js not installed correctly
- Reinstall Python/Node.js
- On Windows: Make sure you checked "Add to PATH" during installation
- Restart your terminal/command prompt after installing

### "Port 3000 is already in use"
**Solution**: The app is already running somewhere
- Close all terminal windows
- Restart your computer
- Try again

### "ModuleNotFoundError"
**Solution**: Dependencies not installed
- Make sure you ran the setup (Step 2)
- Try running: `pip install -r requirements.txt` again

### Browser doesn't open automatically
**Solution**: Manually open browser
- Open your web browser (Chrome, Firefox, Safari, etc.)
- Type in address bar: `localhost:3000`
- Press Enter

### "I closed the terminal and now the app doesn't work"
**Solution**: You need to keep the terminal open
- The terminal must stay open while using the app
- Don't close it until you're done
- Think of it like keeping an app "running"

---

## 💡 **Tips for Non-Programmers**

### What is localhost?
- It's like a web address, but only on YOUR computer
- Nobody else can see it
- It's completely private
- The `:3000` is like an apartment number

### Why do I need the terminal open?
- The terminal is running the "engine" of the app
- Like keeping Excel open to use a spreadsheet
- Once you close it, the app stops

### Is my data saved?
- Yes! Your progress is saved automatically
- It's stored in the `data/users/` folder
- As long as you don't delete that folder, your data persists

### Can I use this offline?
- YES! No internet needed (after initial setup)
- Perfect for studying anywhere

---

## 🎬 **Video Tutorial**

**[Coming Soon]** We'll create a video walkthrough showing:
1. Downloading the app
2. Installing prerequisites
3. First-time setup
4. Starting and using the quiz
5. Common troubleshooting

---

## 📧 **Still Stuck?**

Don't worry! Technology can be tricky.

**Contact**: me@andrewwhaddad.com
**Subject**: "Help with Diagnosis Quiz Tool Setup"

Include:
- What operating system you're using (Windows/Mac)
- What step you're stuck on
- Screenshot of any error messages

We'll help you get it working! 🚀

---

**Remember**: You only need to do the setup (Step 2) ONCE. After that, just run the startup script whenever you want to practice!

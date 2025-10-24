# Quick Start Guide - Diagnosis Quiz Tool

**Get started in 5 minutes!** Perfect for academic demonstrations and peer reviews.

**Psychological Disorder Diagnosis Training Tool** - Practice diagnostic skills with DSM-5 based clinical cases.

## 🚀 Prerequisites

- Python 3.8+ installed
- Node.js 14+ and npm installed
- Basic terminal/command line familiarity

## ⚡ Quick Setup (No Authentication Required)

### 1. Clone or Download
```bash
cd diagnosis_quiz_tool
```

### 2. Install Backend Dependencies
```bash
# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Start Backend Server
```bash
# Option A: Using the startup script
./start_server.sh

# Option B: Manual start
source venv/bin/activate
export FLASK_APP=src.app:create_app
export PYTHONPATH=$(pwd):$PYTHONPATH
python3 -m flask run --host=0.0.0.0 --port=5000
```

Backend will be available at: **http://localhost:5000**

### 5. Start Frontend (In a New Terminal)
```bash
cd frontend
npm start
```

Frontend will open automatically at: **http://localhost:3000**

## 🎯 Try It Out!

1. **Open Browser**: Navigate to http://localhost:3000
2. **Generate Quiz**: Click "Start Quiz" and configure options
3. **Take Quiz**: Answer diagnostic questions
4. **View Results**: See your score and performance analytics

## 📋 Quick API Test

Test the backend directly:

```bash
# Health check
curl http://localhost:5000/api/health

# Generate a quiz
curl -X POST http://localhost:5000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"num_questions": 5, "num_choices": 4}'

# Browse cases
curl http://localhost:5000/api/cases?limit=10
```

## ⚙️ Configuration

The app runs in **demo mode by default** (no authentication required).

To customize, edit `.env` file:

```bash
# No authentication (default for academic use)
REQUIRE_AUTH=False
DEMO_MODE=True

# Enable authentication (optional)
REQUIRE_AUTH=True
# Then generate secret keys:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 Features Available

- ✅ **Quiz Generation**: Create custom diagnostic quizzes
- ✅ **Case Browsing**: Explore 119 clinical cases
- ✅ **Multiple Difficulty Levels**: Basic to advanced
- ✅ **Performance Analytics**: Detailed scoring and feedback
- ✅ **15 DSM-5 Categories**: Comprehensive mental health coverage
- ✅ **No Login Required**: Perfect for demonstrations

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Change port in .env file
FLASK_PORT=5001
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Ensure PYTHONPATH is set
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### Frontend Won't Start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📚 Next Steps

- Read [README.md](README.md) for detailed documentation
- See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for API reference
- Check [USER_GUIDE.md](docs/USER_GUIDE.md) for usage instructions
- Review test results: `pytest tests/ -v`

## 🎓 Academic Use

This tool is designed for:
- Psychiatric/psychological education
- Clinical psychology training
- Mental health professional development
- Diagnostic reasoning research
- Psychology curriculum development

**No authentication required for demo mode** - perfect for showing to peers and professors!

## 🆘 Need Help?

- Check logs in `logs/api.log`
- Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Run smoke test: `python smoke_test.py`
- Check server status: `curl http://localhost:5000/api/health`

---

**Ready to share with peers!** The app works out-of-the-box with no configuration needed.

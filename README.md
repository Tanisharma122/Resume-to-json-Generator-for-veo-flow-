# 🎬 VEO Dialogue Generator - Complete System

AI-powered Resume to Video JSON Generator for Google VEO 3.1 & Flow

## 📁 Project Structure

```
veo-dialogue-generator/
├── app.py                      # Flask backend server
├── resume_parser.py            # Resume parsing logic
├── master_builder.py           # Master JSON generator
├── clip_generator.py           # Clip JSON generator
├── rules.py                    # VEO consistency rules
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this!)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore file
├── index.html                  # React frontend UI
├── uploads/                    # Temporary uploads (auto-created)
├── outputs/                    # Generated JSONs (auto-created)
└── README.md                   # This file
```

## 🚀 Quick Start Guide

### **Step 1: Install Python Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: Configure API Key**

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

**Get your Groq API key:** https://console.groq.com/keys

### **Step 3: Start the Backend Server**

```bash
python app.py
```

The server will start on `https://resume-to-json-generator-for-veo-flow.onrender.com`

### **Step 4: Open the Frontend**

Open `index.html` in your web browser, or use a local server:

```bash
# Option 1: Direct file open
open index.html

# Option 2: Python HTTP server
python -m http.server 8080
# Then visit: http://localhost:8080/index.html

# Option 3: VS Code Live Server
# Right-click index.html → "Open with Live Server"
```

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Groq API Key**: Free tier available
- **Modern Browser**: Chrome, Firefox, Safari, Edge

## 🔧 How It Works

### **Flow Diagram**

```
User Upload Resume (PDF/DOCX)
        ↓
Backend Parses Resume (resume_parser.py)
        ↓
AI Generates Video Script
        ↓
User Configures Settings (tone, speed, clips)
        ↓
User Uploads Reference Image
        ↓
Master JSON Builder (master_builder.py)
        ↓
Clip JSON Generator (clip_generator.py)
        ↓
Download master.json + clip JSONs
        ↓
Use in Google VEO/Flow
```

### **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/test` | GET | Test API configuration |
| `/api/parse-resume` | POST | Parse uploaded resume |
| `/api/generate-description` | POST | Generate video script |
| `/api/generate` | POST | Generate master & clip JSONs |

## 🎯 Features

- ✅ **Resume Parsing**: Extracts structured data from PDF/DOCX
- ✅ **AI Script Generation**: Creates professional video scripts
- ✅ **Speed Control**: 1x, 1.5x, 2x speaking speeds
- ✅ **Voice Tones**: Professional, Friendly, Confident, etc.
- ✅ **Background Music**: Optional 15% volume ambient music
- ✅ **99% Consistency**: Face and voice locked across clips
- ✅ **VEO 3.1 Ready**: Optimized for Google VEO & Flow

## 📝 Configuration Options

### **Speaking Speeds**

| Speed | Words/Second | Target Words | Duration |
|-------|--------------|--------------|----------|
| 1x | 3.0 | 24 | ~8s |
| 1.5x | 4.5 | 36 | ~8s |
| 2x | 5.4 | 43 | ~8s |

### **Voice Tones**

- 💼 Professional
- 😊 Friendly
- 💪 Confident
- 🎉 Enthusiastic
- 🤗 Warm

## 🐛 Troubleshooting

### **"GROQ_API_KEY not configured"**

Solution: Create `.env` file with your API key

```bash
echo "GROQ_API_KEY=your_key_here" > .env
```

### **"Module not found" errors**

Solution: Install dependencies

```bash
pip install -r requirements.txt
```

### **"Connection refused" on frontend**

Solution: Make sure Flask is running on port 5001

```bash
python app.py
```

### **CORS errors in browser**

Solution: flask-cors is installed and enabled in app.py

### **Resume parsing fails**

- Check file format (PDF or DOCX only)
- Check file size (under 10MB)
- Ensure file is not password-protected

## 🔒 Security Notes

- Never commit `.env` file to Git
- API keys are stored securely in `.env`
- Uploaded files are temporary (deleted after processing)
- Use environment variables for all sensitive data

## 📦 Deployment Options

### **Option 1: Local Deployment**

Just run `python app.py` - suitable for personal use

### **Option 2: Heroku**

```bash
heroku create your-app-name
heroku config:set GROQ_API_KEY=your_key
git push heroku main
```

### **Option 3: Docker**

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### **Option 4: Railway/Render**

- Push to GitHub
- Connect repository
- Add `GROQ_API_KEY` environment variable
- Deploy automatically

## 📊 Output Files

### **master.json**

Contains complete video configuration:
- Project metadata
- Person identity
- Visual settings
- Audio profile
- Timing configuration

### **clip_X.json**

Individual clip files containing:
- Dialogue text
- Word count
- Timing information
- VEO prompts
- Keyframes

## 🎬 Using Generated JSONs in VEO/Flow

1. Download all JSON files
2. Access Google VEO 3.1 or Flow
3. For each clip:
   - Copy dialogue from `clip_X.json`
   - Use VEO prompt from JSON
   - Upload reference image
   - Generate video
4. Combine clips in video editor

## 🤝 Contributing

Feel free to fork and improve!

## 📄 License

MIT License - use freely for personal and commercial projects

## 🆘 Support

For issues:
1. Check Troubleshooting section
2. Verify API key is configured
3. Check console for error messages

## 🎓 Technical Details

- **Backend**: Flask (Python)
- **Frontend**: React (via CDN)
- **AI**: Groq API (Llama 3.3 70B)
- **File Parsing**: PyPDF2, python-docx
- **Consistency Rules**: Locked at 99% similarity

---

**Made with ❤️ for professional AI video generation**
=======
# Resume-to-json-Generator-for-veo-flow-
Resume to JSON Generator for Veo/Flow converts resume content into structured JSON and uses prompts to generate professional, personalized videos such as self-introductions, portfolio videos, and career highlights using Veo/Flow.
>>>>>>> 6f3527cb73c7b7bdc4f8fccb70cf57d345a11e09

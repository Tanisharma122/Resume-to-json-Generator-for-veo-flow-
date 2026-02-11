# 🛠️ VEO Dialogue Generator - Tech Stack

## Backend (Python)

### Core Framework
- **Flask** - Web server and REST API framework
- **Flask-CORS** - Cross-origin resource sharing for frontend communication

### AI & LLM
- **Groq API** - LLM provider (Llama 3.3 70B model)
  - Resume parsing and data extraction
  - Person detail extraction
  - Video script generation

### Document Processing
- **PyPDF2** - PDF file parsing and text extraction
- **python-docx** - DOCX file parsing and text extraction

### Utilities
- **python-dotenv** - Environment variable management
- **base64** (built-in) - Image encoding/decoding
- **datetime** (built-in) - Timestamp handling
- **tempfile** (built-in) - Temporary file management
- **json** (built-in) - JSON serialization
- **re** (built-in) - Regular expressions for text parsing

---

## Frontend (JavaScript/React)

### Core Library
- **React 18** - UI framework (loaded via CDN)
- **ReactDOM 18** - React rendering engine

### UI Components
- **Lucide React** - Icon library for modern UI icons

### Styling
- **Tailwind CSS 3.4** - Utility-first CSS framework (via CDN)
- **Custom CSS** - Gradient animations and custom styles

### Browser APIs
- **Fetch API** - HTTP requests to Flask backend
- **FileReader API** - Client-side file reading
- **Canvas API** - Image preview rendering

---

## File Formats

### Input Formats
- **PDF** (.pdf) - Resume uploads
- **DOCX** (.docx) - Resume uploads
- **JPEG/PNG** - Reference images (base64 encoded)

### Output Formats
- **JSON** - master.json and clip JSONs for VEO

---

## Architecture Pattern

```
┌─────────────────┐
│  React Frontend │ (index_premium_final.html)
│   (Port 8080)   │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│  Flask Backend  │ (app.py)
│   (Port 5001)   │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────────┐
    │         │            │              │
┌───▼───┐ ┌──▼──┐ ┌───────▼────┐ ┌──────▼──────┐
│Resume │ │Master│ │Clip        │ │Rules Engine │
│Parser │ │Builder│ │Generator  │ │(Immutable)  │
└───┬───┘ └──┬──┘ └───────┬────┘ └──────┬──────┘
    │        │            │              │
    └────────┴────────────┴──────────────┘
                    │
            ┌───────▼────────┐
            │   Groq API     │
            │ (Llama 3.3 70B)│
            └────────────────┘
```

---

## Key Dependencies

### Python (requirements.txt)
```
flask>=2.3.0
flask-cors>=4.0.0
groq>=0.4.0
PyPDF2>=3.0.0
python-docx>=0.8.11
python-dotenv>=1.0.0
```

### JavaScript (CDN)
```
react@18.2.0
react-dom@18.2.0
lucide-react@latest
tailwindcss@3.4.0
```

---

## External Services

### Required
- **Groq API** - LLM inference (API key required)
  - Endpoint: `https://api.groq.com`
  - Model: `llama-3.3-70b-versatile`

### Optional
- **Google VEO 3.1** - Final video generation (separate service)
- **Google Flow** - Alternative video generation platform

---

## Configuration

### Environment Variables (.env)
```bash
GROQ_API_KEY=your_api_key_here
```

### Ports
- **Backend**: 5001 (Flask)
- **Frontend**: 8080 (HTTP server) or direct file open

---

## Data Flow

1. **Resume Upload** → PyPDF2/python-docx → Raw Text
2. **Text Processing** → Groq API → Structured JSON
3. **Script Generation** → Groq API → Video Description
4. **Image Upload** → Base64 → Temporary Storage
5. **Master JSON** → Rules Engine + LLM → master.json
6. **Clip Generation** → Groq API → clip_1.json, clip_2.json, etc.
7. **Download** → User receives all JSONs

---

## Security

- **dotenv** - Secrets management
- **CORS** - Cross-origin security
- **Base64** - Secure image encoding
- **Temporary Files** - Auto-cleanup after processing

---

## Performance

- **Streaming** - File uploads handled in chunks
- **Async Processing** - Non-blocking API calls
- **Rate Limiting** - Groq API limits respected
- **Caching** - Temporary file storage for efficiency

---

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Required Features:**
- FileReader API
- Fetch API
- ES6+ JavaScript
- CSS Grid/Flexbox

---

## Deployment Options

1. **Local**: Python + HTTP server
2. **Heroku**: Flask deployment
3. **Railway/Render**: Auto-deploy from Git
4. **Docker**: Containerized deployment
5. **Vercel/Netlify**: Frontend only (requires separate backend)

---

**Last Updated**: February 2026  
**Version**: 1.0  
**License**: MIT

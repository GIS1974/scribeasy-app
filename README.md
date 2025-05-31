# ScribeEasy - Audio/Video Transcription App

A modern web application that enables users to upload audio or video files, transcribe them using AssemblyAI, and download the resulting transcriptions and subtitles.

## Features

- 🎵 Support for multiple file formats (.mp4, .mkv, .mp3)
- 🤖 High-quality transcription using AssemblyAI's slam-1 model (highest accuracy for English-only)
- 📝 Multiple output formats (SRT, VTT, TXT)
- 👀 Subtitle preview functionality
- 🔒 Privacy-focused (no permanent file storage)
- 📱 Responsive, modern UI
- ⚡ Real-time transcription progress tracking

## Architecture

- **Frontend**: React with Vite
- **Backend**: Python FastAPI with AssemblyAI SDK
- **Communication**: RESTful APIs
- **File Handling**: Temporary storage with immediate cleanup

## Project Structure

scribeasy-app/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── config.py           # Configuration
│   ├── models.py           # Data models
│   ├── services/           # Business logic
│   ├── utils/              # Utilities
│   └── requirements.txt    # Dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main component
│   │   ├── components/     # UI components
│   │   ├── services/       # API layer
│   │   └── utils/          # Utilities
│   └── package.json        # Dependencies
├── README.md               # Documentation
├── docker-compose.yml      # Docker setup
└── setup.py               # Setup script

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- AssemblyAI API key

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd scribeasy-app
```

### 2. Install Dependencies

Install all dependencies at once:
```bash
npm run install:all
```

Or install manually:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

**Root (for development scripts):**
```bash
npm install
```

### 3. Configure Environment

Create `.env` file in backend directory:
```
ASSEMBLYAI_API_KEY=your_api_key_here
UPLOAD_DIR=./temp_uploads
MAX_FILE_SIZE=1000000000  # 1000MB
```

### 4. Start Development Servers

**Option 1: NPM Script (Recommended)**
```bash
npm run dev
```

**Option 2: Platform-specific scripts**
- Windows: Double-click `dev.bat` or run in command prompt
- Unix/Linux/macOS: `./dev.sh`
- Cross-platform: `node dev.js`

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

> 📝 See [DEV_SCRIPTS.md](DEV_SCRIPTS.md) for detailed information about development scripts.

## Usage

1. **Upload**: Select an audio/video file (.mp4, .mkv, .mp3)
2. **Transcribe**: Wait for AssemblyAI to process your file
3. **Preview**: View a preview of the generated subtitles
4. **Download**: Get your transcription in SRT, VTT, or TXT format

## API Endpoints

- `POST /upload` - Upload and start transcription
- `GET /status/{job_id}` - Check transcription status
- `GET /download/{job_id}/{format}` - Download transcription

## Security Features

- File type validation
- File size limits
- Temporary file storage
- Input sanitization
- CORS configuration

## Deployment

### Using Docker (Recommended)

```bash
docker-compose up -d
```

### Manual Deployment

1. Set up a reverse proxy (nginx)
2. Configure environment variables
3. Use a process manager (PM2, systemd)
4. Set up SSL certificates

## Environment Variables

### Backend
- `ASSEMBLYAI_API_KEY` - Your AssemblyAI API key
- `UPLOAD_DIR` - Temporary file storage directory
- `MAX_FILE_SIZE` - Maximum upload file size in bytes
- `CORS_ORIGINS` - Allowed CORS origins

### Frontend
- `VITE_API_BASE_URL` - Backend API URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

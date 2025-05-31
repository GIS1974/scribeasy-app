# Development Scripts

This document describes the various scripts available to run both frontend and backend development servers simultaneously.

## Available Scripts

### 1. NPM Scripts (Recommended)
```bash
npm run dev
```
This uses the `concurrently` package to run both servers in the same terminal with colored output.

**Other npm commands:**
- `npm run dev:backend` - Run only the backend server
- `npm run dev:frontend` - Run only the frontend server
- `npm run install:all` - Install dependencies for both frontend and backend
- `npm run install:backend` - Install only backend dependencies
- `npm run install:frontend` - Install only frontend dependencies

### 2. Node.js Script (Cross-platform)
```bash
node dev.js
```
A comprehensive Node.js script that:
- Checks for Python and Node.js installation
- Verifies dependencies are installed
- Runs both servers with colored, timestamped output
- Handles graceful shutdown with Ctrl+C

### 3. Windows Batch Script
```cmd
dev.bat
```
Double-click or run from command prompt. Opens both servers in separate command windows.

### 4. Unix/Linux/macOS Shell Script
```bash
./dev.sh
```
Runs both servers in the same terminal with colored output and proper signal handling.

## Prerequisites

Before running any development script, ensure you have:

### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

### Root Dependencies (for npm scripts)
```bash
npm install
```

## Server URLs

When running the development servers:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

### Python Not Found
- Ensure Python 3.8+ is installed and in your PATH
- On some systems, use `python3` instead of `python`

### Port Already in Use
- Stop any existing servers running on ports 8000 or 5173
- Or modify the ports in the respective configuration files

### Dependencies Not Installed
- Run the install commands listed in Prerequisites
- For backend, ensure you're in a virtual environment if preferred

### Permission Denied (Unix/Linux/macOS)
```bash
chmod +x dev.sh
```

## Stopping the Servers

- **NPM/Node.js/Shell scripts**: Press `Ctrl+C`
- **Windows batch script**: Close the command windows or press `Ctrl+C` in each window

## Development Workflow

1. Install all dependencies:
   ```bash
   npm run install:all
   ```

2. Start development servers:
   ```bash
   npm run dev
   ```

3. Open your browser to http://localhost:5173

4. Make changes to your code - both servers support hot reload

5. Stop servers with `Ctrl+C` when done

#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logWithPrefix(prefix, message, color = colors.reset) {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${colors.bright}[${timestamp}]${colors.reset} ${color}[${prefix}]${colors.reset} ${message}`);
}

// Check if Python is available
function checkPython() {
  return new Promise((resolve) => {
    const pythonCmd = os.platform() === 'win32' ? 'python' : 'python3';
    const python = spawn(pythonCmd, ['--version'], { stdio: 'pipe' });
    
    python.on('close', (code) => {
      resolve(code === 0 ? pythonCmd : null);
    });
    
    python.on('error', () => {
      resolve(null);
    });
  });
}

// Check if Node.js dependencies are installed
function checkNodeDeps() {
  const fs = require('fs');
  return fs.existsSync(path.join(__dirname, 'frontend', 'node_modules'));
}

// Check if Python dependencies are installed
function checkPythonDeps() {
  return new Promise((resolve) => {
    const pythonCmd = os.platform() === 'win32' ? 'python' : 'python3';
    const pip = spawn(pythonCmd, ['-c', 'import fastapi, uvicorn'], { 
      cwd: path.join(__dirname, 'backend'),
      stdio: 'pipe' 
    });
    
    pip.on('close', (code) => {
      resolve(code === 0);
    });
    
    pip.on('error', () => {
      resolve(false);
    });
  });
}

// Start backend server
function startBackend(pythonCmd) {
  log('Starting backend server...', colors.blue);
  
  const backend = spawn(pythonCmd, ['-m', 'uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'], {
    cwd: path.join(__dirname, 'backend'),
    stdio: 'pipe'
  });

  backend.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
      logWithPrefix('BACKEND', message, colors.blue);
    }
  });

  backend.stderr.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
      logWithPrefix('BACKEND', message, colors.red);
    }
  });

  backend.on('close', (code) => {
    logWithPrefix('BACKEND', `Process exited with code ${code}`, colors.red);
  });

  return backend;
}

// Start frontend server
function startFrontend() {
  log('Starting frontend server...', colors.green);
  
  const frontend = spawn('npm', ['run', 'dev'], {
    cwd: path.join(__dirname, 'frontend'),
    stdio: 'pipe',
    shell: true
  });

  frontend.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
      logWithPrefix('FRONTEND', message, colors.green);
    }
  });

  frontend.stderr.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
      logWithPrefix('FRONTEND', message, colors.yellow);
    }
  });

  frontend.on('close', (code) => {
    logWithPrefix('FRONTEND', `Process exited with code ${code}`, colors.red);
  });

  return frontend;
}

// Main function
async function main() {
  log('🚀 ScribeEasy Development Server', colors.bright);
  log('================================', colors.bright);

  // Check Python
  const pythonCmd = await checkPython();
  if (!pythonCmd) {
    log('❌ Python not found. Please install Python 3.8+ and try again.', colors.red);
    process.exit(1);
  }
  log(`✅ Python found: ${pythonCmd}`, colors.green);

  // Check dependencies
  const nodeDepsInstalled = checkNodeDeps();
  const pythonDepsInstalled = await checkPythonDeps();

  if (!nodeDepsInstalled) {
    log('❌ Frontend dependencies not installed. Run: cd frontend && npm install', colors.red);
    process.exit(1);
  }
  log('✅ Frontend dependencies installed', colors.green);

  if (!pythonDepsInstalled) {
    log('❌ Backend dependencies not installed. Run: cd backend && pip install -r requirements.txt', colors.red);
    process.exit(1);
  }
  log('✅ Backend dependencies installed', colors.green);

  log('\nStarting development servers...', colors.cyan);
  log('Backend will be available at: http://localhost:8000', colors.cyan);
  log('Frontend will be available at: http://localhost:5173', colors.cyan);
  log('API Documentation: http://localhost:8000/docs', colors.cyan);
  log('\nPress Ctrl+C to stop both servers\n', colors.yellow);

  // Start both servers
  const backend = startBackend(pythonCmd);
  const frontend = startFrontend();

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    log('\n🛑 Shutting down servers...', colors.yellow);
    backend.kill();
    frontend.kill();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    backend.kill();
    frontend.kill();
    process.exit(0);
  });
}

// Run the script
main().catch((error) => {
  log(`❌ Error: ${error.message}`, colors.red);
  process.exit(1);
});

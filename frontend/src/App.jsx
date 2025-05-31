import { useState } from 'react'
import './App.css'
import FileUpload from './components/FileUpload'
import TranscriptionStatus from './components/TranscriptionStatus'
import SubtitlePreview from './components/SubtitlePreview'
import DownloadSection from './components/DownloadSection'

function App() {
  const [currentStep, setCurrentStep] = useState('upload') // upload, processing, completed
  const [jobId, setJobId] = useState(null)
  const [filename, setFilename] = useState('')
  const [transcriptionData, setTranscriptionData] = useState(null)
  const [error, setError] = useState(null)

  const handleUploadSuccess = (uploadResponse) => {
    setJobId(uploadResponse.job_id)
    setFilename(uploadResponse.filename)
    setCurrentStep('processing')
    setError(null)
  }

  const handleTranscriptionComplete = (data) => {
    setTranscriptionData(data)
    setCurrentStep('completed')
  }

  const handleError = (errorMessage) => {
    setError(errorMessage)
  }

  const resetApp = () => {
    setCurrentStep('upload')
    setJobId(null)
    setFilename('')
    setTranscriptionData(null)
    setError(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎵 ScribeEasy</h1>
        <p>Transform your audio and video files into accurate transcriptions</p>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={resetApp} className="retry-btn">Try Again</button>
          </div>
        )}

        <div className="progress-indicator">
          <div className={`step ${currentStep === 'upload' ? 'active' : currentStep !== 'upload' ? 'completed' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-label">Upload</span>
          </div>
          <div className={`step ${currentStep === 'processing' ? 'active' : currentStep === 'completed' ? 'completed' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-label">Transcribe</span>
          </div>
          <div className={`step ${currentStep === 'completed' ? 'active' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-label">Download</span>
          </div>
        </div>

        {currentStep === 'upload' && (
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onError={handleError}
          />
        )}

        {currentStep === 'processing' && (
          <TranscriptionStatus
            jobId={jobId}
            filename={filename}
            onComplete={handleTranscriptionComplete}
            onError={handleError}
          />
        )}

        {currentStep === 'completed' && transcriptionData && (
          <div className="results-section">
            <SubtitlePreview transcriptionData={transcriptionData} />
            <DownloadSection
              jobId={jobId}
              filename={filename}
              transcriptionData={transcriptionData}
            />
            <button onClick={resetApp} className="new-transcription-btn">
              Start New Transcription
            </button>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by AssemblyAI • Built with React & FastAPI</p>
      </footer>
    </div>
  )
}

export default App

import { useState, useEffect } from 'react'
import { Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import apiService from '../services/api'

const TranscriptionStatus = ({ jobId, filename, onComplete, onError }) => {
  const [status, setStatus] = useState('queued')
  const [progress, setProgress] = useState(0)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [estimatedTime, setEstimatedTime] = useState(null)

  useEffect(() => {
    let pollInterval
    let timeInterval

    const pollStatus = async () => {
      try {
        const result = await apiService.getTranscriptionStatus(jobId)
        setStatus(result.status)

        if (result.status === 'completed') {
          clearInterval(pollInterval)
          clearInterval(timeInterval)
          onComplete(result)
        } else if (result.status === 'error') {
          clearInterval(pollInterval)
          clearInterval(timeInterval)
          onError(result.error || 'Transcription failed')
        } else if (result.status === 'processing') {
          // Simulate progress for better UX
          setProgress(prev => Math.min(prev + Math.random() * 10, 85))
        }
      } catch (error) {
        clearInterval(pollInterval)
        clearInterval(timeInterval)
        onError(error.message || 'Failed to check transcription status')
      }
    }

    // Start polling immediately
    pollStatus()
    
    // Poll every 3 seconds
    pollInterval = setInterval(pollStatus, 3000)

    // Update elapsed time every second
    timeInterval = setInterval(() => {
      setElapsedTime(prev => prev + 1)
    }, 1000)

    return () => {
      clearInterval(pollInterval)
      clearInterval(timeInterval)
    }
  }, [jobId, onComplete, onError])

  // Estimate remaining time based on typical transcription speeds
  useEffect(() => {
    if (status === 'processing' && elapsedTime > 10) {
      // Rough estimate: 1 minute of audio takes 30-60 seconds to transcribe
      const estimatedTotal = Math.max(60, elapsedTime * 1.5)
      setEstimatedTime(Math.max(0, estimatedTotal - elapsedTime))
    }
  }, [status, elapsedTime])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'queued':
        return <Clock size={24} className="status-icon queued" />
      case 'processing':
        return <Loader size={24} className="status-icon processing spinning" />
      case 'completed':
        return <CheckCircle size={24} className="status-icon completed" />
      case 'error':
        return <AlertCircle size={24} className="status-icon error" />
      default:
        return <Clock size={24} className="status-icon" />
    }
  }

  const getStatusMessage = () => {
    switch (status) {
      case 'queued':
        return 'Your file is in the queue and will be processed shortly...'
      case 'processing':
        return 'AI is analyzing your audio and generating the transcription...'
      case 'completed':
        return 'Transcription completed successfully!'
      case 'error':
        return 'An error occurred during transcription.'
      default:
        return 'Processing...'
    }
  }

  const getProgressPercentage = () => {
    switch (status) {
      case 'queued':
        return 10
      case 'processing':
        return Math.min(progress, 90)
      case 'completed':
        return 100
      case 'error':
        return 0
      default:
        return 0
    }
  }

  return (
    <div className="transcription-status">
      <div className="status-header">
        <h2>Processing Your File</h2>
        <p className="filename">{filename}</p>
      </div>

      <div className="status-content">
        <div className="status-indicator">
          {getStatusIcon()}
          <div className="status-text">
            <h3>{status.charAt(0).toUpperCase() + status.slice(1)}</h3>
            <p>{getStatusMessage()}</p>
          </div>
        </div>

        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
          <div className="progress-text">
            {getProgressPercentage()}% Complete
          </div>
        </div>

        <div className="time-info">
          <div className="time-item">
            <span className="time-label">Elapsed:</span>
            <span className="time-value">{formatTime(elapsedTime)}</span>
          </div>
          {estimatedTime && status === 'processing' && (
            <div className="time-item">
              <span className="time-label">Est. remaining:</span>
              <span className="time-value">{formatTime(Math.round(estimatedTime))}</span>
            </div>
          )}
        </div>

        {status === 'processing' && (
          <div className="processing-info">
            <p>
              <strong>What's happening:</strong> Our AI is carefully analyzing your audio, 
              identifying speech patterns, and converting them into accurate text with proper 
              punctuation and formatting.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default TranscriptionStatus

import { useState, useEffect } from 'react'
import { Eye, Clock, MessageSquare } from 'lucide-react'

const SubtitlePreview = ({ transcriptionData }) => {
  const [previewMode, setPreviewMode] = useState('text') // 'text' or 'segments'
  const [visibleSegments, setVisibleSegments] = useState(10)

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    const ms = Math.floor((seconds % 1) * 1000)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`
  }

  const getPreviewText = () => {
    if (!transcriptionData?.text) return ''
    
    // Show first 500 characters with word boundary
    const text = transcriptionData.text
    if (text.length <= 500) return text
    
    const truncated = text.substring(0, 500)
    const lastSpace = truncated.lastIndexOf(' ')
    return lastSpace > 400 ? truncated.substring(0, lastSpace) + '...' : truncated + '...'
  }

  const getPreviewSegments = () => {
    if (!transcriptionData?.segments) return []
    return transcriptionData.segments.slice(0, visibleSegments)
  }

  const showMoreSegments = () => {
    setVisibleSegments(prev => Math.min(prev + 10, transcriptionData?.segments?.length || 0))
  }

  const hasMoreSegments = () => {
    return transcriptionData?.segments && visibleSegments < transcriptionData.segments.length
  }

  if (!transcriptionData) {
    return (
      <div className="subtitle-preview">
        <div className="preview-header">
          <Eye size={20} />
          <h3>Transcription Preview</h3>
        </div>
        <div className="preview-content">
          <p>No transcription data available.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="subtitle-preview">
      <div className="preview-header">
        <div className="header-left">
          <Eye size={20} />
          <h3>Transcription Preview</h3>
        </div>
        
        <div className="preview-controls">
          <button
            className={`mode-btn ${previewMode === 'text' ? 'active' : ''}`}
            onClick={() => setPreviewMode('text')}
          >
            <MessageSquare size={16} />
            Text
          </button>
          <button
            className={`mode-btn ${previewMode === 'segments' ? 'active' : ''}`}
            onClick={() => setPreviewMode('segments')}
            disabled={!transcriptionData.segments || transcriptionData.segments.length === 0}
          >
            <Clock size={16} />
            Segments
          </button>
        </div>
      </div>

      <div className="preview-stats">
        {transcriptionData.audio_duration && (
          <div className="stat">
            <span className="stat-label">Duration:</span>
            <span className="stat-value">{formatTime(transcriptionData.audio_duration)}</span>
          </div>
        )}
        {transcriptionData.confidence && (
          <div className="stat">
            <span className="stat-label">Confidence:</span>
            <span className="stat-value">{Math.round(transcriptionData.confidence * 100)}%</span>
          </div>
        )}
        {transcriptionData.segments && (
          <div className="stat">
            <span className="stat-label">Segments:</span>
            <span className="stat-value">{transcriptionData.segments.length}</span>
          </div>
        )}
      </div>

      <div className="preview-content">
        {previewMode === 'text' ? (
          <div className="text-preview">
            <div className="text-content">
              {getPreviewText() || 'No text available'}
            </div>
            {transcriptionData.text && transcriptionData.text.length > 500 && (
              <div className="preview-note">
                <p>Showing first 500 characters. Download the full transcription to see everything.</p>
              </div>
            )}
          </div>
        ) : (
          <div className="segments-preview">
            {getPreviewSegments().length > 0 ? (
              <>
                <div className="segments-list">
                  {getPreviewSegments().map((segment, index) => (
                    <div key={index} className="segment-item">
                      <div className="segment-time">
                        {formatTime(segment.start)} → {formatTime(segment.end)}
                      </div>
                      <div className="segment-text">
                        {segment.text}
                      </div>
                    </div>
                  ))}
                </div>
                
                {hasMoreSegments() && (
                  <div className="load-more">
                    <button onClick={showMoreSegments} className="load-more-btn">
                      Show More Segments ({transcriptionData.segments.length - visibleSegments} remaining)
                    </button>
                  </div>
                )}
                
                {!hasMoreSegments() && transcriptionData.segments.length > 10 && (
                  <div className="preview-note">
                    <p>All segments shown. Download the full transcription for the complete file.</p>
                  </div>
                )}
              </>
            ) : (
              <div className="no-segments">
                <p>No segments available. The transcription may only contain plain text.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SubtitlePreview

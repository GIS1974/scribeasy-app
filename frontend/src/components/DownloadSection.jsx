import { useState } from 'react'
import { Download, FileText, Film, Type } from 'lucide-react'
import apiService from '../services/api'

const DownloadSection = ({ jobId, filename, transcriptionData }) => {
  const [downloadingFormat, setDownloadingFormat] = useState(null)

  const downloadFormats = [
    {
      format: 'srt',
      name: 'SRT Subtitles',
      description: 'Standard subtitle format for video players',
      icon: <Film size={20} />,
      extension: '.srt',
      disabled: !transcriptionData?.segments || transcriptionData.segments.length === 0
    },
    {
      format: 'vtt',
      name: 'WebVTT Subtitles',
      description: 'Web-compatible subtitle format',
      icon: <Film size={20} />,
      extension: '.vtt',
      disabled: !transcriptionData?.segments || transcriptionData.segments.length === 0
    },
    {
      format: 'txt',
      name: 'Plain Text',
      description: 'Simple text file with the transcription',
      icon: <Type size={20} />,
      extension: '.txt',
      disabled: false
    }
  ]

  const handleDownload = async (format) => {
    setDownloadingFormat(format)
    
    try {
      const downloadData = await apiService.downloadTranscription(jobId, format)
      
      // Create download link
      const url = window.URL.createObjectURL(downloadData.blob)
      const link = document.createElement('a')
      link.href = url
      link.download = downloadData.filename
      document.body.appendChild(link)
      link.click()
      
      // Cleanup
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
      
    } catch (error) {
      console.error('Download failed:', error)
      alert(error.message || 'Download failed. Please try again.')
    } finally {
      setDownloadingFormat(null)
    }
  }

  const getBaseFilename = () => {
    if (!filename) return 'transcription'
    const lastDotIndex = filename.lastIndexOf('.')
    return lastDotIndex > 0 ? filename.substring(0, lastDotIndex) : filename
  }

  return (
    <div className="download-section">
      <div className="download-header">
        <Download size={20} />
        <h3>Download Your Transcription</h3>
      </div>

      <div className="download-info">
        <p>Choose your preferred format to download the transcription:</p>
      </div>

      <div className="download-formats">
        {downloadFormats.map((formatInfo) => (
          <div 
            key={formatInfo.format}
            className={`format-card ${formatInfo.disabled ? 'disabled' : ''}`}
          >
            <div className="format-icon">
              {formatInfo.icon}
            </div>
            
            <div className="format-details">
              <h4>{formatInfo.name}</h4>
              <p>{formatInfo.description}</p>
              <div className="format-filename">
                {getBaseFilename()}_transcription{formatInfo.extension}
              </div>
            </div>

            <button
              onClick={() => handleDownload(formatInfo.format)}
              disabled={formatInfo.disabled || downloadingFormat === formatInfo.format}
              className="download-btn"
              title={formatInfo.disabled ? 'Segments not available for this format' : ''}
            >
              {downloadingFormat === formatInfo.format ? (
                <>
                  <div className="spinner small"></div>
                  Downloading...
                </>
              ) : (
                <>
                  <Download size={16} />
                  Download
                </>
              )}
            </button>
          </div>
        ))}
      </div>

      {transcriptionData?.segments && transcriptionData.segments.length === 0 && (
        <div className="download-note">
          <FileText size={16} />
          <p>
            <strong>Note:</strong> Subtitle formats (SRT/VTT) are not available because 
            the transcription doesn't include timing segments. You can still download 
            the plain text version.
          </p>
        </div>
      )}

      <div className="download-tips">
        <h4>Format Guide:</h4>
        <ul>
          <li><strong>SRT:</strong> Best for video editing software and most media players</li>
          <li><strong>VTT:</strong> Ideal for web videos and HTML5 players</li>
          <li><strong>TXT:</strong> Simple text format for documents and editing</li>
        </ul>
      </div>
    </div>
  )
}

export default DownloadSection

import { useState, useRef } from 'react'
import { Upload, File, X } from 'lucide-react'
import apiService from '../services/api'
import fileValidation from '../utils/fileValidation'

const FileUpload = ({ onUploadSuccess, onError }) => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileSelect = (file) => {
    const validation = fileValidation.validateFile(file)
    
    if (!validation.isValid) {
      onError(validation.error)
      return
    }

    setSelectedFile(file)
    onError(null) // Clear any previous errors
  }

  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      handleFileSelect(files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      onError('Please select a file first')
      return
    }

    setIsUploading(true)
    
    try {
      const response = await apiService.uploadFile(selectedFile)
      onUploadSuccess(response)
    } catch (error) {
      onError(error.message || 'Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const clearSelectedFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const openFileDialog = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="file-upload-container">
      <div className="upload-instructions">
        <h2>Upload Your Audio or Video File</h2>
        <p>
          Supported formats: {fileValidation.getSupportedTypesString()}
        </p>
        <p>
          Maximum file size: {fileValidation.formatFileSize(fileValidation.MAX_FILE_SIZE)}
        </p>
      </div>

      <div
        className={`drop-zone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={fileValidation.getAcceptAttribute()}
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />

        {!selectedFile ? (
          <div className="drop-zone-content">
            <Upload size={48} className="upload-icon" />
            <h3>Drop your file here or click to browse</h3>
            <p>Choose an audio or video file to transcribe</p>
          </div>
        ) : (
          <div className="selected-file">
            <File size={32} className="file-icon" />
            <div className="file-info">
              <h4>{selectedFile.name}</h4>
              <p>{fileValidation.formatFileSize(selectedFile.size)}</p>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                clearSelectedFile()
              }}
              className="remove-file-btn"
              disabled={isUploading}
            >
              <X size={20} />
            </button>
          </div>
        )}
      </div>

      {selectedFile && (
        <div className="upload-actions">
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="upload-btn"
          >
            {isUploading ? (
              <>
                <div className="spinner"></div>
                Uploading...
              </>
            ) : (
              <>
                <Upload size={20} />
                Start Transcription
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

export default FileUpload

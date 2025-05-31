// Supported file types and their MIME types
export const SUPPORTED_FILE_TYPES = {
  '.mp3': ['audio/mpeg', 'audio/mp3'],
  '.mp4': ['video/mp4'],
  '.mkv': ['video/x-matroska', 'video/mkv'],
  '.wav': ['audio/wav', 'audio/wave'],
  '.m4a': ['audio/mp4', 'audio/m4a']
}

// Maximum file size (1000MB)
export const MAX_FILE_SIZE = 1000 * 1024 * 1024

export const fileValidation = {
  /**
   * Validate if file type is supported
   * @param {File} file - The file to validate
   * @returns {boolean} - True if file type is supported
   */
  isValidFileType(file) {
    if (!file || !file.name) return false
    
    const fileName = file.name.toLowerCase()
    const fileExtension = fileName.substring(fileName.lastIndexOf('.'))
    
    // Check if extension is supported
    if (!SUPPORTED_FILE_TYPES[fileExtension]) {
      return false
    }
    
    // Check MIME type if available
    if (file.type) {
      const supportedMimeTypes = SUPPORTED_FILE_TYPES[fileExtension]
      return supportedMimeTypes.includes(file.type.toLowerCase())
    }
    
    return true
  },

  /**
   * Validate file size
   * @param {File} file - The file to validate
   * @returns {boolean} - True if file size is within limits
   */
  isValidFileSize(file) {
    if (!file) return false
    return file.size <= MAX_FILE_SIZE
  },

  /**
   * Get file extension from filename
   * @param {string} filename - The filename
   * @returns {string} - File extension with dot
   */
  getFileExtension(filename) {
    if (!filename) return ''
    return filename.substring(filename.lastIndexOf('.')).toLowerCase()
  },

  /**
   * Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} - Formatted file size
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  /**
   * Get supported file types as a string for display
   * @returns {string} - Comma-separated list of supported extensions
   */
  getSupportedTypesString() {
    return Object.keys(SUPPORTED_FILE_TYPES).join(', ')
  },

  /**
   * Get supported file types for file input accept attribute
   * @returns {string} - Accept attribute value
   */
  getAcceptAttribute() {
    const extensions = Object.keys(SUPPORTED_FILE_TYPES)
    const mimeTypes = Object.values(SUPPORTED_FILE_TYPES).flat()
    return [...extensions, ...mimeTypes].join(',')
  },

  /**
   * Comprehensive file validation
   * @param {File} file - The file to validate
   * @returns {Object} - Validation result with isValid and error message
   */
  validateFile(file) {
    if (!file) {
      return {
        isValid: false,
        error: 'No file selected'
      }
    }

    if (!this.isValidFileType(file)) {
      return {
        isValid: false,
        error: `Unsupported file type. Supported formats: ${this.getSupportedTypesString()}`
      }
    }

    if (!this.isValidFileSize(file)) {
      return {
        isValid: false,
        error: `File too large. Maximum size: ${this.formatFileSize(MAX_FILE_SIZE)}`
      }
    }

    return {
      isValid: true,
      error: null
    }
  }
}

export default fileValidation

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'
import { Progress } from './ui/progress'
import { documentService } from '../services'

interface FileUploadProps {
  onUploadSuccess?: (documents: any[]) => void
  onUploadError?: (error: string) => void
  maxFiles?: number
  maxSize?: number // in bytes
  acceptedFileTypes?: string[]
  className?: string
}

interface UploadingFile {
  file: File
  progress: number
  status: 'uploading' | 'success' | 'error'
  error?: string
  id: string
}

export const FileUpload = ({
  onUploadSuccess,
  onUploadError,
  maxFiles = 10,
  maxSize = 10 * 1024 * 1024, // 10MB default
  acceptedFileTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ],
  className = ''
}: FileUploadProps) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    // Check if adding these files would exceed max files
    if (uploadingFiles.length + acceptedFiles.length > maxFiles) {
      onUploadError?.(`Maximum ${maxFiles} files allowed`)
      return
    }

    // Create uploading file objects
    const newUploadingFiles: UploadingFile[] = acceptedFiles.map(file => ({
      file,
      progress: 0,
      status: 'uploading' as const,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }))

    setUploadingFiles(prev => [...prev, ...newUploadingFiles])

    // Process uploads
    const uploadPromises = newUploadingFiles.map(async (uploadingFile) => {
      try {
        // Simulate progress for better UX
        const progressInterval = setInterval(() => {
          setUploadingFiles(prev => 
            prev.map(f => 
              f.id === uploadingFile.id 
                ? { ...f, progress: Math.min(f.progress + 10, 90) }
                : f
            )
          )
        }, 200)

        const result = await documentService.uploadDocument(uploadingFile.file)
        
        clearInterval(progressInterval)

        if (result) {
          setUploadingFiles(prev => 
            prev.map(f => 
              f.id === uploadingFile.id 
                ? { ...f, progress: 100, status: 'success' as const }
                : f
            )
          )
          return result
        } else {
          throw new Error('Upload failed')
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Upload failed'
        setUploadingFiles(prev => 
          prev.map(f => 
            f.id === uploadingFile.id 
              ? { ...f, status: 'error' as const, error: errorMessage }
              : f
          )
        )
        onUploadError?.(errorMessage)
        return null
      }
    })

    try {
      const results = await Promise.all(uploadPromises)
      const successfulUploads = results.filter(result => result !== null)
      
      if (successfulUploads.length > 0) {
        onUploadSuccess?.(successfulUploads)
      }
    } catch (error) {
      console.error('Upload batch failed:', error)
    }
  }, [uploadingFiles.length, maxFiles, onUploadError, onUploadSuccess])

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    fileRejections
  } = useDropzone({
    onDrop,
    accept: acceptedFileTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize,
    maxFiles: maxFiles - uploadingFiles.length,
    multiple: true
  })

  const removeFile = (fileId: string) => {
    setUploadingFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const clearCompleted = () => {
    setUploadingFiles(prev => prev.filter(f => f.status === 'uploading'))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className={className}>
      {/* Drop Zone */}
      <Card 
        {...getRootProps()} 
        className={`
          cursor-pointer border-2 border-dashed transition-colors duration-200
          ${isDragActive && !isDragReject ? 'border-primary bg-primary/5' : ''}
          ${isDragReject ? 'border-destructive bg-destructive/5' : ''}
          ${!isDragActive ? 'border-muted-foreground/25 hover:border-muted-foreground/50' : ''}
        `}
      >
        <CardContent className="p-8 text-center">
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 rounded-full bg-muted">
              <Upload className="h-8 w-8 text-muted-foreground" />
            </div>
            
            <div className="space-y-2">
              <p className="text-lg font-medium">
                {isDragActive 
                  ? 'Drop files here' 
                  : 'Drag & drop files here, or click to select'
                }
              </p>
              <p className="text-sm text-muted-foreground">
                Support for PDF, DOC, DOCX, TXT files up to {formatFileSize(maxSize)}
              </p>
              <p className="text-xs text-muted-foreground">
                Maximum {maxFiles} files
              </p>
            </div>

            <Button variant="outline" type="button">
              Select Files
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* File Rejections */}
      {fileRejections.length > 0 && (
        <div className="mt-4 space-y-2">
          {fileRejections.map(({ file, errors }) => (
            <div key={file.name} className="flex items-center space-x-2 text-sm text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span>{file.name}: {errors.map(e => e.message).join(', ')}</span>
            </div>
          ))}
        </div>
      )}

      {/* Uploading Files List */}
      {uploadingFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Uploading Files</h3>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={clearCompleted}
              disabled={!uploadingFiles.some(f => f.status !== 'uploading')}
            >
              Clear Completed
            </Button>
          </div>

          <div className="space-y-2">
            {uploadingFiles.map((uploadingFile) => (
              <Card key={uploadingFile.id}>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <File className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium truncate">
                          {uploadingFile.file.name}
                        </p>
                        <div className="flex items-center space-x-2">
                          {uploadingFile.status === 'success' && (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          )}
                          {uploadingFile.status === 'error' && (
                            <AlertCircle className="h-4 w-4 text-destructive" />
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(uploadingFile.id)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="mt-1 flex items-center space-x-2">
                        <p className="text-xs text-muted-foreground">
                          {formatFileSize(uploadingFile.file.size)}
                        </p>
                        {uploadingFile.status === 'uploading' && (
                          <div className="flex-1">
                            <Progress value={uploadingFile.progress} className="h-2" />
                          </div>
                        )}
                      </div>
                      
                      {uploadingFile.error && (
                        <p className="text-xs text-destructive mt-1">
                          {uploadingFile.error}
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

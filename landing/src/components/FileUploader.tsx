import { useState, useCallback, useRef } from 'react'

interface UploadResult {
    code: string
    codeFormatted: string
    originalName: string
    fileType: string
    fileSizeBytes: number
    expiresAt: string | null
}

interface FileUploaderProps {
    onUploadComplete: (result: UploadResult) => void
}

const FILE_TYPES = [
    { ext: 'pdf', label: 'PDF', color: 'pdf' },
    { ext: 'epub', label: 'EPUB', color: 'epub' },
    { ext: 'cbz', label: 'CBZ', color: 'cbz' },
    { ext: 'cbr', label: 'CBR', color: 'cbr' },
]

const ALLOWED_EXTENSIONS = FILE_TYPES.map(f => f.ext)
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

export function FileUploader({ onUploadComplete }: FileUploaderProps) {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [error, setError] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const validateFile = (file: File): string | null => {
        const extension = file.name.split('.').pop()?.toLowerCase()

        if (!extension || !ALLOWED_EXTENSIONS.includes(extension)) {
            return `Tipo de arquivo não suportado. Use: ${ALLOWED_EXTENSIONS.join(', ').toUpperCase()}`
        }

        if (file.size > MAX_FILE_SIZE) {
            return `Arquivo muito grande. Máximo: 50MB`
        }

        return null
    }

    const uploadFile = async (file: File) => {
        setError(null)

        const validationError = validateFile(file)
        if (validationError) {
            setError(validationError)
            return
        }

        setIsUploading(true)
        setProgress(0)

        try {
            const formData = new FormData()
            formData.append('file', file)

            // Simulate progress for better UX
            const progressInterval = setInterval(() => {
                setProgress(prev => Math.min(prev + 10, 90))
            }, 200)

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            })

            clearInterval(progressInterval)
            setProgress(100)

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Upload falhou')
            }

            const result = await response.json()

            setTimeout(() => {
                onUploadComplete(result)
            }, 500)

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao fazer upload')
            setIsUploading(false)
            setProgress(0)
        }
    }

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }, [])

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
    }, [])

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)

        const file = e.dataTransfer.files[0]
        if (file) {
            uploadFile(file)
        }
    }, [])

    const handleClick = () => {
        fileInputRef.current?.click()
    }

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            uploadFile(file)
        }
    }

    return (
        <div>
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.cbz,.cbr,.epub"
                onChange={handleFileChange}
                style={{ display: 'none' }}
            />

            <div
                className={`upload-zone ${isDragging ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={handleClick}
            >
                <span className="upload-icon">
                    {isUploading ? '⏳' : '📤'}
                </span>

                <h2 className="upload-title">
                    {isUploading ? 'Enviando arquivo...' : 'Arraste seu arquivo aqui'}
                </h2>

                <p className="upload-subtitle">
                    {isUploading ? 'Por favor, aguarde o upload completar' : 'ou clique para selecionar do seu dispositivo'}
                </p>

                <div className="upload-formats">
                    {FILE_TYPES.map(type => (
                        <span key={type.ext} className={`format-badge ${type.color}`}>
                            {type.label}
                        </span>
                    ))}
                </div>

                <p className="upload-size-info">
                    Suporta arquivos até 50MB
                </p>
            </div>

            {isUploading && (
                <div className="progress-container">
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                    <p className="progress-text">{progress}% completo</p>
                </div>
            )}

            {error && (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            )}
        </div>
    )
}

import { useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'

interface UploadResult {
    code: string
    codeFormatted: string
    originalName: string
    fileType: string
    fileSizeBytes: number
    expiresAt: string | null
}

interface SuccessViewProps {
    result: UploadResult
    onReset: () => void
}

export function SuccessView({ result, onReset }: SuccessViewProps) {
    const [copied, setCopied] = useState(false)

    const copyCode = async () => {
        try {
            await navigator.clipboard.writeText(result.code)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch (err) {
            console.error('Failed to copy:', err)
        }
    }

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return `${bytes} B`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    }

    const formatExpiry = (expiresAt: string | null): string => {
        if (!expiresAt) return 'Permanente'

        const expiry = new Date(expiresAt)
        const now = new Date()
        const diffMs = expiry.getTime() - now.getTime()
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

        if (diffHours < 1) return 'Menos de 1 hora'
        return `${diffHours} horas`
    }

    // Generate the deep link URL for the mobile app
    const deepLinkUrl = `imagineread://lite/${result.code}`

    return (
        <div className="success-card fade-in">
            <div className="success-icon">✅</div>

            <h2 className="success-title">Upload Concluído!</h2>

            <p className="success-subtitle">
                {result.originalName} ({formatFileSize(result.fileSizeBytes)})
            </p>

            {/* QR Code */}
            <div className="qr-container">
                <QRCodeSVG
                    value={deepLinkUrl}
                    size={200}
                    level="H"
                    includeMargin={false}
                    bgColor="#ffffff"
                    fgColor="#000000"
                />
            </div>

            <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px', marginBottom: '24px' }}>
                Escaneie o QRCode com o app ImagineRead
            </p>

            {/* Code Display */}
            <div className="code-section">
                <p className="code-label">Ou digite o código:</p>
                <div className="code-display">
                    <span className="code-text">{result.codeFormatted}</span>
                    <button
                        className="copy-button"
                        onClick={copyCode}
                        title="Copiar código"
                    >
                        {copied ? '✓' : '📋'}
                    </button>
                </div>
            </div>

            {/* Expiry Info */}
            <div className="expiry-info">
                ⏰ Expira em: {formatExpiry(result.expiresAt)}
            </div>

            {/* Actions */}
            <div style={{ marginTop: '32px', display: 'flex', justifyContent: 'center', gap: '16px' }}>
                <button className="button button-primary" onClick={onReset}>
                    📤 Enviar outro arquivo
                </button>
            </div>
        </div>
    )
}

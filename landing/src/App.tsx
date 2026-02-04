import { useState } from 'react'
import { FileUploader } from './components/FileUploader'
import { SuccessView } from './components/SuccessView'

interface UploadResult {
    code: string
    codeFormatted: string
    originalName: string
    fileType: string
    fileSizeBytes: number
    expiresAt: string | null
}

function App() {
    const [uploadResult, setUploadResult] = useState<UploadResult | null>(null)

    const handleUploadComplete = (result: UploadResult) => {
        setUploadResult(result)
    }

    const handleReset = () => {
        setUploadResult(null)
    }

    return (
        <div className="app">
            {/* Animated Background */}
            <div className="bg-animated" />
            <div className="bg-stars" />

            <div className="container">
                {/* Header */}
                <header className="header">
                    <div className="logo">
                        <div className="logo-icon">📚</div>
                        <span className="logo-text">ImagineRead</span>
                    </div>
                </header>

                {/* Hero Section */}
                <section className="hero">
                    <div className="hero-badge">
                        <span className="hero-badge-dot"></span>
                        Grátis • Sem registro
                    </div>
                    <h1 className="hero-title">
                        Compartilhe Arquivos<br />
                        <span className="hero-title-gradient">Instantaneamente</span>
                    </h1>
                    <p className="hero-subtitle">
                        Envie PDFs, eBooks e quadrinhos para qualquer dispositivo usando QR Code
                    </p>
                </section>

                {/* Main Upload Card */}
                <main className="main-card fade-in-up">
                    {uploadResult ? (
                        <SuccessView
                            result={uploadResult}
                            onReset={handleReset}
                        />
                    ) : (
                        <FileUploader onUploadComplete={handleUploadComplete} />
                    )}
                </main>

                {/* Features */}
                <section className="features">
                    <div className="feature fade-in-up delay-1">
                        <span className="feature-icon">⚡</span>
                        <div className="feature-title">Ultra Rápido</div>
                        <div className="feature-desc">Upload instantâneo sem criar conta</div>
                    </div>
                    <div className="feature fade-in-up delay-2">
                        <span className="feature-icon">📱</span>
                        <div className="feature-title">Super Fácil</div>
                        <div className="feature-desc">Escaneie o QR Code ou digite o código</div>
                    </div>
                    <div className="feature fade-in-up delay-3">
                        <span className="feature-icon">🔐</span>
                        <div className="feature-title">Privado</div>
                        <div className="feature-desc">Arquivos expiram automaticamente em 24h</div>
                    </div>
                </section>

                {/* Footer */}
                <footer className="footer">
                    <p>
                        Feito com 💜 por <a href="https://imagineread.com">ImagineRead</a>
                    </p>
                </footer>
            </div>
        </div>
    )
}

export default App

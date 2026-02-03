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
        <>
            <div className="bg-gradient" />

            <div className="container">
                <header className="header">
                    <div className="logo">
                        <div className="logo-icon">📚</div>
                        <span className="logo-text">ImagineRead Lite</span>
                    </div>
                    <p className="tagline">
                        Compartilhe arquivos PDF, CBZ, CBR e EPUB instantaneamente via QRCode
                    </p>
                </header>

                <main className="main-card fade-in">
                    {uploadResult ? (
                        <SuccessView
                            result={uploadResult}
                            onReset={handleReset}
                        />
                    ) : (
                        <FileUploader onUploadComplete={handleUploadComplete} />
                    )}
                </main>

                <section className="features">
                    <div className="feature">
                        <div className="feature-icon">⚡</div>
                        <div className="feature-title">Rápido</div>
                        <div className="feature-desc">Upload instantâneo, sem criar conta</div>
                    </div>
                    <div className="feature">
                        <div className="feature-icon">📱</div>
                        <div className="feature-title">Fácil</div>
                        <div className="feature-desc">Escaneie o QRCode ou digite o código</div>
                    </div>
                    <div className="feature">
                        <div className="feature-icon">🔒</div>
                        <div className="feature-title">Seguro</div>
                        <div className="feature-desc">Arquivos expiram em 24 horas</div>
                    </div>
                </section>

                <footer className="footer">
                    <p>
                        Feito com ❤️ por <a href="#">ImagineRead</a>
                    </p>
                    <p style={{ marginTop: '8px' }}>
                        Limite: 10MB gratuito • <a href="#">Upgrade para Premium</a>
                    </p>
                </footer>
            </div>
        </>
    )
}

export default App

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
            <header className="header">
                <div className="logo">
                    <span className="logo-icon">📚</span>
                    <span className="logo-text">ImagineRead</span>
                </div>
            </header>

            <main className="main-card">
                {uploadResult ? (
                    <SuccessView
                        result={uploadResult}
                        onReset={handleReset}
                    />
                ) : (
                    <FileUploader onUploadComplete={handleUploadComplete} />
                )}
            </main>

            <footer className="footer">
                <a href="https://imagineread.com">imagineread.com</a>
            </footer>
        </div>
    )
}

export default App

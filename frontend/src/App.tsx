import { useState } from "react";
import OcrUpload from "./components/OcrUpload";
import ObjectDetection from "./components/ObjectDetection";
import InvoiceProcessor from "./components/InvoiceProcessor";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState<"ocr" | "detect" | "invoice">(
    "ocr"
  );

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 Local AI System</h1>
        <p>OCR • Object Detection • Invoice Processing</p>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${activeTab === "ocr" ? "active" : ""}`}
          onClick={() => setActiveTab("ocr")}
        >
          📄 OCR
        </button>
        <button
          className={`tab ${activeTab === "detect" ? "active" : ""}`}
          onClick={() => setActiveTab("detect")}
        >
          🔍 Object Detection
        </button>
        <button
          className={`tab ${activeTab === "invoice" ? "active" : ""}`}
          onClick={() => setActiveTab("invoice")}
        >
          📊 Invoice Processing
        </button>
      </nav>

      <main className="main">
        {activeTab === "ocr" && <OcrUpload />}
        {activeTab === "detect" && <ObjectDetection />}
        {activeTab === "invoice" && <InvoiceProcessor />}
      </main>

      <footer className="footer">
        <p>Powered by PyTorch, Tesseract OCR & NestJS | Local AI System v1.0</p>
      </footer>
    </div>
  );
}

export default App;

import { useState } from "react";
import { apiService, OcrResult } from "../services/api.service";

export default function OcrUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OcrResult | null>(null);
  const [error, setError] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
      setError("");

      if (selectedFile.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = () => setPreview(reader.result as string);
        reader.readAsDataURL(selectedFile);
      } else {
        setPreview("");
      }
    }
  };

  const handleProcess = async () => {
    if (!file) return;

    setLoading(true);
    setError("");

    try {
      const response = await apiService.processOcr(file);
      setResult(response);
    } catch (err: any) {
      setError(
        err.response?.data?.error || err.message || "Error processing file"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feature-container">
      <h2>📄 OCR - Text Extraction</h2>
      <p className="subtitle">Extract text from images and PDF documents</p>

      <div className="upload-section">
        <input
          type="file"
          accept="image/*,.pdf"
          onChange={handleFileChange}
          className="file-input"
          id="ocr-file"
        />
        <label htmlFor="ocr-file" className="file-label">
          {file ? file.name : "Choose image or PDF..."}
        </label>

        {file && (
          <button
            onClick={handleProcess}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? "Processing..." : "Extract Text"}
          </button>
        )}
      </div>

      {preview && (
        <div className="preview">
          <img src={preview} alt="Preview" />
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result">
          <div className="result-header">
            <h3>
              ✅ Extracted Text ({result.totalPages} page
              {result.totalPages > 1 ? "s" : ""})
            </h3>
          </div>

          {result.pages.map((page) => (
            <div key={page.page} className="page-result">
              <h4>Page {page.page}</h4>
              <pre className="text-output">
                {page.text || "(No text found)"}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

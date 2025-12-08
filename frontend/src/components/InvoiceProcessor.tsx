import { useState } from "react";
import { apiService, InvoiceResult } from "../services/api.service";

export default function InvoiceProcessor() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InvoiceResult | null>(null);
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
      const response = await apiService.processInvoice(file);
      setResult(response);
    } catch (err: any) {
      setError(
        err.response?.data?.error || err.message || "Error processing invoice"
      );
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.75) return "hsl(120, 60%, 50%)";
    if (confidence >= 0.5) return "hsl(45, 70%, 50%)";
    return "hsl(0, 60%, 50%)";
  };

  return (
    <div className="feature-container">
      <h2>📊 Invoice Processing</h2>
      <p className="subtitle">
        Extract invoice data automatically from images and PDFs
      </p>

      <div className="upload-section">
        <input
          type="file"
          accept="image/*,.pdf"
          onChange={handleFileChange}
          className="file-input"
          id="invoice-file"
        />
        <label htmlFor="invoice-file" className="file-label">
          {file ? file.name : "Choose invoice (image or PDF)..."}
        </label>

        {file && (
          <button
            onClick={handleProcess}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? "Processing..." : "Extract Invoice Data"}
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
            <h3>✅ Invoice Data Extracted</h3>
            <div
              className="confidence-badge"
              style={{ backgroundColor: getConfidenceColor(result.confidence) }}
            >
              Confidence: {(result.confidence * 100).toFixed(0)}%
            </div>
          </div>

          <div className="invoice-data">
            <div className="invoice-field">
              <label>Invoice Number:</label>
              <span>{result.invoiceData.invoiceNumber || "Not found"}</span>
            </div>
            <div className="invoice-field">
              <label>Client:</label>
              <span>{result.invoiceData.client || "Not found"}</span>
            </div>
            <div className="invoice-field">
              <label>Date:</label>
              <span>{result.invoiceData.date || "Not found"}</span>
            </div>
            <div className="invoice-field">
              <label>Amount:</label>
              <span className="amount">
                {result.invoiceData.amount
                  ? `$${result.invoiceData.amount}`
                  : "Not found"}
              </span>
            </div>
          </div>

          {result.rawText && (
            <details className="raw-text-details">
              <summary>View raw extracted text</summary>
              <pre className="text-output">{result.rawText}</pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

import { useState, useRef, useEffect } from "react";
import { apiService, DetectionResult } from "../services/api.service";

export default function ObjectDetection() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string>("");
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type.startsWith("image/")) {
      setFile(selectedFile);
      setResult(null);
      setError("");

      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleDetect = async () => {
    if (!file) return;

    setLoading(true);
    setError("");

    try {
      const response = await apiService.detectObjects(file);
      setResult(response);
    } catch (err: any) {
      setError(
        err.response?.data?.error || err.message || "Error detecting objects"
      );
    } finally {
      setLoading(false);
    }
  };

  // Draw bounding boxes on canvas
  useEffect(() => {
    if (result && preview && canvasRef.current) {
      const img = new Image();
      img.onload = () => {
        const canvas = canvasRef.current!;
        const ctx = canvas.getContext("2d")!;

        canvas.width = img.width;
        canvas.height = img.height;

        ctx.drawImage(img, 0, 0);

        // Draw bounding boxes
        result.detections.forEach((detection, index) => {
          const [x1, y1, x2, y2] = detection.bbox;
          const width = x2 - x1;
          const height = y2 - y1;

          // Generate color based on label
          const hue = (index * 137.5) % 360;
          ctx.strokeStyle = `hsl(${hue}, 70%, 50%)`;
          ctx.fillStyle = `hsla(${hue}, 70%, 50%, 0.2)`;
          ctx.lineWidth = 3;

          // Draw box
          ctx.fillRect(x1, y1, width, height);
          ctx.strokeRect(x1, y1, width, height);

          // Draw label
          ctx.fillStyle = `hsl(${hue}, 70%, 40%)`;
          ctx.font = "bold 16px Arial";
          const label = `${detection.label} (${(detection.score * 100).toFixed(
            0
          )}%)`;
          const textWidth = ctx.measureText(label).width;
          ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);
          ctx.fillStyle = "white";
          ctx.fillText(label, x1 + 5, y1 - 7);
        });
      };
      img.src = preview;
    }
  }, [result, preview]);

  return (
    <div className="feature-container">
      <h2>🔍 Object Detection</h2>
      <p className="subtitle">
        Detect objects in images using PyTorch Faster R-CNN
      </p>

      <div className="upload-section">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="file-input"
          id="detect-file"
        />
        <label htmlFor="detect-file" className="file-label">
          {file ? file.name : "Choose image..."}
        </label>

        {file && (
          <button
            onClick={handleDetect}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? "Detecting..." : "Detect Objects"}
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result">
          <div className="result-header">
            <h3>
              ✅ Detected {result.totalDetections} object
              {result.totalDetections !== 1 ? "s" : ""}
            </h3>
          </div>

          <div className="detection-canvas">
            <canvas
              ref={canvasRef}
              style={{ maxWidth: "100%", height: "auto" }}
            />
          </div>

          <div className="detections-list">
            <h4>Detections:</h4>
            {result.detections.map((detection, index) => (
              <div key={index} className="detection-item">
                <span className="detection-label">{detection.label}</span>
                <span className="detection-score">
                  {(detection.score * 100).toFixed(1)}%
                </span>
                <span className="detection-bbox">
                  [{detection.bbox.map((n) => n.toFixed(0)).join(", ")}]
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

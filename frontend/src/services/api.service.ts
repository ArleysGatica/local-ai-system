import axios from "axios";

const API_BASE_URL = "http://localhost:3000/ai";

export interface OcrResult {
  success: boolean;
  pages: Array<{ page: number; text: string }>;
  fullText: string;
  totalPages: number;
}

export interface Detection {
  label: string;
  score: number;
  bbox: number[];
}

export interface DetectionResult {
  success: boolean;
  detections: Detection[];
  totalDetections: number;
  imageSize: { width: number; height: number };
}

export interface InvoiceData {
  invoiceNumber: string | null;
  client: string | null;
  date: string | null;
  amount: string | null;
}

export interface InvoiceResult {
  success: boolean;
  invoiceData: InvoiceData;
  confidence: number;
  rawText?: string;
  pages: number;
}

class ApiService {
  async processOcr(file: File): Promise<OcrResult> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post<OcrResult>(
      `${API_BASE_URL}/ocr`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  }

  async detectObjects(file: File): Promise<DetectionResult> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post<DetectionResult>(
      `${API_BASE_URL}/detect`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  }

  async processInvoice(file: File): Promise<InvoiceResult> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post<InvoiceResult>(
      `${API_BASE_URL}/invoice`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  }
}

export const apiService = new ApiService();

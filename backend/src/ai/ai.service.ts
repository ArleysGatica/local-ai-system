import { Injectable } from "@nestjs/common";
import { HttpService } from "@nestjs/axios";
import { firstValueFrom } from "rxjs";
import FormData from "form-data";

@Injectable()
export class AiService {
  private readonly AI_SERVICE_URL: string;

  constructor(private readonly httpService: HttpService) {
    // Default to localhost:5001 for local dev, override with AI_SERVICE_URL env var for Docker
    this.AI_SERVICE_URL = process.env.AI_SERVICE_URL || "http://localhost:5001";
  }

  /**
   * Process OCR on an uploaded file
   */
  async processOcr(file: Express.Multer.File) {
    try {
      const formData = new FormData();
      formData.append("file", file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });

      const response = await firstValueFrom(
        this.httpService.post(`${this.AI_SERVICE_URL}/ocr`, formData, {
          headers: formData.getHeaders(),
        })
      );

      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || error.message || "Unknown error";
      console.error("OCR Error:", errorMessage);
      throw new Error(`OCR processing failed: ${errorMessage}`);
    }
  }

  /**
   * Detect objects in an uploaded image
   */
  async detectObjects(file: Express.Multer.File) {
    try {
      const formData = new FormData();
      formData.append("file", file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });

      const response = await firstValueFrom(
        this.httpService.post(`${this.AI_SERVICE_URL}/detect`, formData, {
          headers: formData.getHeaders(),
        })
      );

      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || error.message || "Unknown error";
      console.error("Detection Error:", errorMessage);
      throw new Error(`Object detection failed: ${errorMessage}`);
    }
  }

  /**
   * Process invoice data extraction
   */
  async processInvoice(file: Express.Multer.File) {
    try {
      const formData = new FormData();
      formData.append("file", file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });

      const response = await firstValueFrom(
        this.httpService.post(`${this.AI_SERVICE_URL}/invoice`, formData, {
          headers: formData.getHeaders(),
        })
      );

      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || error.message || "Unknown error";
      console.error("Invoice Error:", errorMessage);
      throw new Error(`Invoice processing failed: ${errorMessage}`);
    }
  }
}

import {
  Controller,
  Post,
  UseInterceptors,
  UploadedFile,
  HttpException,
  HttpStatus,
  Get,
} from "@nestjs/common";
import { FileInterceptor } from "@nestjs/platform-express";
import {
  ApiTags,
  ApiOperation,
  ApiConsumes,
  ApiBody,
  ApiResponse,
} from "@nestjs/swagger";
import { AiService } from "./ai.service";

@ApiTags("ai")
@Controller("ai")
export class AiController {
  constructor(private readonly aiService: AiService) {}

  @Get("/health")
  @ApiOperation({ summary: "Health check endpoint" })
  @ApiResponse({ status: 200, description: "Service is healthy" })
  healthCheck() {
    return {
      status: "healthy",
      service: "NestJS Backend",
      version: "1.0.0",
    };
  }

  @Post("ocr")
  @ApiOperation({ summary: "Extract text from images or PDFs using OCR" })
  @ApiConsumes("multipart/form-data")
  @ApiBody({
    schema: {
      type: "object",
      properties: {
        file: {
          type: "string",
          format: "binary",
          description: "Image or PDF file to process",
        },
      },
    },
  })
  @ApiResponse({
    status: 200,
    description: "Text extracted successfully",
    schema: {
      example: {
        success: true,
        pages: [
          { page: 1, text: "Extracted text from page 1..." },
          { page: 2, text: "Extracted text from page 2..." },
        ],
        fullText: "Complete extracted text...",
        totalPages: 2,
      },
    },
  })
  @ApiResponse({ status: 400, description: "Bad request - no file provided" })
  @ApiResponse({ status: 500, description: "Internal server error" })
  @UseInterceptors(FileInterceptor("file"))
  async processOcr(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new HttpException("No file provided", HttpStatus.BAD_REQUEST);
    }

    try {
      return await this.aiService.processOcr(file);
    } catch (error) {
      throw new HttpException(
        error.message || "OCR processing failed",
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  @Post("detect")
  @ApiOperation({ summary: "Detect objects in images" })
  @ApiConsumes("multipart/form-data")
  @ApiBody({
    schema: {
      type: "object",
      properties: {
        file: {
          type: "string",
          format: "binary",
          description: "Image file to analyze",
        },
      },
    },
  })
  @ApiResponse({
    status: 200,
    description: "Objects detected successfully",
    schema: {
      example: {
        success: true,
        detections: [
          {
            label: "person",
            score: 0.98,
            bbox: [100, 50, 300, 400],
          },
          {
            label: "car",
            score: 0.95,
            bbox: [500, 200, 800, 600],
          },
        ],
        totalDetections: 2,
        imageSize: { width: 1920, height: 1080 },
      },
    },
  })
  @ApiResponse({ status: 400, description: "Bad request - no file provided" })
  @ApiResponse({ status: 500, description: "Internal server error" })
  @UseInterceptors(FileInterceptor("file"))
  async detectObjects(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new HttpException("No file provided", HttpStatus.BAD_REQUEST);
    }

    try {
      return await this.aiService.detectObjects(file);
    } catch (error) {
      throw new HttpException(
        error.message || "Object detection failed",
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  @Post("invoice")
  @ApiOperation({ summary: "Extract invoice data from images or PDFs" })
  @ApiConsumes("multipart/form-data")
  @ApiBody({
    schema: {
      type: "object",
      properties: {
        file: {
          type: "string",
          format: "binary",
          description: "Invoice image or PDF file",
        },
      },
    },
  })
  @ApiResponse({
    status: 200,
    description: "Invoice data extracted successfully",
    schema: {
      example: {
        success: true,
        invoiceData: {
          invoiceNumber: "FAC-001-2024",
          client: "Empresa XYZ S.A.",
          date: "2024-12-05",
          amount: "1500.00",
        },
        confidence: 0.85,
        pages: 1,
      },
    },
  })
  @ApiResponse({ status: 400, description: "Bad request - no file provided" })
  @ApiResponse({ status: 500, description: "Internal server error" })
  @UseInterceptors(FileInterceptor("file"))
  async processInvoice(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new HttpException("No file provided", HttpStatus.BAD_REQUEST);
    }

    try {
      return await this.aiService.processInvoice(file);
    } catch (error) {
      throw new HttpException(
        error.message || "Invoice processing failed",
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }
}

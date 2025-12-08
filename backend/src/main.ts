import { NestFactory } from "@nestjs/core";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable CORS
  app.enableCors({
    origin: "*",
    methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
    credentials: true,
  });

  // Configure Swagger
  const config = new DocumentBuilder()
    .setTitle("AI Service API")
    .setDescription(
      "Local AI Service API for OCR, Object Detection, and Invoice Processing"
    )
    .setVersion("1.0")
    .addTag("ai", "AI processing endpoints")
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup("api", app, document);

  await app.listen(3000);
  console.log("🚀 NestJS Backend running on http://localhost:3000");
  console.log(
    "📚 Swagger documentation available at http://localhost:3000/api"
  );
}

bootstrap();

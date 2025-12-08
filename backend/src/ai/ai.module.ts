import { Module } from "@nestjs/common";
import { HttpModule } from "@nestjs/axios";
import { AiController } from "./ai.controller";
import { AiService } from "./ai.service";

@Module({
  imports: [
    HttpModule.register({
      timeout: 60000, // 60 seconds timeout for AI processing
      maxRedirects: 5,
    }),
  ],
  controllers: [AiController],
  providers: [AiService],
})
export class AiModule {}

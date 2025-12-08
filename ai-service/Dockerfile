FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
	tesseract-ocr \
	tesseract-ocr-spa \
	tesseract-ocr-eng \
	poppler-utils \
	libgl1 \
	libglib2.0-0 \
	libgomp1 \
	libsm6 \
	libxext6 \
	libxrender1 \
	libfontconfig1 \
	wget \
	build-essential \
	python3-dev \
	&& rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download LayoutLM model during build (for faster startup)
RUN python -c "from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification; \
	LayoutLMv3Processor.from_pretrained('microsoft/layoutlmv3-base'); \
	print('LayoutLM model downloaded')" || echo "LayoutLM download will happen at runtime"

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p models

# Expose port
EXPOSE 5000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
	CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the application
CMD ["python", "app.py"]

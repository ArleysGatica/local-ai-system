# Local AI System

Sistema completo de IA local que reemplaza funcionalidades de Google Cloud Vision y Document AI, usando Docker, Python/Flask, NestJS y React.

## 🚀 Características

- **OCR** - Extracción de texto de imágenes y PDFs multipágina usando Tesseract
- **Detección de Objetos** - Detección de objetos en imágenes usando PyTorch Faster R-CNN
- **Procesamiento de Facturas** - Extracción automática de datos de facturas (número, cliente, fecha, monto)
- **API REST** - Backend NestJS con documentación Swagger
- **Frontend Moderno** - Interfaz React con diseño premium

## 📋 Requisitos

- Docker y Docker Compose instalados
- Al menos 4GB de RAM disponible para los contenedores
- Puertos 3000 y 5000 disponibles

## 🛠️ Instalación y Ejecución

### 1. Levantar servicios con Docker Compose

```bash
# Clonar o navegar al directorio del proyecto
cd local-ai-system

# Construir y levantar servicios
docker-compose up --build

# O en modo detached (background)
docker-compose up -d --build
```

### 2. Acceder a los servicios

Una vez que los contenedores estén en ejecución:

- **Swagger API Documentation**: http://localhost:3000/api
- **NestJS Backend**: http://localhost:3000
- **AI Service**: http://localhost:5000

### 3. Frontend (desarrollo local)

Para ejecutar el frontend localmente:

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en: http://localhost:3001

## 📚 Uso de la API

### Endpoint OCR

```bash
curl -X POST http://localhost:3000/ai/ocr \
  -F "file=@/path/to/image.png"
```

### Endpoint de Detección de Objetos

```bash
curl -X POST http://localhost:3000/ai/detect \
  -F "file=@/path/to/image.jpg"
```

### Endpoint de Procesamiento de Facturas

```bash
curl -X POST http://localhost:3000/ai/invoice \
  -F "file=@/path/to/invoice.pdf"
```

## 🏗️ Arquitectura

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│  Port: 3001 │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   Backend   │ (NestJS + Swagger)
│  Port: 3000 │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│ AI Service  │ (Flask + PyTorch + Tesseract)
│  Port: 5000 │
└─────────────┘
```

## 📦 Estructura del Proyecto

```
local-ai-system/
├── ai-service/          # Servicio de IA (Python/Flask)
│   ├── services/        # Servicios de OCR, detección, facturas
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── backend/             # Backend (NestJS)
│   ├── src/ai/         # Módulo AI
│   ├── Dockerfile
│   └── package.json
├── frontend/            # Frontend (React)
│   ├── src/
│   │   ├── components/ # Componentes React
│   │   └── services/   # Cliente API
│   └── package.json
└── docker-compose.yml
```

## 🔧 Desarrollo

### Detener servicios

```bash
docker-compose down
```

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f ai-service
docker-compose logs -f backend
```

### Reconstruir servicios

```bash
docker-compose up --build
```

## 🌟 Capacidades

### OCR
- Soporte para imágenes (PNG, JPG, JPEG)
- Soporte para PDFs multipágina
- Reconocimiento en español e inglés
- Extracción de texto estructurada por página

### Detección de Objetos
- Modelo Faster R-CNN pre-entrenado con COCO dataset
- 80+ clases de objetos detectables
- Bounding boxes con coordenadas precisas
- Scores de confianza por detección

### Procesamiento de Facturas
- Extracción automática de campos clave
- Detección de número de factura
- Identificación de cliente/razón social
- Extracción de fecha
- Detección de monto total
- Score de confianza de la extracción

## 📝 Notas

- El primer inicio puede tardar varios minutos mientras se descargan los modelos de PyTorch
- Los modelos se cachean en un volumen Docker para posteriores ejecuciones
- El AI Service requiere más recursos (CPU/RAM) para el procesamiento
- Para producción, considerar agregar autenticación y rate limiting

## 🤝 Tecnologías

- **Backend**: NestJS, TypeScript, Swagger
- **AI Service**: Python, Flask, PyTorch, Tesseract OCR
- **Frontend**: React, TypeScript, Vite, Axios
- **Infraestructura**: Docker, Docker Compose

¡Disfruta tu sistema de IA local! 🎉

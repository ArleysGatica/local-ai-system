from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

from services.ocr_service import OcrService
from services.detection_service import DetectionService
from services.invoice_service import InvoiceService

app = Flask(__name__)
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize services
print("Initializing AI services...")
ocr_service = OcrService()
detection_service = DetectionService(confidence_threshold=0.5)
invoice_service = InvoiceService()
print("AI services initialized successfully!")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Service',
        'version': '1.0.0'
    }), 200


@app.route('/ocr', methods=['POST'])
def ocr():
    """
    OCR endpoint - Extract text from images or PDFs.
    
    Expected input: multipart/form-data with 'file' field
    Returns: JSON with extracted text by page
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
        
        # Read file content
        filename = secure_filename(file.filename)
        file_bytes = file.read()
        
        # Process with OCR service
        result = ocr_service.process_file(file_bytes, filename)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/detect', methods=['POST'])
def detect():
    """
    Object detection endpoint - Detect objects in images.
    
    Expected input: multipart/form-data with 'file' field (image)
    Returns: JSON with detected objects (label, score, bbox)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
        
        # Read file content
        file_bytes = file.read()
        
        # Process with detection service
        result = detection_service.detect_objects(file_bytes)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/invoice', methods=['POST'])
def invoice():
    """
    Invoice processing endpoint - Extract invoice data from images or PDFs.
    
    Expected input: multipart/form-data with 'file' field
    Returns: JSON with extracted invoice data
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
        
        # Read file content
        filename = secure_filename(file.filename)
        file_bytes = file.read()
        
        print(f"📁 Processing file: {filename} ({len(file_bytes)} bytes)")
        
        # Process with invoice service
        result = invoice_service.process_invoice(file_bytes, filename)
        
        # Debug: Print extracted data
        print(f"✅ Extracted data: {json.dumps(result['data'], indent=2, ensure_ascii=False)[:500]}...")
        print(f"📊 Confidence: {result['confidence']}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Invoice processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    import socket
    
    def is_port_available(port):
        """Check if a port is available."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return True
            except OSError:
                return False
    
    # Try port 5000 first, fallback to 5005
    port = 5000
    if not is_port_available(port):
        print(f"⚠️  Port {port} is in use, trying port 5005...")
        port = 5005
        if not is_port_available(port):
            print(f"❌ Port {port} is also in use!")
            exit(1)
    
    print(f"🚀 Starting AI Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

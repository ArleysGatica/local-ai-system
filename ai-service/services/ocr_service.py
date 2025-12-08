import io
import os
from PIL import Image
import fitz  # PyMuPDF

# Try PaddleOCR first, fallback to Tesseract
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    import pytesseract


class OcrService:
    """Advanced OCR service using PaddleOCR with Tesseract fallback."""
    
    def __init__(self):
        if PADDLE_AVAILABLE:
            print("Loading PaddleOCR model...")
            # Use lightweight model for faster inference
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='es',  # Spanish + English
                use_gpu=False,
                show_log=False
            )
            self.engine = 'paddleocr'
            print("PaddleOCR loaded successfully!")
        else:
            print("PaddleOCR not available, using Tesseract")
            self.engine = 'tesseract'
            self.lang = 'spa+eng'
    
    def process_file(self, file_bytes, filename):
        """
        Process a file (image or PDF) and extract text.
        
        Args:
            file_bytes: File content as bytes
            filename: Name of the file to determine type
            
        Returns:
            dict: Structured response with pages and full text
        """
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == '.pdf':
                return self._process_pdf(file_bytes)
            else:
                return self._process_image(file_bytes)
                
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    def _process_image(self, image_bytes):
        """Extract text from a single image."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if self.engine == 'paddleocr':
                text, boxes = self._paddle_ocr(image)
            else:
                text = self._tesseract_ocr(image)
                boxes = []
            
            return {
                'success': True,
                'pages': [
                    {'page': 1, 'text': text.strip(), 'boxes': boxes}
                ],
                'fullText': text.strip(),
                'totalPages': 1,
                'engine': self.engine
            }
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    def _process_pdf(self, pdf_bytes):
        """Extract text from all pages of a PDF using PyMuPDF + OCR."""
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            pages = []
            full_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # First try to extract text directly (for native PDFs)
                text = page.get_text()
                
                # If no text found, use OCR on rendered image
                if not text.strip():
                    # Render page to image
                    mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
                    pix = page.get_pixmap(matrix=mat)
                    img_bytes = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_bytes))
                    
                    if self.engine == 'paddleocr':
                        text, boxes = self._paddle_ocr(image)
                    else:
                        text = self._tesseract_ocr(image)
                        boxes = []
                else:
                    boxes = []
                
                pages.append({
                    'page': page_num + 1,
                    'text': text.strip(),
                    'boxes': boxes[:20] if boxes else []  # Limit boxes
                })
                full_text.append(text.strip())
            
            doc.close()
            
            return {
                'success': True,
                'pages': pages,
                'fullText': '\n\n'.join(full_text),
                'totalPages': len(pages),
                'engine': self.engine
            }
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _paddle_ocr(self, image):
        """Run PaddleOCR on an image."""
        # Convert PIL image to numpy array
        import numpy as np
        img_array = np.array(image)
        
        result = self.ocr.ocr(img_array, cls=True)
        
        if not result or not result[0]:
            return '', []
        
        lines = []
        boxes = []
        
        for line in result[0]:
            if line and len(line) >= 2:
                box = line[0]
                text_info = line[1]
                text = text_info[0]
                confidence = text_info[1]
                
                lines.append(text)
                boxes.append({
                    'text': text,
                    'confidence': round(confidence, 3),
                    'box': box
                })
        
        return '\n'.join(lines), boxes
    
    def _tesseract_ocr(self, image):
        """Run Tesseract OCR on an image (fallback)."""
        import pytesseract
        return pytesseract.image_to_string(image, lang=self.lang)

import re
import json
from datetime import datetime
from services.ocr_service import OcrService

# Try to import LayoutLM
try:
    from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
    import torch
    LAYOUTLM_AVAILABLE = True
except ImportError:
    LAYOUTLM_AVAILABLE = False

# Try to import Ollama client
try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class InvoiceService:
    """Advanced service for extracting structured data from documents using AI models."""
    
    def __init__(self):
        self.ocr_service = OcrService()
        self.ollama_url = "http://ollama:11434"  # Docker service name
        
        # Initialize LayoutLM if available
        if LAYOUTLM_AVAILABLE:
            try:
                print("Loading LayoutLM model...")
                self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
                print("LayoutLM processor loaded!")
                self.layoutlm_ready = True
            except Exception as e:
                print(f"LayoutLM not available: {e}")
                self.layoutlm_ready = False
        else:
            self.layoutlm_ready = False
    
    def process_invoice(self, file_bytes, filename):
        """
        Extract structured data from a document using advanced AI.
        
        Pipeline:
        1. PaddleOCR extracts text with bounding boxes
        2. Regex patterns extract structured fields
        3. Ollama (if available) enhances extraction with semantic analysis
        """
        try:
            # Step 1: Extract text with OCR
            ocr_result = self.ocr_service.process_file(file_bytes, filename)
            
            if not ocr_result.get('success'):
                raise Exception("OCR processing failed")
            
            full_text = ocr_result.get('fullText', '')
            boxes = []
            for page in ocr_result.get('pages', []):
                boxes.extend(page.get('boxes', []))
            
            # Step 2: Extract structured data with regex
            receipt_data = self._extract_bank_receipt(full_text)
            
            # Step 3: Try Ollama for semantic enhancement (optional)
            if self._check_ollama_available():
                enhanced_data = self._enhance_with_llm(full_text, receipt_data)
                if enhanced_data:
                    receipt_data = enhanced_data
            
            # Calculate confidence
            total_fields = self._count_fields(receipt_data)
            confidence = min(total_fields / 15, 1.0)
            
            return {
                'success': True,
                'data': receipt_data,
                'confidence': round(confidence, 2),
                'rawText': full_text[:1500] + '...' if len(full_text) > 1500 else full_text,
                'pages': ocr_result.get('totalPages', 1),
                'ocrEngine': ocr_result.get('engine', 'unknown'),
                'llmEnhanced': self._check_ollama_available()
            }
            
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    def _check_ollama_available(self):
        """Check if Ollama service is available."""
        if not OLLAMA_AVAILABLE:
            return False
        try:
            # Try localhost first, then docker service name
            for url in ["http://localhost:11434", "http://ollama:11434"]:
                try:
                    response = requests.get(f"{url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        self.ollama_url = url
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def _enhance_with_llm(self, text, initial_data):
        """Use Ollama/Llama to enhance data extraction."""
        try:
            prompt = f"""Analiza el siguiente texto de un recibo bancario y extrae la información en formato JSON.
            
Texto del recibo:
{text[:3000]}

Extrae estos campos en JSON:
- banco (nombre del banco)
- sucursal
- tipo_operacion (DEPOSITO EN EFECTIVO, TRANSFERENCIA, etc)
- fecha (formato YYYY-MM-DD)
- hora (formato HH:MM:SS)
- numero_cuenta
- iban
- titular
- moneda (USD, NIO, EUR)
- monto_efectivo (número decimal)
- monto_total (número decimal)
- referencia_cliente
- depositante (nombre de quien deposita)

Responde SOLO con el JSON, sin explicaciones."""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_text = result.get('response', '')
                
                # Try to parse JSON from response
                json_match = re.search(r'\{[\s\S]*\}', llm_text)
                if json_match:
                    llm_data = json.loads(json_match.group())
                    return self._merge_with_llm_data(initial_data, llm_data)
            
            return None
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return None
    
    def _merge_with_llm_data(self, initial_data, llm_data):
        """Merge LLM extracted data with regex data."""
        result = initial_data.copy()
        
        # Map LLM fields to our structure
        field_mapping = {
            'banco': ('transaccion', 'banco'),
            'sucursal': ('transaccion', 'sucursal'),
            'tipo_operacion': ('transaccion', 'tipo_operacion'),
            'fecha': ('transaccion', 'fecha'),
            'hora': ('transaccion', 'hora'),
            'numero_cuenta': ('cuenta', 'numero_cuenta'),
            'iban': ('cuenta', 'iban'),
            'titular': ('cuenta', 'titular'),
            'moneda': ('deposito', 'moneda'),
            'monto_efectivo': ('deposito', 'monto_efectivo'),
            'monto_total': ('deposito', 'monto_total'),
            'referencia_cliente': ('referencias', 'referencia_cliente'),
            'depositante': ('referencias', 'depositante'),
        }
        
        for llm_key, (section, field) in field_mapping.items():
            if llm_key in llm_data and llm_data[llm_key]:
                # Only update if current value is empty
                if not result.get(section, {}).get(field):
                    if section not in result:
                        result[section] = {}
                    result[section][field] = llm_data[llm_key]
        
        return result
    
    def _extract_bank_receipt(self, text):
        """Extract bank receipt fields using regex patterns."""
        result = {
            "transaccion": {
                "banco": self._extract_banco(text),
                "sucursal": self._extract_pattern(text, r'(?:sucursal|suc)[:\s]*([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?:\n|$|,)', ''),
                "tipo_operacion": self._extract_tipo_operacion(text),
                "numero_secuencia": self._extract_pattern(text, r'(?:sec|secuencia|seq)[:\s#]*(\d+)', ''),
                "cajero_id": self._extract_pattern(text, r'(?:cajero|caj)[:\s]*([A-Z0-9]+)', ''),
                "fecha": self._extract_fecha(text),
                "hora": self._extract_hora(text)
            },
            "cuenta": {
                "numero_cuenta": self._extract_pattern(text, r'(?:cuenta|cta)[:\s#]*(\d{6,20})', ''),
                "iban": self._extract_pattern(text, r'([A-Z]{2}[A-Z0-9]{15,30})', ''),
                "titular": self._extract_pattern(text, r'(?:titular|beneficiario)[:\s]*([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?:\n|$)', '')
            },
            "deposito": {
                "moneda": self._extract_moneda(text),
                "monto_efectivo": self._extract_monto(text, r'(?:efectivo)[:\s]*[\$C]?\s*([\d,]+\.?\d*)'),
                "monto_total": self._extract_monto_total(text),
                "tipo_cambio": self._extract_monto(text, r'(?:tipo.?cambio|tc)[:\s]*([\d.]+)') or 1.00
            },
            "referencias": {
                "referencia_cliente": self._extract_pattern(text, r'(?:referencia|ref)[:\s#]*(\d+)', ''),
                "depositante": self._extract_depositante(text),
                "datos_sector": self._extract_pattern(text, r'(?:sector|area)[:\s]*([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?:\n|$)', '')
            },
            "informacion_adicional": {
                "identificaciones": self._extract_identificaciones(text),
                "notas": self._extract_notas(text),
                "firmas_requeridas": self._check_firmas_requeridas(text)
            }
        }
        return result
    
    def _extract_pattern(self, text, pattern, default=''):
        """Extract a value using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return default
    
    def _extract_banco(self, text):
        """Extract bank name from text."""
        bancos = ['BAC', 'BANPRO', 'LAFISE', 'BDF', 'FICOHSA', 'AVANZ', 'ATLANTIDA', 
                  'BANCENTRO', 'PROMERICA', 'CITI', 'SCOTIABANK', 'BANCO NACIONAL',
                  'DAVIVIENDA', 'BANRURAL', 'INDUSTRIAL', 'G&T']
        text_upper = text.upper()
        for banco in bancos:
            if banco in text_upper:
                return banco
        return ''
    
    def _extract_tipo_operacion(self, text):
        """Extract operation type."""
        operaciones = [
            ('DEPOSITO EN EFECTIVO', ['deposito en efectivo', 'dep efectivo', 'deposito efectivo', 'efectivo']),
            ('DEPOSITO CON CHEQUE', ['deposito con cheque', 'dep cheque']),
            ('TRANSFERENCIA', ['transferencia', 'transf', 'transfer']),
            ('RETIRO', ['retiro', 'withdrawal']),
            ('PAGO DE SERVICIOS', ['pago de servicio', 'pago servicio']),
            ('PAGO', ['pago', 'payment'])
        ]
        text_lower = text.lower()
        for tipo, patrones in operaciones:
            for patron in patrones:
                if patron in text_lower:
                    return tipo
        return 'DEPOSITO'
    
    def _extract_fecha(self, text):
        """Extract and normalize date."""
        patterns = [
            r'(\d{4}[-/]\d{2}[-/]\d{2})',
            r'(\d{2}[-/]\d{2}[-/]\d{4})',
            r'(\d{2}[-/]\d{2}[-/]\d{2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return self._normalize_date(match.group(1))
        return ''
    
    def _normalize_date(self, date_str):
        """Normalize date to YYYY-MM-DD format."""
        date_str = date_str.replace('/', '-')
        formats = [('%Y-%m-%d', '%Y-%m-%d'), ('%d-%m-%Y', '%Y-%m-%d'), 
                   ('%d-%m-%y', '%Y-%m-%d'), ('%m-%d-%Y', '%Y-%m-%d')]
        for in_fmt, out_fmt in formats:
            try:
                return datetime.strptime(date_str, in_fmt).strftime(out_fmt)
            except ValueError:
                continue
        return date_str
    
    def _extract_hora(self, text):
        """Extract time from text."""
        match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', text)
        if match:
            hora = match.group(1)
            return hora if len(hora.split(':')) == 3 else hora + ':00'
        return ''
    
    def _extract_moneda(self, text):
        """Extract currency from text."""
        text_upper = text.upper()
        if 'USD' in text_upper or 'DOLAR' in text_upper:
            return 'USD'
        elif 'NIO' in text_upper or 'CORDOBA' in text_upper or 'C$' in text:
            return 'NIO'
        elif 'EUR' in text_upper:
            return 'EUR'
        elif '$' in text:
            return 'USD'
        return 'USD'
    
    def _extract_monto(self, text, pattern):
        """Extract monetary amount."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                pass
        return 0.00
    
    def _extract_monto_total(self, text):
        """Extract total amount - find largest number."""
        amounts = re.findall(r'[\$C]?\s*([\d,]+\.?\d*)', text)
        valid_amounts = []
        for a in amounts:
            try:
                val = float(a.replace(',', ''))
                if 1 < val < 1000000:  # Reasonable range
                    valid_amounts.append(val)
            except ValueError:
                continue
        return max(valid_amounts) if valid_amounts else 0.00
    
    def _extract_depositante(self, text):
        """Extract depositor name."""
        patterns = [
            r'(?:depositante|deposita|depositado por)[:\s]*([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?:\n|$)',
            r'(?:nombre)[:\s]*([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3:
                    return name
        return ''
    
    def _extract_identificaciones(self, text):
        """Extract identification numbers."""
        ids = []
        patterns = [
            r'(\d{13,16})\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s]{5,50})',
            r'(?:cedula|id)[:\s]*(\d{10,16})',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches[:3]:
                if isinstance(m, tuple):
                    ids.append(f"{m[0]} {m[1].strip()}")
                else:
                    ids.append(m)
        return ids
    
    def _extract_notas(self, text):
        """Extract notes."""
        patterns = [r'(?:nota|notas)[:\s]*(.+?)(?:\n\n|$)', r'(he revisado.+?correctos)']
        notes = []
        for p in patterns:
            matches = re.findall(p, text, re.IGNORECASE | re.DOTALL)
            notes.extend([m.strip()[:200] for m in matches if len(m.strip()) > 10])
        return ' '.join(notes[:2])
    
    def _check_firmas_requeridas(self, text):
        """Check if signatures required."""
        text_lower = text.lower()
        if 'no necesita' in text_lower or 'sin firma' in text_lower:
            return False
        return 'firma' in text_lower and 'requerida' in text_lower
    
    def _count_fields(self, data):
        """Count non-empty fields."""
        count = 0
        for section in data.values():
            if isinstance(section, dict):
                for v in section.values():
                    if v and v != 0:
                        count += 1
            elif section:
                count += 1
        return count
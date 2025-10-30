import os
import base64
import requests
import time
import firebase_admin
from firebase_admin import firestore
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel

class AIServices:
    """
    AI servisleri için sınıf
    """
    
    def __init__(self):
        # Gemini API Key
        self.gemini_api_key = "AIzaSyBRtYZYRcsS8ULYhDj3jUieBVIs6OVqVOE"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Firebase Vision için
        try:
            self.db = firestore.client()
        except Exception as e:            self.db = None
        
        # Google Cloud credentials (opsiyonel)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'path/to/service-account.json')
        
        # Gemini AI için (Vertex AI yerine REST API kullanıyoruz)
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'your-project-id')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        # Vertex AI sadece gerekirse kullanılacak
        try:
            vertexai.init(project=project_id, location=location)
            self.gemini_model = GenerativeModel("gemini-1.5-flash")
        except Exception as e:            self.gemini_model = None
    
    def _make_gemini_request(self, data, max_retries=3):
        """
        Gemini API isteği yap, retry mekanizması ile
        """
        for attempt in range(max_retries):
            try:
                headers = {
                    'Content-Type': 'application/json',
                }
                
                url = f"{self.gemini_base_url}?key={self.gemini_api_key}"
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return "Sonuç alınamadı."
                elif response.status_code == 503:                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        return "Gemini API şu anda meşgul. Lütfen daha sonra tekrar deneyin."
                else:                    return f"API Hatası: {response.status_code}"
                    
            except Exception as e:                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return f"Bağlantı hatası: {str(e)}"
        
        return "Tüm denemeler başarısız oldu."
    
    def analyze_image_with_firebase_vision(self, file_path_or_name):
        """
        Firebase Vision AI ile fotoğraf analizi
        """
        try:            # Firebase Storage'dan dosya adını al
            if '/' in file_path_or_name:
                # Firebase Storage path'inden dosya adını çıkar
                file_name = file_path_or_name.split('/')[-1]
            else:
                file_name = file_path_or_name
            
            # Firestore'dan extracted text'i kontrol et
            if self.db:
                try:
                    # Firebase Vision AI eklentisinin sonucunu bekle
                    time.sleep(3)  # Eklentinin işlemesi için bekle
                    
                    # Firestore'dan extracted text'i al
                    doc_ref = self.db.collection('extractedText').document(file_name)
                    doc = doc_ref.get()
                    
                    if doc.exists:
                        data = doc.to_dict()
                        extracted_text = data.get('text', '')                        return extracted_text
                    else:                        # Fallback olarak Gemini Vision kullan
                        if os.path.exists(file_path_or_name):
                            return self._analyze_with_gemini_vision(file_path_or_name)
                        else:
                            return "Firebase Vision AI sonucu bulunamadı ve dosya erişilebilir değil."
                        
                except Exception as e:                    # Fallback olarak Gemini Vision kullan
                    if os.path.exists(file_path_or_name):
                        return self._analyze_with_gemini_vision(file_path_or_name)
                    else:
                        return f"Firebase Vision AI hatası: {str(e)}"
            else:                if os.path.exists(file_path_or_name):
                    return self._analyze_with_gemini_vision(file_path_or_name)
                else:
                    return "Firebase bağlantısı yok ve dosya erişilebilir değil."
                
        except Exception as e:            return f"Vision analizi hatası: {str(e)}"
    
    def _analyze_with_gemini_vision(self, image_path):
        """
        Gemini Vision ile fotoğraf analizi (fallback)
        """
        try:
            # Fotoğrafı base64'e çevir
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            data = {
                "contents": [{
                    "parts": [
                        {
                            "text": "Bu fotoğraftaki metni çıkar ve sadece metni döndür. Eğer matematik sorusu varsa, soruyu ve şıkları ayrı ayrı belirt."
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            result = self._make_gemini_request(data)            return result
            
        except Exception as e:            return f"Gemini Vision hatası: {str(e)}"
    
    def get_gemini_solution(self, konu, ders, mesaj, vision_text):
        """
        Gemini AI ile çözüm üret
        """
        try:
            # Kısa ve öz çözüm için prompt
            prompt = f"""
Sen bir matematik öğretmenisin. Aşağıdaki soruyu kısa ve öz şekilde çöz.

SORU:
{vision_text}

KULLANICI MESAJI: {mesaj}

ÇÖZÜM FORMATI:
1. Verilen bilgiler
2. Kritik adımlar
3. Sonuç

ÖNEMLİ KURALLAR:
- Sadece düz metin kullan
- HTML tag'leri kullanma
- Matematiksel ifadeleri düzgün yaz (x² yerine x^2)
- Kısa ve öz olsun
- Sadece kritik adımları göster
- Sonucu net belirt
- Fotoğraftaki metin kısmını yazma, direkt çözüme geç

Çözümü başlat:
"""

            data = {
                "contents": [{
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }]
            }
            
            result = self._make_gemini_request(data)
            
            # Çıktıyı temizle
            cleaned_result = self._clean_ai_output(result)            return cleaned_result
            
        except Exception as e:            return f"Çözüm oluşturulurken hata: {str(e)}"
    
    def _clean_ai_output(self, text):
        """
        AI çıktısını temizle
        """
        import re
        
        # HTML tag'lerini kaldır
        text = re.sub(r'<[^>]+>', '', text)
        
        # Superscript'leri düzelt
        text = re.sub(r'<sup>(\d+)</sup>', r'^(\1)', text)
        text = re.sub(r'<sup>([^<]+)</sup>', r'^(\1)', text)
        
        # Diğer HTML tag'lerini temizle
        text = text.replace('<br>', '\n')
        text = text.replace('<p>', '\n')
        text = text.replace('</p>', '\n')
        text = text.replace('<strong>', '**')
        text = text.replace('</strong>', '**')
        text = text.replace('<em>', '*')
        text = text.replace('</em>', '*')
        
        # Fazla boşlukları temizle
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text 
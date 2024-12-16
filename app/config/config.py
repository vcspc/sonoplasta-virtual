import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

class Config:
    # Configurações gerais
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-padrao')
    UPLOAD_PASSWORD = os.getenv('UPLOAD_PASSWORD', 'senha_padrao')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # Configurações de diretórios
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FILES_DIR = os.path.join(BASE_DIR, 'files')
    VIDEOS_DIR = os.path.join(BASE_DIR, 'videos')
    
    # Configurações SSL
    SSL_CERT = os.path.join(BASE_DIR, 'cert.pem')
    SSL_KEY = os.path.join(BASE_DIR, 'key.pem')
    
    # Extensões permitidas
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov'}
    PRESENTATION_EXTENSIONS = {'.ppt', '.pptx', '.odp', '.key', '.pdf'}
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.wma'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    @property
    def ALLOWED_EXTENSIONS(self):
        return self.VIDEO_EXTENSIONS | self.PRESENTATION_EXTENSIONS | self.AUDIO_EXTENSIONS | self.IMAGE_EXTENSIONS 
from flask import Flask
import os
import logging
import threading
from .routes.main_routes import main
from .utils.helpers import create_self_signed_cert, setup_ssl_context, ensure_directories_exist
from .config.config import Config
from qr_window import QRWindow

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    config = Config()
    
    # Registra os blueprints
    app.register_blueprint(main)
    
    # Garante que os diretórios necessários existam
    directories = [config.FILES_DIR, config.VIDEOS_DIR]
    if not ensure_directories_exist(directories):
        logger.error("Erro ao criar diretórios necessários")
        return None
    
    # Cria o certificado SSL se não existir
    if not (os.path.exists(config.SSL_CERT) and os.path.exists(config.SSL_KEY)):
        logger.info("Criando certificado SSL...")
        if not create_self_signed_cert(config.SSL_CERT, config.SSL_KEY):
            logger.error("Erro ao criar certificado SSL")
            return None
    
    # Configura o contexto SSL
    ssl_context = setup_ssl_context(config.SSL_CERT, config.SSL_KEY)
    if not ssl_context:
        logger.error("Erro ao configurar contexto SSL")
        return None
    
    # Inicia a janela QR Code em uma thread separada
    def show_qr():
        qr_window = QRWindow()
        qr_window.run()
    
    qr_thread = threading.Thread(target=show_qr)
    qr_thread.daemon = True
    qr_thread.start()
    
    return app, ssl_context 
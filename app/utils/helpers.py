import os
import logging
import ssl
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_self_signed_cert(cert_path, key_path):
    """Cria um certificado SSL auto-assinado"""
    try:
        # Gera uma chave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Cria o certificado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost")
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).sign(private_key, hashes.SHA256())

        # Salva o certificado e a chave
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        logger.info("Certificado SSL criado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar certificado SSL: {str(e)}")
        return False

def find_file(search_term, files_dir, video_extensions, presentation_extensions, audio_extensions):
    """Procura por um arquivo com base no termo de pesquisa"""
    logger.info(f"Procurando arquivo com termo: {search_term}")
    files_folder = Path(files_dir)
    
    if not files_folder.exists():
        logger.warning("Pasta 'files' não encontrada")
        os.makedirs(files_dir, exist_ok=True)
        logger.info("Pasta 'files' criada")
        return None, None
    
    for file in files_folder.glob('**/*'):
        if search_term.lower() in file.name.lower():
            if file.suffix.lower() in video_extensions:
                logger.info(f"Vídeo encontrado: {file}")
                return str(file.absolute()), 'video'
            elif file.suffix.lower() in presentation_extensions:
                logger.info(f"Apresentação encontrada: {file}")
                return str(file.absolute()), 'presentation'
            elif file.suffix.lower() in audio_extensions:
                logger.info(f"Áudio encontrado: {file}")
                return str(file.absolute()), 'audio'
    
    logger.warning(f"Nenhum arquivo encontrado com o termo: {search_term}")
    return None, None

def setup_ssl_context(cert_path, key_path):
    """Configura o contexto SSL para o servidor"""
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_path, key_path)
        return context
    except Exception as e:
        logger.error(f"Erro ao configurar contexto SSL: {str(e)}")
        return None

def ensure_directories_exist(directories):
    """Garante que os diretórios necessários existam"""
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Diretório verificado/criado: {directory}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório {directory}: {str(e)}")
            return False
    return True 
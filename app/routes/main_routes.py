from flask import Blueprint, request, jsonify, redirect, url_for, render_template, Response
from pathlib import Path
import os
import logging
import pyautogui
from ..services.media_control_service import MediaControlService
from ..services.system_control_service import SystemControlService
from ..services.presentation_service import PresentationService
from ..services.youtube_service import YouTubeService
from ..utils.helpers import find_file
from ..config.config import Config
from werkzeug.utils import secure_filename
import subprocess
import json
import time

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)
config = Config()

# Instancia os serviços
media_control = MediaControlService()
system_control = SystemControlService()
presentation_control = PresentationService()
youtube_service = YouTubeService(config.YOUTUBE_API_KEY)

UPLOAD_FOLDER = config.FILES_DIR
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'ppt', 'pptx', 'odp', 'key', 'pdf', 
                     'mp3', 'wav', 'ogg', 'm4a', 'wma', 'jpg', 'jpeg', 'png', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.before_request
def before_request():
    if request.scheme == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url)

@main.route('/')
def home():
    """Página inicial com instruções de uso"""
    logger.info("Página inicial acessada")
    return render_template('index.html')

@main.route('/api/search')
def api_search():
    """Endpoint para buscar arquivos e retornar lista de resultados"""
    search_term = request.args.get('term', '').lower()
    logger.info(f"Buscando arquivos com termo: {search_term}")
    
    files_folder = Path(config.FILES_DIR)
    if not files_folder.exists():
        logger.warning("Pasta 'files' não encontrada")
        os.makedirs(config.FILES_DIR, exist_ok=True)
        logger.info("Pasta 'files' criada")
        return jsonify({'videos': []})
    
    files = []
    for file in files_folder.glob('**/*'):
        if search_term in file.name.lower():
            file_type = None
            if file.suffix.lower() in config.VIDEO_EXTENSIONS:
                file_type = 'video'
            elif file.suffix.lower() in config.PRESENTATION_EXTENSIONS:
                file_type = 'presentation'
            elif file.suffix.lower() in config.AUDIO_EXTENSIONS:
                file_type = 'audio'
                
            if file_type:
                files.append({
                    'name': file.name,
                    'path': str(file.absolute()),
                    'type': file_type
                })
    
    logger.info(f"Arquivos encontrados: {files}")
    return jsonify({'videos': files})

@main.route('/search/<term>', methods=['GET'])
def search_get(term):
    """Endpoint GET para buscar arquivos diretamente pelo navegador"""
    logger.info(f"Recebida requisição GET para buscar: {term}")
    
    try:
        file_path, file_type = find_file(
            term,
            config.FILES_DIR,
            config.VIDEO_EXTENSIONS,
            config.PRESENTATION_EXTENSIONS,
            config.AUDIO_EXTENSIONS
        )
        
        if not file_path:
            error_msg = f"Arquivo não encontrado para o termo: {term}"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'dica': 'Verifique se o arquivo está na pasta "files" e se o nome está correto'
            }), 404
        
        success, error = media_control.play_media(file_path, file_type)
        
        if success:
            return jsonify({
                'message': 'Arquivo iniciado com sucesso',
                'file_path': file_path,
                'file_type': file_type
            })
        else:
            return jsonify({'error': error}), 500
            
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@main.route('/volume/<action>', methods=['GET'])
def volume_get(action):
    """Endpoint GET para controlar volume"""
    logger.info(f"Recebida requisição para alterar volume: {action}")
    
    if action not in ['up', 'down']:
        error_msg = f"Ação inválida: {action}. Use 'up' ou 'down'"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 400
    
    success, error = media_control.adjust_volume(action)
    if success:
        return jsonify({'message': f'Volume {action} executado com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/play', methods=['POST', 'GET'])
def play():
    """Endpoint para play/pause"""
    logger.info("Recebida requisição para play/pause")
    success, error = media_control.toggle_play_pause()
    if success:
        return jsonify({'message': 'Comando executado com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/volume/mute', methods=['POST', 'GET'])
def toggle_mute():
    """Endpoint para alternar entre mudo/desmudo"""
    success, error = media_control.toggle_mute()
    if success:
        return jsonify({'message': 'Volume alternado com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/fullscreen', methods=['POST', 'GET'])
def toggle_fullscreen():
    """Endpoint para alternar tela cheia"""
    success, error = media_control.toggle_fullscreen()
    if success:
        return jsonify({'message': 'Tela cheia alternada com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/hide-controls', methods=['POST', 'GET'])
def hide_controls():
    """Endpoint para ocultar os controles de mídia"""
    success, error = media_control.hide_controls()
    if success:
        return jsonify({'message': 'Controles ocultados com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/presentation/next', methods=['POST', 'GET'])
def next_slide():
    """Endpoint para avançar slide"""
    success, error = presentation_control.next_slide()
    if success:
        return jsonify({'message': 'Próximo slide'})
    else:
        return jsonify({'error': error}), 500

@main.route('/presentation/previous', methods=['POST', 'GET'])
def previous_slide():
    """Endpoint para voltar slide"""
    success, error = presentation_control.previous_slide()
    if success:
        return jsonify({'message': 'Slide anterior'})
    else:
        return jsonify({'error': error}), 500

@main.route('/presentation/fullscreen', methods=['POST', 'GET'])
def toggle_presentation_fullscreen():
    """Endpoint para alternar modo apresentação"""
    success, error = presentation_control.toggle_fullscreen()
    if success:
        return jsonify({'message': 'Modo apresentação alternado'})
    else:
        return jsonify({'error': error}), 500

@main.route('/close-app', methods=['POST', 'GET'])
def close_app():
    """Endpoint para fechar o aplicativo atual"""
    success, error = system_control.close_app()
    if success:
        return jsonify({'message': 'Comando enviado com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/system/minimize', methods=['POST', 'GET'])
def minimize_window():
    """Endpoint para minimizar todas as janelas"""
    success, error = system_control.minimize_window()
    if success:
        return jsonify({'message': 'Área de trabalho mostrada com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/system/maximize', methods=['POST', 'GET'])
def maximize_window():
    """Endpoint para maximizar a janela atual"""
    success, error = system_control.maximize_window()
    if success:
        return jsonify({'message': 'Janela maximizada com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/system/switch-app', methods=['POST', 'GET'])
def switch_app():
    """Endpoint para alternar entre aplicativos"""
    success, error = system_control.switch_app()
    if success:
        return jsonify({'message': 'Alternado entre aplicativos com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/youtube/search')
def youtube_search():
    """Endpoint para buscar vídeos no YouTube"""
    query = request.args.get('query', '')
    videos, error = youtube_service.search_videos(query)
    if videos is not None:
        return jsonify({'videos': videos})
    else:
        return jsonify({'error': error}), 500

@main.route('/youtube/play/<video_id>')
def youtube_play(video_id):
    """Endpoint para abrir um vídeo do YouTube"""
    success, error = youtube_service.play_video(video_id)
    if success:
        return jsonify({'message': 'Vídeo aberto com sucesso'})
    else:
        return jsonify({'error': error}), 500

@main.route('/youtube/fullscreen', methods=['POST', 'GET'])
def youtube_fullscreen():
    """Endpoint para alternar tela cheia do YouTube"""
    try:
        pyautogui.press('f')
        return jsonify({'message': 'Comando de tela cheia enviado'})
    except Exception as e:
        error_msg = f"Erro ao alternar tela cheia: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@main.route('/youtube/rewind', methods=['POST', 'GET'])
def youtube_rewind():
    """Endpoint para retroceder o vídeo do YouTube em 10 segundos"""
    try:
        # Pressiona a tecla J para retroceder 10 segundos no YouTube
        pyautogui.press('j')
        return jsonify({'message': 'Vídeo retrocedido em 10 segundos'})
    except Exception as e:
        error_msg = f"Erro ao retroceder vídeo: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@main.route('/system/close-window', methods=['POST', 'GET'])
def close_window():
    """Endpoint para fechar a janela atual usando Alt+F4"""
    try:
        pyautogui.hotkey('alt', 'f4')
        return jsonify({'message': 'Janela fechada com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao fechar janela: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@main.route('/upload')
def upload_page():
    """Renderiza a página de upload"""
    return render_template('upload.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    """Processa o upload de arquivos"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    password = request.form.get('password')
    category = request.form.get('category', '')
    
    # Validar senha (você pode modificar a senha conforme necessário)
    if password != config.UPLOAD_PASSWORD:
        return jsonify({'error': 'Senha incorreta'}), 401
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Criar pasta da categoria se especificada
        upload_path = UPLOAD_FOLDER
        if category:
            upload_path = os.path.join(UPLOAD_FOLDER, category)
            os.makedirs(upload_path, exist_ok=True)
        
        try:
            file.save(os.path.join(upload_path, filename))
            return jsonify({
                'message': 'Arquivo enviado com sucesso',
                'filename': filename
            })
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {str(e)}")
            return jsonify({'error': 'Erro ao salvar arquivo'}), 500
    
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400 

@main.route('/doxologia')
def doxologia_page():
    """Renderiza a página de doxologia"""
    return render_template('doxologia.html')

@main.route('/api/doxologia/<category>')
def get_doxologia_files(category):
    """Retorna os arquivos de uma categoria específica da doxologia"""
    try:
        category_path = os.path.join(config.FILES_DIR, category)
        
        if not os.path.exists(category_path):
            os.makedirs(category_path, exist_ok=True)
            return jsonify({'files': []})
        
        files = []
        for file in os.listdir(category_path):
            file_path = os.path.join(category_path, file)
            if os.path.isfile(file_path):
                extension = os.path.splitext(file)[1].lower()
                file_type = None
                
                if extension in config.VIDEO_EXTENSIONS:
                    file_type = 'video'
                elif extension in config.AUDIO_EXTENSIONS:
                    file_type = 'audio'
                elif extension in config.PRESENTATION_EXTENSIONS:
                    file_type = 'presentation'
                
                if file_type:
                    files.append({
                        'name': file,
                        'type': file_type,
                        'path': file_path
                    })
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Erro ao listar arquivos da categoria {category}: {str(e)}")
        return jsonify({'error': str(e)}), 500 

@main.route('/youtube-download')
def youtube_download_page():
    """Renderiza a página de download do YouTube"""
    return render_template('youtube_download.html')

@main.route('/youtube/download', methods=['POST', 'GET'])
def download_youtube():
    """Processa o download de vídeos do YouTube usando yt-dlp"""
    try:
        # Pega os dados dependendo do método da requisição
        if request.method == 'POST':
            data = request.get_json()
            url = data.get('url')
            category = data.get('category')
            # Retorna imediatamente após iniciar o processo
            return jsonify({'status': 'iniciado'})
        else:  # GET
            url = request.args.get('url')
            category = request.args.get('category')

        if not url:
            return jsonify({'error': 'URL não fornecida'}), 400

        # Configura o diretório de download
        download_path = config.FILES_DIR
        if category:
            download_path = os.path.join(download_path, category)
            os.makedirs(download_path, exist_ok=True)

        # Configura o comando yt-dlp
        command = [
            'yt-dlp',
            '--no-check-certificate',
            '-f', 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]',
            '--merge-output-format', 'mp4',
            '--audio-format', 'aac',
            '--audio-quality', '0',
            '--postprocessor-args', 'ffmpeg:-c:v libx264 -c:a aac -ar 44100 -b:a 192k -strict experimental',
            '-o', os.path.join(download_path, '%(title)s.%(ext)s'),
            '--newline',
            '--progress',
            '--progress-template', '%(progress._percent_str)s',
            url
        ]

        def generate():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )

                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        try:
                            progress = float(output.strip().replace('%', ''))
                            yield f"data: {json.dumps({'progress': progress})}\n\n"
                        except (ValueError, TypeError):
                            continue

                # Verifica se houve erro
                if process.returncode != 0:
                    error = process.stderr.read()
                    yield f"data: {json.dumps({'error': str(error)})}\n\n"
                else:
                    yield f"data: {json.dumps({'completed': True})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                if 'process' in locals():
                    try:
                        process.terminate()
                    except:
                        pass

        response = Response(generate(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        return response

    except Exception as e:
        logger.error(f"Erro no download do YouTube: {str(e)}")
        return jsonify({'error': str(e)}), 500
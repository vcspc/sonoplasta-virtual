from flask import Flask, request, jsonify, redirect, url_for
import pyautogui
import os
from pathlib import Path
import subprocess
import logging
import ssl
import secrets
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variável global para controlar o processo do vídeo
video_process = None
video_paused = False

def create_self_signed_cert():
    """Cria um certificado SSL auto-assinado"""
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
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open("key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

def find_video(search_term):
    """Procura por um arquivo de vídeo com base no termo de pesquisa"""
    logger.info(f"Procurando vídeo com termo: {search_term}")
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    videos_folder = Path('videos')
    
    if not videos_folder.exists():
        logger.warning("Pasta 'videos' não encontrada")
        return None
    
    all_files = list(videos_folder.glob('**/*'))
    logger.info(f"Arquivos encontrados na pasta: {[str(f) for f in all_files]}")
    
    for file in videos_folder.glob('**/*'):
        if file.suffix.lower() in video_extensions and search_term.lower() in file.name.lower():
            logger.info(f"Vídeo encontrado: {file}")
            return str(file.absolute())
    
    logger.warning(f"Nenhum vídeo encontrado com o termo: {search_term}")
    return None

@app.route('/')
def home():
    """Página inicial com instruções de uso"""
    logger.info("Página inicial acessada")
    # Redireciona HTTP para HTTPS
    if request.scheme == 'http':
        return redirect(url_for('home', _scheme='https', _external=True))

    return '''
    <html>
        <head>
            <title>API de Controle de Vídeo</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <style>
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }

                body { 
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    padding: 20px;
                    min-height: 100vh;
                }

                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .search-container {
                    margin: 20px 0;
                    width: 100%;
                }

                #searchInput {
                    width: 100%;
                    padding: 15px;
                    font-size: 16px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    transition: border-color 0.3s;
                }

                #searchInput:focus {
                    outline: none;
                    border-color: #0056b3;
                }

                #searchResults {
                    list-style: none;
                    padding: 0;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    max-height: 300px;
                    overflow-y: auto;
                    display: none;
                    background-color: white;
                }

                #searchResults li {
                    padding: 15px;
                    border-bottom: 1px solid #ddd;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }

                #searchResults li:last-child {
                    border-bottom: none;
                }

                #searchResults li:hover {
                    background-color: #f0f0f0;
                }

                .warning {
                    color: #856404;
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    text-align: center;
                }

                h1 {
                    color: #333;
                    margin-bottom: 20px;
                    text-align: center;
                    font-size: 24px;
                }

                .controls {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }

                .controls-group {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 15px;
                }

                .volume-controls {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    justify-content: center;
                }

                .control-button {
                    background: none;
                    border: 2px solid #ddd;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 12px;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s;
                    background-color: white;
                }

                .control-button:hover {
                    background-color: #e9ecef;
                    transform: scale(1.1);
                    border-color: #0056b3;
                }

                .control-button:active {
                    background-color: #dee2e6;
                    transform: scale(0.95);
                }

                .control-button i {
                    color: #495057;
                }

                .now-playing {
                    text-align: center;
                    margin: 15px 0;
                    padding: 10px;
                    color: #6c757d;
                    font-style: italic;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    word-break: break-word;
                }

                .muted {
                    color: #dc3545 !important;
                }

                /* Estilos para Mobile */
                @media (max-width: 600px) {
                    body {
                        padding: 10px;
                    }

                    .container {
                        padding: 15px;
                    }

                    h1 {
                        font-size: 20px;
                    }

                    .control-button {
                        width: 45px;
                        height: 45px;
                        font-size: 18px;
                    }

                    .controls {
                        padding: 15px;
                    }

                    .controls-group {
                        gap: 10px;
                    }

                    #searchInput {
                        padding: 12px;
                        font-size: 14px;
                    }

                    .warning {
                        padding: 12px;
                        font-size: 14px;
                    }

                    #searchResults li {
                        padding: 12px;
                        font-size: 14px;
                    }
                }

                /* Suporte para telas muito pequenas */
                @media (max-width: 350px) {
                    .controls-group {
                        flex-direction: column;
                        align-items: center;
                    }

                    .volume-controls {
                        width: 100%;
                        justify-content: center;
                    }
                }

                /* Suporte para Dark Mode */
                @media (prefers-color-scheme: dark) {
                    body {
                        background-color: #1a1a1a;
                        color: #fff;
                    }

                    .container {
                        background-color: #2d2d2d;
                    }

                    #searchInput {
                        background-color: #3d3d3d;
                        color: #fff;
                        border-color: #4d4d4d;
                    }

                    #searchResults {
                        background-color: #2d2d2d;
                        border-color: #4d4d4d;
                    }

                    #searchResults li {
                        border-color: #4d4d4d;
                    }

                    #searchResults li:hover {
                        background-color: #3d3d3d;
                    }

                    .control-button {
                        background-color: #3d3d3d;
                        border-color: #4d4d4d;
                    }

                    .control-button:hover {
                        background-color: #4d4d4d;
                    }

                    .control-button i {
                        color: #fff;
                    }

                    .controls {
                        background-color: #2d2d2d;
                    }

                    .now-playing {
                        background-color: #2d2d2d;
                        color: #adb5bd;
                    }

                    h1 {
                        color: #fff;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Sonoplasta Virtual</h1>
                
                <div class="search-container">
                    <input type="text" 
                           id="searchInput" 
                           placeholder="Digite para buscar vídeos..."
                           autocomplete="off">
                    <ul id="searchResults"></ul>
                </div>

                <div class="warning">
                    <strong>Dica:</strong> Digite parte do nome do vídeo para buscar
                </div>

                <div id="nowPlaying" class="now-playing" style="display: none;">
                    Reproduzindo: <span id="currentVideo">Nenhum vídeo</span>
                </div>

                <div class="controls">
                    <div class="controls-group">
                        <div class="volume-controls">
                            <button class="control-button" onclick="adjustVolume('down')" title="Diminuir Volume">
                                <i class="fas fa-volume-down"></i>
                            </button>
                            <button class="control-button" onclick="toggleMute()" title="Mudo/Desmudo" id="muteButton">
                                <i class="fas fa-volume-up" id="muteIcon"></i>
                            </button>
                            <button class="control-button" onclick="adjustVolume('up')" title="Aumentar Volume">
                                <i class="fas fa-volume-up"></i>
                            </button>
                        </div>
                        <button class="control-button" onclick="togglePlayPause()" title="Play/Pause">
                            <i class="fas fa-play" id="playPauseIcon"></i>
                        </button>
                        <button class="control-button" onclick="toggleFullscreen()" title="Tela Cheia (F11)">
                            <i class="fas fa-expand" id="fullscreenIcon"></i>
                        </button>
                        <button class="control-button" onclick="hideControls()" title="Ocultar Controles do Player (H)">
                            <i class="fas fa-eye-slash"></i>
                        </button>
                    </div>
                </div>
            </div>

            <script>
                const searchInput = document.getElementById('searchInput');
                const searchResults = document.getElementById('searchResults');
                const nowPlaying = document.getElementById('nowPlaying');
                const currentVideo = document.getElementById('currentVideo');
                const playPauseIcon = document.getElementById('playPauseIcon');
                const muteIcon = document.getElementById('muteIcon');
                const fullscreenIcon = document.getElementById('fullscreenIcon');
                let timeoutId;
                let isPlaying = false;
                let isMuted = false;
                let isFullscreen = false;

                function toggleMute() {
                    fetch('/volume/mute')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            } else {
                                isMuted = !isMuted;
                                muteIcon.className = isMuted ? 'fas fa-volume-mute muted' : 'fas fa-volume-up';
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao alternar mudo');
                        });
                }

                function togglePlayPause() {
                    fetch('/play')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            } else {
                                isPlaying = !isPlaying;
                                playPauseIcon.className = isPlaying ? 'fas fa-pause' : 'fas fa-play';
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao controlar reprodução');
                        });
                }

                function adjustVolume(action) {
                    fetch(`/volume/${action}`)
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            } else if (isMuted) {
                                // Se estava mudo, desativa o mudo ao ajustar o volume
                                isMuted = false;
                                muteIcon.className = 'fas fa-volume-up';
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao ajustar volume');
                        });
                }

                function toggleFullscreen() {
                    fetch('/fullscreen')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            } else {
                                isFullscreen = !isFullscreen;
                                fullscreenIcon.className = isFullscreen ? 'fas fa-compress' : 'fas fa-expand';
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao alternar tela cheia');
                        });
                }

                function hideControls() {
                    fetch('/hide-controls')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao ocultar controles');
                        });
                }

                searchInput.addEventListener('input', function() {
                    clearTimeout(timeoutId);
                    const searchTerm = this.value.trim();
                    
                    if (searchTerm === '') {
                        searchResults.style.display = 'none';
                        return;
                    }

                    timeoutId = setTimeout(() => {
                        fetch(`/api/search?term=${encodeURIComponent(searchTerm)}`)
                            .then(response => response.json())
                            .then(data => {
                                searchResults.innerHTML = '';
                                
                                if (data.videos && data.videos.length > 0) {
                                    data.videos.forEach(video => {
                                        const li = document.createElement('li');
                                        li.textContent = video.name;
                                        li.onclick = () => {
                                            fetch(`/search/${encodeURIComponent(video.name)}`)
                                                .then(response => response.json())
                                                .then(result => {
                                                    if (result.error) {
                                                        alert(result.error);
                                                    } else {
                                                        nowPlaying.style.display = 'block';
                                                        currentVideo.textContent = video.name;
                                                        isPlaying = true;
                                                        playPauseIcon.className = 'fas fa-pause';
                                                    }
                                                })
                                                .catch(error => {
                                                    console.error('Erro:', error);
                                                    alert('Erro ao reproduzir o vídeo');
                                                });
                                        };
                                        searchResults.appendChild(li);
                                    });
                                    searchResults.style.display = 'block';
                                } else {
                                    const li = document.createElement('li');
                                    li.textContent = 'Nenhum vídeo encontrado';
                                    searchResults.appendChild(li);
                                    searchResults.style.display = 'block';
                                }
                            })
                            .catch(error => {
                                console.error('Erro:', error);
                                searchResults.innerHTML = '<li>Erro ao buscar vídeos</li>';
                                searchResults.style.display = 'block';
                            });
                    }, 300);
                });

                // Fecha a lista de resultados quando clicar fora
                document.addEventListener('click', function(e) {
                    if (!searchResults.contains(e.target) && e.target !== searchInput) {
                        searchResults.style.display = 'none';
                    }
                });

                // Atalhos de teclado
                document.addEventListener('keydown', function(e) {
                    // Espaço para play/pause
                    if (e.code === 'Space' && document.activeElement !== searchInput) {
                        e.preventDefault();
                        togglePlayPause();
                    }
                    // Seta para cima para aumentar volume
                    else if (e.code === 'ArrowUp' && document.activeElement !== searchInput) {
                        e.preventDefault();
                        adjustVolume('up');
                    }
                    // Seta para baixo para diminuir volume
                    else if (e.code === 'ArrowDown' && document.activeElement !== searchInput) {
                        e.preventDefault();
                        adjustVolume('down');
                    }
                    // M para mudo/desmudo
                    else if (e.code === 'KeyM' && document.activeElement !== searchInput) {
                        e.preventDefault();
                        toggleMute();
                    }
                    // F11 para tela cheia
                    if (e.code === 'F11' && document.activeElement !== searchInput) {
                        e.preventDefault();
                        toggleFullscreen();
                    }
                    // H para ocultar controles
                    if (e.code === 'KeyH' && document.activeElement !== searchInput) {
                        e.preventDefault();
                        hideControls();
                    }
                });
            </script>
        </body>
    </html>
    '''

@app.route('/api/search')
def api_search():
    """Endpoint para buscar vídeos e retornar lista de resultados"""
    search_term = request.args.get('term', '').lower()
    logger.info(f"Buscando vídeos com termo: {search_term}")
    
    videos_folder = Path('videos')
    if not videos_folder.exists():
        return jsonify({'videos': []})
    
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    videos = []
    
    for file in videos_folder.glob('**/*'):
        if file.suffix.lower() in video_extensions and search_term in file.name.lower():
            videos.append({
                'name': file.name,
                'path': str(file.absolute())
            })
    
    return jsonify({'videos': videos})

@app.before_request
def before_request():
    if request.scheme == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url)

@app.route('/search/<term>', methods=['GET'])
def search_get(term):
    """Endpoint GET para buscar vídeos diretamente pelo navegador"""
    logger.info(f"Recebida requisição GET para buscar: {term}")
    global video_process
    
    try:
        video_path = find_video(term)
        
        if not video_path:
            error_msg = f"Vídeo não encontrado para o termo: {term}"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'dica': 'Verifique se o vídeo está na pasta "videos" e se o nome está correto'
            }), 404
        
        # Se já existe um vídeo em reprodução, fecha ele
        if video_process is not None:
            try:
                video_process.terminate()
                logger.info("Processo de vídeo anterior terminado")
            except Exception as e:
                logger.error(f"Erro ao terminar processo anterior: {e}")
        
        try:
            # No Windows, usa o comando start /max para tela cheia
            if os.name == 'nt':
                # Primeiro, maximiza o player padrão
                video_process = subprocess.Popen(['start', '/max', '', video_path], shell=True)
                # Depois de um pequeno delay, simula Alt+Enter para forçar tela cheia
                time.sleep(1.5)
                pyautogui.hotkey('alt', 'enter')
            else:
                # No Linux/Mac
                if os.system('which vlc > /dev/null') == 0:
                    # Se tiver VLC instalado, usa ele em tela cheia
                    video_process = subprocess.Popen(['vlc', '--fullscreen', video_path])
                else:
                    # Caso contrário, usa o player padrão
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    video_process = subprocess.Popen([opener, video_path])
                    time.sleep(1.5)
                    pyautogui.hotkey('alt', 'enter')
            
            logger.info(f"Vídeo iniciado com sucesso em tela cheia: {video_path}")
            return jsonify({
                'message': 'Vídeo iniciado com sucesso',
                'video_path': video_path
            })
        except Exception as e:
            error_msg = f"Erro ao abrir o vídeo: {str(e)}"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'video_path': video_path
            }), 500
            
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/search', methods=['POST'])
def search_post():
    """Endpoint POST original para buscar vídeos"""
    logger.info("Recebida requisição POST para buscar vídeo")
    global video_process
    
    try:
        data = request.get_json()
        logger.info(f"Dados recebidos: {data}")
        
        if not data or 'term' not in data:
            error_msg = "Termo de pesquisa não fornecido no JSON"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'exemplo_correto': {'term': 'nome_do_video'}
            }), 400
        
        search_term = data['term']
        return search_get(search_term)
        
    except Exception as e:
        error_msg = f"Erro ao processar requisição POST: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 400

@app.route('/volume/<action>', methods=['GET'])
def volume_get(action):
    """Endpoint GET para controlar volume diretamente pelo navegador"""
    logger.info(f"Recebida requisição para alterar volume: {action}")
    
    if action not in ['up', 'down']:
        error_msg = f"Ação inválida: {action}. Use 'up' ou 'down'"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 400
    
    try:
        if action == 'up':
            pyautogui.press('volumeup')
        else:
            pyautogui.press('volumedown')
        
        logger.info(f"Volume {action} executado com sucesso")
        return jsonify({'message': f'Volume {action} executado com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao controlar volume: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/play', methods=['POST', 'GET'])
def play():
    logger.info("Recebida requisição para play/pause")
    global video_paused, video_process
    
    if video_process is None:
        error_msg = "Nenhum vídeo em reprodução"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 400
    
    try:
        # Simula pressionar a tecla de espaço para play/pause
        pyautogui.press('space')
        video_paused = not video_paused
        status = 'pausado' if video_paused else 'reproduzindo'
        
        logger.info(f"Vídeo {status} com sucesso")
        return jsonify({'message': f'Vídeo {status}'})
    except Exception as e:
        error_msg = f"Erro ao controlar reprodução: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/volume/mute', methods=['POST', 'GET'])
def toggle_mute():
    """Endpoint para alternar entre mudo/desmudo"""
    try:
        pyautogui.press('volumemute')
        return jsonify({'message': 'Volume alternado com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao controlar volume: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/fullscreen', methods=['POST', 'GET'])
def toggle_fullscreen():
    """Endpoint para alternar tela cheia"""
    try:
        pyautogui.press('f11')
        return jsonify({'message': 'Tela cheia alternada com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao alternar tela cheia: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/hide-controls', methods=['POST', 'GET'])
def hide_controls():
    """Endpoint para ocultar os controles de mídia do player"""
    try:
        # Simula um clique na tela para esconder os controles
        x, y = pyautogui.size()
        # Clica no centro da tela
        pyautogui.click(x//2, y//2)
        return jsonify({'message': 'Controles ocultados com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao ocultar controles: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    # Cria a pasta de vídeos se não existir
    videos_path = os.path.join(os.getcwd(), 'videos')
    os.makedirs(videos_path, exist_ok=True)
    logger.info(f"Pasta de vídeos criada/verificada em: {videos_path}")
    
    # Lista os vídeos disponíveis no início
    logger.info("Vídeos disponíveis:")
    for video in Path(videos_path).glob('**/*'):
        if video.suffix.lower() in ('.mp4', '.avi', '.mkv', '.mov'):
            logger.info(f"- {video.name}")
    
    # Cria o certificado SSL se não existir
    if not (os.path.exists("cert.pem") and os.path.exists("key.pem")):
        logger.info("Criando certificado SSL...")
        create_self_signed_cert()
        logger.info("Certificado SSL criado com sucesso!")
    
    # Configuração do contexto SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    # Executa o servidor com HTTPS
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True) 
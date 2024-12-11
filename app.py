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

def find_file(search_term):
    """Procura por um arquivo (vídeo, apresentação ou áudio) com base no termo de pesquisa"""
    logger.info(f"Procurando arquivo com termo: {search_term}")
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    presentation_extensions = ('.ppt', '.pptx', '.odp', '.key', '.pdf')
    audio_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.wma')
    files_folder = Path('files')
    
    if not files_folder.exists():
        logger.warning("Pasta 'files' não encontrada")
        os.makedirs('files', exist_ok=True)
        logger.info("Pasta 'files' criada")
        return None, None
    
    all_files = list(files_folder.glob('**/*'))
    logger.info(f"Arquivos encontrados na pasta: {[str(f) for f in all_files]}")
    
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
                    max-width: 300px;
                    margin: 20px auto;
                    background-color: #f8f9fa;
                    border-radius: 20px;
                    padding: 25px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }

                .section-title {
                    font-size: 1em;
                    color: #666;
                    text-align: center;
                    margin: 15px 0 10px 0;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                .controls-group {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 20px;
                    margin-bottom: 25px;
                }

                .volume-controls,
                .playback-controls,
                .presentation-controls,
                .screen-controls {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    width: 100%;
                }

                .control-button {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background-color: white;
                    border: none;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: all 0.2s;
                }

                .control-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }

                .control-button:active {
                    transform: translateY(0);
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }

                /* Suporte para Dark Mode */
                @media (prefers-color-scheme: dark) {
                    .controls {
                        background-color: #2d2d2d;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    }

                    .control-button {
                        background-color: #3d3d3d;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    }

                    .section-title {
                        color: #adb5bd;
                    }
                }

                /* Estilos para Mobile */
                @media (max-width: 350px) {
                    .controls {
                        padding: 15px;
                    }

                    .control-button {
                        width: 50px;
                        height: 50px;
                    }
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

                .file-icon {
                    margin-right: 10px;
                    width: 20px;
                    text-align: center;
                }
                .file-type {
                    font-size: 12px;
                    color: #6c757d;
                    margin-left: 10px;
                    padding: 2px 6px;
                    border-radius: 4px;
                    background-color: #e9ecef;
                }

                .section-title {
                    font-size: 1.2em;
                    color: #666;
                    margin: 15px 0 10px 0;
                    padding-bottom: 5px;
                    border-bottom: 1px solid #ddd;
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
                    margin-bottom: 20px;
                }

                .controls-group:last-child {
                    margin-bottom: 0;
                }

                /* Suporte para Dark Mode */
                @media (prefers-color-scheme: dark) {
                    .section-title {
                        color: #adb5bd;
                        border-bottom-color: #4d4d4d;
                    }
                }

                /* Estilos para Mobile */
                @media (max-width: 600px) {
                    .section-title {
                        font-size: 1.1em;
                        margin: 12px 0 8px 0;
                    }
                }

                .control-button.danger {
                    color: #dc3545;
                }

                .control-button.danger:hover {
                    background-color: #dc3545;
                    color: white;
                }

                /* Suporte para Dark Mode */
                @media (prefers-color-scheme: dark) {
                    .control-button.danger {
                        color: #ff6b6b;
                    }
                    
                    .control-button.danger:hover {
                        background-color: #ff6b6b;
                        color: #1a1a1a;
                    }
                }

                .system-controls {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    width: 100%;
                }

                .system-controls .control-button {
                    color: #666;
                }

                .system-controls .control-button:hover {
                    background-color: #f0f0f0;
                }

                /* Suporte para Dark Mode */
                @media (prefers-color-scheme: dark) {
                    .system-controls .control-button {
                        color: #adb5bd;
                    }
                    
                    .system-controls .control-button:hover {
                        background-color: #4d4d4d;
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
                           placeholder="Digite para buscar arquivos..."
                           autocomplete="off">
                    <ul id="searchResults"></ul>
                </div>

                <div class="warning">
                    <strong>Dica:</strong> Digite parte do nome do arquivo para buscar
                </div>

                <div id="nowPlaying" class="now-playing" style="display: none;">
                    Reproduzindo: <span id="currentVideo">Nenhum vídeo</span>
                </div>

                <div class="controls">
                    <h2 class="section-title">Mídia</h2>
                    <div class="controls-group">
                        <div class="volume-controls">
                            <button class="control-button" onclick="adjustVolume('down')" title="Diminuir Volume">
                                <i class="fas fa-volume-down"></i>
                            </button>
                            <button class="control-button" onclick="toggleMute()" title="Mudo/Desmudo" id="muteButton">
                                <i class="fas fa-volume-mute" id="muteIcon"></i>
                            </button>
                            <button class="control-button" onclick="adjustVolume('up')" title="Aumentar Volume">
                                <i class="fas fa-volume-up"></i>
                            </button>
                        </div>
                        
                        <div class="playback-controls">
                            <button class="control-button" onclick="togglePlayPause()" title="Play/Pause">
                                <i class="fas fa-play" id="playPauseIcon"></i>
                            </button>
                        </div>
                        
                        <div class="screen-controls">
                            <button class="control-button" onclick="toggleFullscreen()" title="Tela Cheia (F11)">
                                <i class="fas fa-expand-arrows-alt"></i>
                            </button>
                            <button class="control-button" onclick="hideControls()" title="Ocultar Controles (H)">
                                <i class="fas fa-eye-slash"></i>
                            </button>
                        </div>
                    </div>

                    <h2 class="section-title">Apresentação</h2>
                    <div class="controls-group">
                        <div class="presentation-controls">
                            <button class="control-button" onclick="previousSlide()" title="Slide Anterior (←)">
                                <i class="fas fa-step-backward"></i>
                            </button>
                            <button class="control-button" onclick="togglePresentationMode()" title="Modo Apresentação (F5)">
                                <i class="fas fa-tv"></i>
                            </button>
                            <button class="control-button" onclick="nextSlide()" title="Próximo Slide (→)">
                                <i class="fas fa-step-forward"></i>
                            </button>
                        </div>
                    </div>

                    <h2 class="section-title">Sistema</h2>
                    <div class="controls-group">
                        <div class="system-controls">
                            <button class="control-button" onclick="minimizeWindow()" title="Mostrar Área de Trabalho (Win+D)">
                                <i class="fas fa-desktop"></i>
                            </button>
                            <button class="control-button" onclick="maximizeWindow()" title="Maximizar Janela (Win+↑)">
                                <i class="fas fa-square"></i>
                            </button>
                            <button class="control-button" onclick="switchApp()" title="Alternar Aplicativos (Alt+Tab)">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                            <button class="control-button danger" onclick="closeApp()" title="Fechar Aplicativo (Alt+F4)">
                                <i class="fas fa-power-off"></i>
                            </button>
                        </div>
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
                            // Atualiza o ícone independente da resposta, já que a ação foi executada
                            isFullscreen = !isFullscreen;
                            fullscreenIcon.className = isFullscreen ? 'fas fa-compress-arrows-alt' : 'fas fa-expand-arrows-alt';
                        })
                        .catch(error => {
                            // Não mostra alerta, apenas loga o erro
                            console.error('Erro:', error);
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

                function nextSlide() {
                    fetch('/presentation/next')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao avançar slide');
                        });
                }

                function previousSlide() {
                    fetch('/presentation/previous')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao voltar slide');
                        });
                }

                function togglePresentationMode() {
                    fetch('/presentation/fullscreen')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao alternar modo apresentação');
                        });
                }

                function closeApp() {
                    if (confirm('Tem certeza que deseja fechar o aplicativo atual?')) {
                        fetch('/close-app')
                            .then(response => response.json())
                            .then(result => {
                                if (result.error) {
                                    alert(result.error);
                                }
                            })
                            .catch(error => {
                                console.error('Erro:', error);
                                alert('Erro ao fechar aplicativo');
                            });
                    }
                }

                function minimizeWindow() {
                    fetch('/system/minimize')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao minimizar janela');
                        });
                }

                function maximizeWindow() {
                    fetch('/system/maximize')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao maximizar janela');
                        });
                }

                function switchApp() {
                    fetch('/system/switch-app')
                        .then(response => response.json())
                        .then(result => {
                            if (result.error) {
                                alert(result.error);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            alert('Erro ao alternar entre aplicativos');
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
                                    data.videos.forEach(file => {
                                        const li = document.createElement('li');
                                        const icon = file.type === 'video' ? 'fas fa-film' : 
                                                    file.type === 'audio' ? 'fas fa-music' : 
                                                    'fas fa-file-powerpoint';
                                        const type = file.type === 'video' ? 'Vídeo' : 
                                                    file.type === 'audio' ? 'Áudio' : 
                                                    'Apresentação';
                                        li.innerHTML = `
                                            <i class="${icon} file-icon"></i>
                                            ${file.name}
                                            <span class="file-type">${type}</span>
                                        `;
                                        li.onclick = () => {
                                            fetch(`/search/${encodeURIComponent(file.name)}`)
                                                .then(response => response.json())
                                                .then(result => {
                                                    if (result.error) {
                                                        alert(result.error);
                                                    } else {
                                                        nowPlaying.style.display = 'block';
                                                        currentVideo.textContent = file.name;
                                                        isPlaying = true;
                                                        playPauseIcon.className = 'fas fa-pause';
                                                    }
                                                })
                                                .catch(error => {
                                                    console.error('Erro:', error);
                                                    alert('Erro ao abrir o arquivo');
                                                });
                                        };
                                        searchResults.appendChild(li);
                                    });
                                    searchResults.style.display = 'block';
                                } else {
                                    const li = document.createElement('li');
                                    li.textContent = 'Nenhum arquivo encontrado';
                                    searchResults.appendChild(li);
                                    searchResults.style.display = 'block';
                                }
                            })
                            .catch(error => {
                                console.error('Erro:', error);
                                searchResults.innerHTML = '<li>Erro ao buscar arquivos</li>';
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

                // Adiciona atalhos de teclado para apresentação
                document.addEventListener('keydown', function(e) {
                    if (document.activeElement === searchInput) return;

                    switch(e.code) {
                        case 'Space':
                            e.preventDefault();
                            togglePlayPause();
                            break;
                        case 'ArrowUp':
                            e.preventDefault();
                            adjustVolume('up');
                            break;
                        case 'ArrowDown':
                            e.preventDefault();
                            adjustVolume('down');
                            break;
                        case 'ArrowRight':
                            e.preventDefault();
                            nextSlide();
                            break;
                        case 'ArrowLeft':
                            e.preventDefault();
                            previousSlide();
                            break;
                        case 'KeyM':
                            e.preventDefault();
                            toggleMute();
                            break;
                        case 'KeyH':
                            e.preventDefault();
                            hideControls();
                            break;
                        case 'F11':
                            e.preventDefault();
                            toggleFullscreen();
                            break;
                        case 'F5':
                            e.preventDefault();
                            togglePresentationMode();
                            break;
                        case 'AltF4':
                            e.preventDefault();
                            closeApp();
                            break;
                        case 'ArrowUp':
                            e.preventDefault();
                            maximizeWindow();
                            break;
                        case 'ArrowDown':
                            e.preventDefault();
                            minimizeWindow();
                            break;
                        case 'AltTab':
                            e.preventDefault();
                            switchApp();
                            break;
                    }
                });
            </script>
        </body>
    </html>
    '''

@app.route('/api/search')
def api_search():
    """Endpoint para buscar arquivos e retornar lista de resultados"""
    search_term = request.args.get('term', '').lower()
    logger.info(f"Buscando arquivos com termo: {search_term}")
    
    files_folder = Path('files')
    if not files_folder.exists():
        logger.warning("Pasta 'files' não encontrada")
        os.makedirs('files', exist_ok=True)
        logger.info("Pasta 'files' criada")
        return jsonify({'videos': []})
    
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    presentation_extensions = ('.ppt', '.pptx', '.odp', '.key', '.pdf')
    audio_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.wma')
    files = []
    
    for file in files_folder.glob('**/*'):
        if search_term in file.name.lower():
            file_type = None
            if file.suffix.lower() in video_extensions:
                file_type = 'video'
            elif file.suffix.lower() in presentation_extensions:
                file_type = 'presentation'
            elif file.suffix.lower() in audio_extensions:
                file_type = 'audio'
                
            if file_type:
                files.append({
                    'name': file.name,
                    'path': str(file.absolute()),
                    'type': file_type
                })
    
    logger.info(f"Arquivos encontrados: {files}")
    return jsonify({'videos': files})

@app.before_request
def before_request():
    if request.scheme == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url)

@app.route('/search/<term>', methods=['GET'])
def search_get(term):
    """Endpoint GET para buscar arquivos diretamente pelo navegador"""
    logger.info(f"Recebida requisição GET para buscar: {term}")
    global video_process
    
    try:
        file_path, file_type = find_file(term)
        
        if not file_path:
            error_msg = f"Arquivo não encontrado para o termo: {term}"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'dica': 'Verifique se o arquivo está na pasta "files" e se o nome está correto'
            }), 404
        
        # Se já existe um processo em execução, fecha ele
        if video_process is not None:
            try:
                video_process.terminate()
                logger.info("Processo anterior terminado")
            except Exception as e:
                logger.error(f"Erro ao terminar processo anterior: {e}")
        
        try:
            if file_type == 'video':
                # Abre vídeo em tela cheia
                if os.name == 'nt':
                    video_process = subprocess.Popen(['start', '/max', '', file_path], shell=True)
                    time.sleep(1.5)
                    pyautogui.hotkey('alt', 'enter')
                else:
                    if os.system('which vlc > /dev/null') == 0:
                        video_process = subprocess.Popen(['vlc', '--fullscreen', file_path])
                    else:
                        opener = 'xdg-open' if os.name == 'posix' else 'open'
                        video_process = subprocess.Popen([opener, file_path])
                        time.sleep(1.5)
                        pyautogui.hotkey('alt', 'enter')
            elif file_type == 'audio':
                # Abre áudio com o player padrão
                if os.name == 'nt':
                    video_process = subprocess.Popen(['start', '', file_path], shell=True)
                else:
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    video_process = subprocess.Popen([opener, file_path])
            else:
                # Abre apresentação e coloca em modo apresentação após 3 segundos
                if os.name == 'nt':
                    video_process = subprocess.Popen(['start', '', file_path], shell=True)
                    time.sleep(3)
                    pyautogui.press('f5')
                else:
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    video_process = subprocess.Popen([opener, file_path])
                    time.sleep(3)
                    pyautogui.press('f5')
            
            logger.info(f"Arquivo iniciado com sucesso: {file_path}")
            return jsonify({
                'message': 'Arquivo iniciado com sucesso',
                'file_path': file_path,
                'file_type': file_type
            })
        except Exception as e:
            error_msg = f"Erro ao abrir o arquivo: {str(e)}"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'file_path': file_path
            }), 500
            
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/presentation/next', methods=['POST', 'GET'])
def next_slide():
    """Endpoint para avançar slide"""
    try:
        pyautogui.press('right')
        return jsonify({'message': 'Próximo slide'})
    except Exception as e:
        error_msg = f"Erro ao avançar slide: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/presentation/previous', methods=['POST', 'GET'])
def previous_slide():
    """Endpoint para voltar slide"""
    try:
        pyautogui.press('left')
        return jsonify({'message': 'Slide anterior'})
    except Exception as e:
        error_msg = f"Erro ao voltar slide: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/presentation/fullscreen', methods=['POST', 'GET'])
def toggle_presentation_fullscreen():
    """Endpoint para alternar modo apresentação"""
    try:
        pyautogui.press('f5')
        return jsonify({'message': 'Modo apresentação alternado'})
    except Exception as e:
        error_msg = f"Erro ao alternar modo apresentação: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

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
        logger.error(f"Erro ao alternar tela cheia: {str(e)}")
        return jsonify({'message': 'Tela cheia alternada com sucesso'})

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

@app.route('/close-app', methods=['POST', 'GET'])
def close_app():
    """Endpoint para fechar o aplicativo atual (Alt+F4)"""
    try:
        pyautogui.hotkey('alt', 'f4')
        return jsonify({'message': 'Comando enviado com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao fechar aplicativo: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/system/minimize', methods=['POST', 'GET'])
def minimize_window():
    """Endpoint para minimizar todas as janelas e mostrar a área de trabalho"""
    try:
        if os.name == 'nt':
            pyautogui.hotkey('win', 'd')  # Windows + D mostra a área de trabalho
        else:
            pyautogui.hotkey('win', 'd')  # Também funciona em muitas distribuições Linux
        return jsonify({'message': 'Área de trabalho mostrada com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao mostrar área de trabalho: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/system/maximize', methods=['POST', 'GET'])
def maximize_window():
    """Endpoint para maximizar a janela atual"""
    try:
        if os.name == 'nt':
            pyautogui.hotkey('win', 'up')  # Windows + Up maximiza no Windows
        else:
            pyautogui.hotkey('win', 'up')  # Pode variar dependendo do sistema
        return jsonify({'message': 'Janela maximizada com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao maximizar janela: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/system/switch-app', methods=['POST', 'GET'])
def switch_app():
    """Endpoint para alternar entre aplicativos (Alt+Tab)"""
    try:
        if os.name == 'nt':
            pyautogui.hotkey('alt', 'tab')
        else:
            pyautogui.hotkey('alt', 'tab')
        return jsonify({'message': 'Alternado entre aplicativos com sucesso'})
    except Exception as e:
        error_msg = f"Erro ao alternar entre aplicativos: {str(e)}"
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
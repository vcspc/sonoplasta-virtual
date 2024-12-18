import os
import logging
import pyautogui
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class MediaControlService:
    def __init__(self):
        self.video_process = None
        self.video_paused = False
    
    def play_media(self, file_path, file_type):
        """Reproduz um arquivo de mídia"""
        try:
            # Se já existe um processo em execução, fecha ele
            if self.video_process is not None:
                try:
                    self.video_process.terminate()
                    logger.info("Processo anterior terminado")
                except Exception as e:
                    logger.error(f"Erro ao terminar processo anterior: {e}")
            
            if file_type == 'image':
                # Abre imagem com o visualizador padrão
                if os.name == 'nt':
                    os.startfile(file_path)
                else:
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    self.video_process = subprocess.Popen([opener, file_path])
                return True, None
            
            elif file_type == 'video':
                # Abre vídeo em tela cheia
                if os.name == 'nt':
                    self.video_process = subprocess.Popen(['start', '/max', '', file_path], shell=True)
                    time.sleep(1.5)
                    pyautogui.hotkey('alt', 'enter')
                else:
                    if os.system('which vlc > /dev/null') == 0:
                        self.video_process = subprocess.Popen(['vlc', '--fullscreen', file_path])
                    else:
                        opener = 'xdg-open' if os.name == 'posix' else 'open'
                        self.video_process = subprocess.Popen([opener, file_path])
                        time.sleep(1.5)
                        pyautogui.hotkey('alt', 'enter')
                return True, None
            
            elif file_type == 'audio':
                # Abre áudio com o player padrão
                if os.name == 'nt':
                    self.video_process = subprocess.Popen(['start', '', file_path], shell=True)
                else:
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    self.video_process = subprocess.Popen([opener, file_path])
                return True, None
            
            else:  # presentation
                # Abre apresentação e coloca em modo apresentação após 3 segundos
                if os.name == 'nt':
                    self.video_process = subprocess.Popen(['start', '', file_path], shell=True)
                    time.sleep(3)
                    pyautogui.press('f5')
                else:
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    self.video_process = subprocess.Popen([opener, file_path])
                    time.sleep(3)
                    pyautogui.press('f5')
                return True, None
            
        except Exception as e:
            error_msg = f"Erro ao reproduzir mídia: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def toggle_play_pause(self):
        """Alterna entre play/pause"""
        try:
            pyautogui.press('space')
            self.video_paused = not self.video_paused
            return True, None
        except Exception as e:
            error_msg = f"Erro ao alternar play/pause: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def adjust_volume(self, action):
        """Ajusta o volume (up/down)"""
        try:
            if action == 'up':
                pyautogui.press('volumeup')
            else:
                pyautogui.press('volumedown')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao ajustar volume: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def toggle_mute(self):
        """Alterna entre mudo/desmudo"""
        try:
            pyautogui.press('volumemute')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao alternar mudo: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def toggle_fullscreen(self):
        """Alterna modo tela cheia"""
        try:
            pyautogui.press('f11')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao alternar tela cheia: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def hide_controls(self):
        """Oculta os controles de mídia"""
        try:
            x, y = pyautogui.size()
            pyautogui.click(x//2, y//2)
            return True, None
        except Exception as e:
            error_msg = f"Erro ao ocultar controles: {str(e)}"
            logger.error(error_msg)
            return False, error_msg 
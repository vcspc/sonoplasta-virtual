import logging
import pyautogui

logger = logging.getLogger(__name__)

class SystemControlService:
    @staticmethod
    def minimize_window():
        """Minimiza todas as janelas e mostra a área de trabalho"""
        try:
            pyautogui.hotkey('win', 'd')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao minimizar janela: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def maximize_window():
        """Maximiza a janela atual"""
        try:
            pyautogui.hotkey('win', 'up')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao maximizar janela: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def switch_app():
        """Alterna entre aplicativos"""
        try:
            pyautogui.hotkey('alt', 'tab')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao alternar entre aplicativos: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def close_app():
        """Fecha o aplicativo atual"""
        try:
            pyautogui.hotkey('alt', 'f4')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao fechar aplicativo: {str(e)}"
            logger.error(error_msg)
            return False, error_msg 
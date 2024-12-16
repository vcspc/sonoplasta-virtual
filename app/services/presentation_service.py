import logging
import pyautogui

logger = logging.getLogger(__name__)

class PresentationService:
    @staticmethod
    def next_slide():
        """Avança para o próximo slide"""
        try:
            pyautogui.press('right')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao avançar slide: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def previous_slide():
        """Volta para o slide anterior"""
        try:
            pyautogui.press('left')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao voltar slide: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def toggle_fullscreen():
        """Alterna modo apresentação"""
        try:
            pyautogui.press('f5')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao alternar modo apresentação: {str(e)}"
            logger.error(error_msg)
            return False, error_msg 
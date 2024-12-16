import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def search_videos(self, query, max_results=10):
        """Busca vídeos no YouTube"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video'
            ).execute()

            videos = [{
                'title': item['snippet']['title'],
                'id': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'channel': item['snippet']['channelTitle']
            } for item in search_response.get('items', [])]

            return videos, None
        except HttpError as e:
            error_msg = f"Erro ao buscar no YouTube: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def play_video(self, video_id):
        """Abre um vídeo do YouTube no navegador padrão"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            if os.name == 'nt':
                os.system(f'start {url}')
            else:
                os.system(f'xdg-open {url}')
            return True, None
        except Exception as e:
            error_msg = f"Erro ao abrir vídeo: {str(e)}"
            logger.error(error_msg)
            return False, error_msg 
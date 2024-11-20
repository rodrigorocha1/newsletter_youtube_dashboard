from typing import List, Optional, Tuple, Union
from src.interfaces.iservice_api import IServiceAPI
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build  # type: ignore
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    VideoUnavailable,
    TranscriptsDisabled,
)  # type: ignore
load_dotenv()


class YoutubeService(IServiceAPI):

    def __init__(self):
        self.__api_key = os.environ['YOUTUBE_API_KEY']
        self.__youtube = build('youtube', 'v3', developerKey=self.__api_key)

    def obter_id_canal(self, url_canal: str) -> Optional[Tuple[str, str]]:
        request = self.__youtube.search().list(
            part="snippet",
            q=url_canal,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]['id']['channelId'], response['items'][0]['snippet']['title']
        return None

    def obter_video_por_data(self, id_canal: str, data_inicio: datetime) -> List[Tuple[str, str]]:
        data_inicio_string: str = data_inicio.isoformat() + 'Z'

        request = self.__youtube.search().list(
            part="snippet",
            channelId=id_canal,
            order="date",
            publishedAfter=data_inicio_string
        )

        response = request.execute()

        video_ids = list(
            map(lambda x: (x['id']['videoId'],
                x['snippet']['title']), response['items'])
        )

        return video_ids

    def obter_transcricao_video(self, id_video: str) -> Union[str, bool]:

        try:
            transcricao = YouTubeTranscriptApi.get_transcript(
                video_id=id_video, languages=['pt']
            )
            transcricao = '\n'.join([item['text']
                                     for item in transcricao])
            return transcricao
        except NoTranscriptFound:
            return False
        except TranscriptsDisabled:
            return False
        except VideoUnavailable:
            return False
        except Exception as e:
            return False

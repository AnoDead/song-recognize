import requests
import json
import time 

from loguru import logger

from exceptions import *

TRACK=0
ARTIST=1
ALBUM=2
ALBUM_YEAR=3

GET_RESULT_WAIT_COUNT = 5 # количество повторов провереки результата get_result при статусе wait
WAIT_SEC_COUNT = 1 # количество секунд ожидани перед повтором запроса get_result


class SongInfo:

    def __init__(self, artist:str=None, track:str=None, album:str=None, album_year:int=None) -> None:
        self.artist = artist
        self.album = album
        self.track = track
        self.album_year = album_year

    def __repr__(self):
        return f"Song({self.artist}, {self.track}, {self.album}, {self.album_year})"

class SoundRecognizer:
    def __init__(self, apikey):
        self._api_url = 'https://audiotag.info/api'
        self._api_key = apikey
        self._rec_token = None
        self._found = None

    def recognize(self, filename:str) -> str:
        """Отправляет подготовленный аудио файл на распознавание"""
        
        payload =  {'action':'identify', 'apikey':self._api_key}

        try:
            with open(filename, 'rb') as fh:
                response = requests.post(self._api_url, data=payload, files={'file':fh})
            response = json.loads(response.text)
        except IOError as err:
            logger.debug(err)
            return None
        except requests.RequestException as err:
            logger.debug(err)
            return None
        

        if response['error'] or not response['success']:
            logger.error(response['error'])
            return None
        else:
            self._rec_token = response['token']
            logger.info(self._rec_token)
            return self._rec_token

    def _parse_response_data_block(self, data=dict) -> SongInfo:
        """Парсит блок data в ответе сервиса распознования песни"""

        song = SongInfo()

        for i in data: #перебераем список совпадений перезаписываем пустые поля 
            item = i['tracks'][0]
            song.artist = song.artist or item[ARTIST]
            song.track = song.track or item[TRACK]
            song.album = item[ALBUM] if (item[ALBUM] != "[no album information]") else song.album
            song.album_year = song.album_year or item[ALBUM_YEAR]

        return song
            


    def _parse_get_result_response(self, response:requests.Response, repeat:int) -> SongInfo:
        """"Парсит ответ get_result сервиса распознования песни"""

        response = response.json()
        if response['success'] == True:

            result = response['result']

            if result == 'found':
                song = self._parse_response_data_block(response['data'])
                self._found = True
                logger.debug('Song found: ', song)
                return song

            elif result == 'not found':
                self._found = False
                logger.debug('Song not found: ')
                raise GetResultNotFoundException('song not found')

            elif result == 'wait':
                time.sleep(WAIT_SEC_COUNT)
                self._get_result_by_token(self._rec_token, repeat+1)
        else:
            error = response['error']
            raise GetResultNotSuccess(error)


    def _get_result_by_token(self, token:str, repeat:int=0) -> SongInfo:
        """делает пост запрос на get_result"""

        if repeat > GET_RESULT_WAIT_COUNT:
            raise GetResultAlongWait('Превышено время ожидания результата')

        payload = {'action': 'get_result', 'token':token, 'apikey':self._api_key}
        try:
            response = requests.post(self._api_url, data=payload)
        except requests.RequestException as err:
            logger.error(err)
            # return {'error': err}
            raise GetResultException(err)

        return self._parse_get_result_response(response, repeat)



    def get_result(self, token:str=None) -> SongInfo:
        return self._get_result_by_token(token or self._rec_token)
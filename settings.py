import os

API_KEY_TOKEN = '1073949dc8b6113c8b74e3b5ace1806c'

TEMP_DIR = '.\\trans_samples\\'
FULL_PATH = os.getcwd()
FFMPEG_EX = FULL_PATH + "\\ffmpeg-4.4-full_build\\bin\\ffmpeg.exe"
FILES_INFO = FULL_PATH + "\\files_info.json"
command = '{ffmpeg} -i {source} -ar 8000 -ac 1 -vn -to 00:00:15 {destenation}'

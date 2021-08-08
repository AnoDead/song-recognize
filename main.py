import subprocess
import os
import sys
import argparse
import json
from loguru import logger
from mutagen.easyid3 import EasyID3
import re

from SoundRecognizer import SoundRecognizer


token_list = {}

def preparation_files(path:str):
    """подготавливает файлы для обработки сервисом"""
    for file in [f for f in os.listdir(path) if f.endswith('.mp3')]:
        task = command.format(ffmpeg=FFMPEG_EX, source=path+file, destenation=TEMP_DIR+file[:-3] + 'wav')
        logger.info('Будет выполнена команда: '+ task)
        subprocess.call([FFMPEG_EX, '-i', path+file, '-ar', '8000', '-ac', '1', '-vn', '-to', '00:00:15', TEMP_DIR+file[:-3]+'wav'])

def recognize():
    info = {}
    recognizer = SoundRecognizer(API_KEY_TOKEN)
    for file in os.listdir(TEMP_DIR): 
        token = recognizer.recognize(TEMP_DIR + file)
        if token:
            token_list[token] = file
        else:
            logger.error(file +'| recognize error')

    for token, file in token_list.items():
        info[file] = recognizer.get_result(token) 

    with open(FILES_INFO, 'w') as fh:
        json.dump(info, fh)
    return True

def set_tags(path:str, filename:str, info:dict[str, str]):
    tags = EasyID3(path + filename)
    tags['artist'] = info['author']
    tags['title'] = info['track']
    tags['album'] = info['album']
    tags.save(v2_version=3)

def rename_file(path:str):
    fh = open(FILES_INFO, 'r')
    data = json.load(fh)
    fh.close()
    outsiders = {}
    rename_history = {}
    for filename, info in data.items():
        filename = filename[:-3] + 'mp3'
        if info.get('author'):
            new_filename = info['author'] + ' - ' + info['track'] + '.mp3'
            new_filename=re.sub('[!@#$%^&*?><]', '', new_filename)
            print("файл ({name}) будет переименован в ({newname})".format(name=filename, newname = new_filename))
            rename_history[filename] = new_filename
            set_tags(path, filename, info)
            os.rename(path+filename, path+new_filename)
        else:
            outsiders[filename] = info
    
    with open('outsiders.json', 'w') as fh:
        json.dump(outsiders, fh)
    with open('rename_history.json', 'w') as fh:
        json.dump(rename_history, fh)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=None)
    arg = parser.parse_args(sys.argv[1:])
    if arg.path:
        preparation_files(arg.path)
        recognize()
    else:
        print('Укажите деректорию')
        return

if __name__ == "__main__":
    main()

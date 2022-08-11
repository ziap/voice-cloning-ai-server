from fastapi import APIRouter, Response, File, UploadFile, BackgroundTasks
from shutil import rmtree
from pathlib import Path
 
import numpy as np
import os
import aiofiles

from loadmodel import preprocess_wav, embed_utterance

root_data_path = os.path.join(os.getcwd(), 'data/users')
if not os.path.isdir(root_data_path):
    os.makedirs(root_data_path)

queue_path = os.path.join(os.getcwd(), 'data/queue')
if not os.path.isdir(queue_path):
    os.makedirs(queue_path)

def UserPath(userid):
    return os.path.join(root_data_path, userid)

def encode_voice(userid):
    # Get files
    in_file = os.path.join(queue_path, '%s.wav' % userid)
    user_path = UserPath(userid)
    out_file = os.path.join(user_path, 'voice')
    
    # Generate embedding vector
    voice = preprocess_wav(Path(in_file))
    os.remove(in_file)
    data = embed_utterance(voice)

    # Save output
    np.save(out_file, data)

router = APIRouter(
    prefix='/user',
    tags=['User'],
    responses={404: {'description': 'Not found'}},
)

@router.get('-{userid}', status_code=404)
async def GetUser(userid, response: Response):
    if os.path.isdir(UserPath(userid)):
        response.status_code = 200
        return {'id': userid}

@router.put('-{userid}', status_code=201)
async def PutUser(userid, tasks: BackgroundTasks, voice: UploadFile = File(...)):
    voice_queue_file = os.path.join(queue_path, '%s.wav' % userid) 
    user_path = UserPath(userid)
    if not os.path.isdir(user_path):
        os.makedirs(user_path)
    async with aiofiles.open(voice_queue_file, 'wb') as out_file:
        content = await voice.read(1024)
        while content:
            await out_file.write(content)
            content = await voice.read(1024)
    tasks.add_task(encode_voice, userid)
    return {'id': userid, 'file': voice_queue_file}

@router.delete('-{userid}', status_code=409)
async def DeleteUser(userid, response: Response):
    user_path = UserPath(userid)
    if os.path.isdir(UserPath(user_path)):
        response.status_code=200
        rmtree(user_path)
        return {'deleted': True}
    return {'deleted': False}

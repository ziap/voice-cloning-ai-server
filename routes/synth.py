from fastapi import APIRouter, Response, BackgroundTasks
from fastapi.responses import FileResponse
from loadmodel import sample_rate, preprocess_wav, synthesize_spectrograms, infer_waveform

from .user import UserPath
from .story import StoryGlob

import os
import numpy as np
import soundfile as sf

router = APIRouter(
    prefix='',
    tags=['Synthesize'],
    responses={404: {'description': 'Not found'}},
)

def VoiceFile(userid, storyid):
    return os.path.join(UserPath(userid), '%s.wav' % storyid)

def SynthesizeVoice(userid, storyid):
    user_path = UserPath(userid)
    story_file = StoryGlob(storyid)[0]
    user_voice = os.path.join(user_path, 'voice.npy')
    voice = np.load(user_voice)
    with open(story_file) as f:
        text = f.read()
        spec = synthesize_spectrograms([text], [voice])[0]
        wav = infer_waveform(spec) 
        wav = np.pad(wav, (0, sample_rate), mode='constant')
        wav = preprocess_wav(wav)
        file = VoiceFile(userid, storyid)
        if len(StoryGlob(storyid)) > 0:
            sf.write(file, wav.astype(np.float32), sample_rate)


@router.get('/user-{userid}/story-{storyid}', status_code=404)
async def GetVoice(userid, storyid, response: Response, task: BackgroundTasks):
    user_path = UserPath(userid)
    if os.path.isdir(user_path):
        voice_file = VoiceFile(userid, storyid)
        if os.path.isfile(voice_file):
            response.status_code = 200
            return FileResponse(voice_file)
        response.status_code = 404
        story_glob = StoryGlob(storyid)
        if len(story_glob) == 0:
            return 
        file = story_glob[0]
        if file[file.rindex('/') + 1:file.rindex('-')] != storyid:
            return
        response.status_code = 202
        task.add_task(SynthesizeVoice, userid, storyid)
        return {'status': 'processing'}
         

@router.delete('/user-{userid}/story-{storyid}', status_code=409)
async def DeleteVoice(userid, storyid, response: Response):
    voice_file = VoiceFile(userid, storyid)
    if os.path.isdir(UserPath(userid)) and os.path.isfile(voice_file):
        response.status_code = 200
        os.remove(voice_file)
        return {'deleted': True}
    return {'deleted': False}

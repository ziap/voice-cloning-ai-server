from fastapi import APIRouter, Response, BackgroundTasks
from fastapi.responses import FileResponse
from loadmodel import hop_size, sample_rate, preprocess_wav, synthesize_spectrograms, infer_waveform

from .user import UserPath
from .story import StoryGlob, root_data_path

import aiofiles
import os
import numpy as np
import soundfile as sf

processing = set()

router = APIRouter(
    prefix='',
    tags=['Synthesize'],
    responses={404: {'description': 'Not found'}},
)

def VoiceFile(userid, storyid):
    return os.path.join(UserPath(userid), '%s.wav' % storyid)

def SynthesizeVoice(userid, storyid):
    processing.add((userid, storyid))
    user_path = UserPath(userid)
    story_file = StoryGlob(storyid)[0]
    user_voice = os.path.join(user_path, 'voice.npy')
    voice = np.load(user_voice)
    with open(story_file) as f:
        texts = f.read().split('\n')
        voices = [voice] * len(texts)
        specs = synthesize_spectrograms(texts, voices)
        breaks = [spec.shape[1] for spec in specs]
        spec = np.concatenate(specs, axis=1)
        wav = infer_waveform(spec) 
        b_ends = np.cumsum(np.array(breaks) * hop_size)
        b_starts = np.concatenate(([0], b_ends[:-1]))
        wavs = [wav[start:end] for start, end in zip(b_starts, b_ends)]
        breaks = [np.zeros(int(0.15 * sample_rate))] * len(breaks)
        wav = np.concatenate([i for w, b in zip(wavs, breaks) for i in (w, b)])
        wav = preprocess_wav(wav)
        file = VoiceFile(userid, storyid)
        if len(StoryGlob(storyid)) > 0:
            sf.write(file, wav.astype(np.float32), sample_rate)
    processing.remove((userid, storyid))

@router.get('/user-{userid}/stories', status_code=404)
async def GetVoices(userid, response: Response):
    user_path = UserPath(userid)
    if os.path.isdir(user_path):
        response.status_code = 200
        stories = dict()
        for file in os.listdir(root_data_path):
            id = file[:file.rindex('-')]
            title = file[file.rindex('-') + 1:file.rindex('.')] 
            async with aiofiles.open(os.path.join(root_data_path, file), mode='r') as f:
                content = await f.read()
            voice_file = VoiceFile(userid, id)
            status = 'not synthesized'
            if os.path.isfile(voice_file):
                status = 'synthesized'
            elif (userid, id) in processing:
                status = 'synthesizing'
            stories[id] = {'title': title, 'content': content, 'status': status}
        return stories

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
        if (userid, storyid) in processing:
            return {'status': 'processing'}
        task.add_task(SynthesizeVoice, userid, storyid)
        return {'status': 'started processing'}
         

@router.delete('/user-{userid}/story-{storyid}', status_code=409)
async def DeleteVoice(userid, storyid, response: Response):
    voice_file = VoiceFile(userid, storyid)
    if os.path.isdir(UserPath(userid)) and os.path.isfile(voice_file):
        response.status_code = 200
        os.remove(voice_file)
        return {'deleted': True}
    return {'deleted': False}

from fastapi import APIRouter, Response
from pydantic import BaseModel
from glob import glob

import os
import aiofiles

class Story(BaseModel):
    title: str
    content: str

root_data_path = os.path.join(os.getcwd(), 'data/stories')
if not os.path.isdir(root_data_path):
    os.makedirs(root_data_path)

router = APIRouter(
    prefix='/story',
    tags=['Story'],
    responses={404: {"description": "Not found"}},
)

def delete_story(storyid):
    deleted = False
    story_glob = StoryGlob(storyid)
    if len(story_glob) > 0:
        deleted = True
        for file in story_glob:
            if file[file.rindex('/') + 1:file.rindex('-')] == storyid:
                os.remove(file)
    return deleted

def StoryGlob(storyid):
    return glob(os.path.join(root_data_path, "%s-*.txt" % storyid))

@router.get("-{storyid}", status_code=404)
async def GetStory(storyid, response: Response):
    story_glob = StoryGlob(storyid)
    if len(story_glob) > 0:
        file = story_glob[0]
        if file[file.rindex('/') + 1:file.rindex('-')] != storyid:
            return
        response.status_code = 200
        title = file[file.rindex('-') + 1:file.rindex('.')]
        async with aiofiles.open(file, mode='r') as f:
            content = await f.read()
        return {'id': storyid, 'title': title, 'content': content} 

@router.put("-{storyid}", status_code=201)
async def PutStory(storyid, story: Story):
    delete_story(storyid)
    file = os.path.join(root_data_path, "%s-%s.txt" % (storyid, story.title))
    async with aiofiles.open(file, mode='w') as f:
       await f.write(story.content) 
    return {'id': storyid}

@router.delete("-{storyid}", status_code=409)
async def DeleteStory(storyid, response: Response):
    deleted = delete_story(storyid)
    if deleted:
        response.status_code = 200
    return {'id': storyid, 'deleted': deleted}

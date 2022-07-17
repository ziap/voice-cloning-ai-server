from fastapi import APIRouter
from .story import root_data_path

import os

router = APIRouter(
    prefix='/stories',
    tags=['Stories'],
    responses={404: {"description": "Not found"}},
)

@router.get('/')
async def GetStories():
    stories = []
    for file in os.listdir(root_data_path):
        id = file[:file.rindex('-')]
        title = file[file.rindex('-') + 1:file.rindex('.')]
        stories.append({'id': id, 'title': title})
    return stories

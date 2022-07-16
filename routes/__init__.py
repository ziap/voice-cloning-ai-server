from fastapi import APIRouter
from . import user, story, liststory

router = APIRouter()
router.include_router(user.router)
router.include_router(story.router)
router.include_router(liststory.router)

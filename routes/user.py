from fastapi import APIRouter

router = APIRouter(
    prefix='/user',
    tags=['User'],
    responses={404: {"description": "Not found"}},
)

@router.get('-{userid}')
def getuser(userid):
    return {'id': userid}

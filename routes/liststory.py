from fastapi import APIRouter

router = APIRouter(
    prefix='/Stories',
    tags=['Stories'],
    responses={404: {"description": "Not found"}},
)


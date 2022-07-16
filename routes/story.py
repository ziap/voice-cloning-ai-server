from fastapi import APIRouter

router = APIRouter(
    prefix='/story',
    tags=['Story'],
    responses={404: {"description": "Not found"}},
)

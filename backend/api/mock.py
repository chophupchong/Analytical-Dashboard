from fastapi import APIRouter

router = APIRouter(
    prefix='/mock',
    tags=['mock'],
    responses={
        404:{'description':'Not Found'}
    }
)

@router.get('/')

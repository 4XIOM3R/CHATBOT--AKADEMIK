from fastapi import APIRouter, Depends
from api.deps import get_current_user

from services.academic_service import (
    get_khs_by_user,
    get_ipk,
    get_ips_per_semester,
)

router = APIRouter()


@router.get("/khs")
def khs(user=Depends(get_current_user)):
    return get_khs_by_user(str(user.id))


@router.get("/ipk")
def ipk(user=Depends(get_current_user)):
    return {"ipk": get_ipk(str(user.id))}


@router.get("/ips")
def ips(user=Depends(get_current_user)):
    return get_ips_per_semester(str(user.id))
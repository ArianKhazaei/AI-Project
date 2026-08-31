from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database import get_connection


router = APIRouter()


class AdminLoginRequest(BaseModel):
    username: str
    password: str


@router.post("/admin/login")
def admin_login(req: AdminLoginRequest):
    username = req.username.strip()
    password = req.password

    if not username:
        raise HTTPException(
            status_code=400,
            detail="نام کاربری مدیر وارد نشده است.",
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail="رمز عبور مدیر وارد نشده است.",
        )

    conn = get_connection()

    try:
        admin = conn.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                name
            FROM admins
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if not admin:
            raise HTTPException(
                status_code=401,
                detail="نام کاربری یا رمز عبور مدیر اشتباه است.",
            )

        if admin["password_hash"] != password:
            raise HTTPException(
                status_code=401,
                detail="نام کاربری یا رمز عبور مدیر اشتباه است.",
            )

        return {
            "status": "success",
            "role": "admin",
            "id": admin["id"],
            "username": admin["username"],
            "name": admin["name"],
        }

    finally:
        conn.close()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database import get_connection


router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    username = req.username.strip()
    password = req.password

    if not username:
        raise HTTPException(
            status_code=400,
            detail="نام کاربری وارد نشده است.",
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail="رمز عبور وارد نشده است.",
        )

    conn = get_connection()

    try:
        # --------------------------------------------------------
        # Teacher
        # --------------------------------------------------------

        teacher = conn.execute(
            """
            SELECT
                id,
                name,
                username,
                password,
                password_hash,
                is_approved
            FROM teachers
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if teacher:
            stored_password = (
                teacher["password_hash"]
                or teacher["password"]
                or ""
            )

            if stored_password != password:
                raise HTTPException(
                    status_code=401,
                    detail="نام کاربری یا رمز عبور اشتباه است.",
                )

            if not teacher["is_approved"]:
                raise HTTPException(
                    status_code=403,
                    detail="حساب استاد هنوز توسط مدیر تأیید نشده است.",
                )

            return {
                "status": "success",
                "role": "teacher",
                "id": teacher["id"],
                "name": teacher["name"],
                "username": teacher["username"],
            }

        # --------------------------------------------------------
        # Student
        # --------------------------------------------------------

        student = conn.execute(
            """
            SELECT
                id,
                name,
                username,
                password_hash,
                is_approved
            FROM students
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if student:
            stored_password = (
                student["password_hash"]
                or ""
            )

            if stored_password != password:
                raise HTTPException(
                    status_code=401,
                    detail="نام کاربری یا رمز عبور اشتباه است.",
                )

            if not student["is_approved"]:
                raise HTTPException(
                    status_code=403,
                    detail="حساب هنرجو هنوز توسط مدیر تأیید نشده است.",
                )

            return {
                "status": "success",
                "role": "student",
                "id": student["id"],
                "name": student["name"],
                "username": student["username"],
            }

        raise HTTPException(
            status_code=401,
            detail="نام کاربری یا رمز عبور اشتباه است.",
        )

    finally:
        conn.close()

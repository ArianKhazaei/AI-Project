from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database import get_connection


router = APIRouter()


class StudentRegisterRequest(BaseModel):
    name: str
    national_code: str
    level: Optional[str] = "مقدماتی"


class TeacherRegisterRequest(BaseModel):
    name: str
    national_code: str


def validate_national_code(national_code: str) -> str:
    national_code = national_code.strip()

    if not national_code.isdigit() or len(national_code) != 10:
        raise HTTPException(
            status_code=400,
            detail="کد ملی باید دقیقاً ۱۰ رقم و فقط شامل اعداد باشد.",
        )

    return national_code


@router.post("/register/student")
def register_student(req: StudentRegisterRequest):
    name = req.name.strip()
    national_code = validate_national_code(req.national_code)

    if not name:
        raise HTTPException(
            status_code=400,
            detail="نام هنرجو وارد نشده است.",
        )

    conn = get_connection()

    try:
        existing_student = conn.execute(
            """
            SELECT id
            FROM students
            WHERE username = ?
            """,
            (national_code,),
        ).fetchone()

        if existing_student:
            raise HTTPException(
                status_code=400,
                detail="این کد ملی قبلاً برای یک هنرجو ثبت شده است.",
            )

        existing_request = conn.execute(
            """
            SELECT id
            FROM registration_requests
            WHERE requested_username = ?
            AND status = 'pending'
            """,
            (national_code,),
        ).fetchone()

        if existing_request:
            raise HTTPException(
                status_code=400,
                detail="برای این کد ملی یک درخواست ثبت‌نام در انتظار تأیید وجود دارد.",
            )

        cursor = conn.execute(
            """
            INSERT INTO registration_requests (
                user_type,
                name,
                requested_username,
                level,
                status
            )
            VALUES (
                'student',
                ?,
                ?,
                ?,
                'pending'
            )
            """,
            (
                name,
                national_code,
                req.level or "مقدماتی",
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "درخواست ثبت‌نام هنرجو برای مدیر ارسال شد.",
            "request_id": cursor.lastrowid,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"ثبت درخواست هنرجو انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


@router.post("/register/teacher")
def register_teacher(req: TeacherRegisterRequest):
    name = req.name.strip()
    national_code = validate_national_code(req.national_code)

    if not name:
        raise HTTPException(
            status_code=400,
            detail="نام استاد وارد نشده است.",
        )

    conn = get_connection()

    try:
        existing_teacher = conn.execute(
            """
            SELECT id
            FROM teachers
            WHERE username = ?
            """,
            (national_code,),
        ).fetchone()

        if existing_teacher:
            raise HTTPException(
                status_code=400,
                detail="این کد ملی قبلاً برای یک استاد ثبت شده است.",
            )

        existing_request = conn.execute(
            """
            SELECT id
            FROM registration_requests
            WHERE requested_username = ?
            AND status = 'pending'
            """,
            (national_code,),
        ).fetchone()

        if existing_request:
            raise HTTPException(
                status_code=400,
                detail="برای این کد ملی یک درخواست ثبت‌نام در انتظار تأیید وجود دارد.",
            )

        cursor = conn.execute(
            """
            INSERT INTO registration_requests (
                user_type,
                name,
                requested_username,                status
            )
            VALUES (
                'teacher',
                ?,
                ?,
                'pending'
            )
            """,
                        (
                name,
                national_code,
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "درخواست ثبت‌نام استاد برای مدیر ارسال شد.",
            "request_id": cursor.lastrowid,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"ثبت درخواست استاد انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


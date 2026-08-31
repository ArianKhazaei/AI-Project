from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database import get_connection


router = APIRouter()


class AdminProcessRegistrationRequest(BaseModel):
    request_id: int
    approve: bool


@router.get("/admin/registration-requests")
def get_registration_requests():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                user_type,
                name,
                requested_username,
                level,
                teacher_prompt,
                status,
                requested_username AS assigned_username,
                CASE
                    WHEN status = 'approved' THEN '1234'
                    ELSE NULL
                END AS default_password,
                created_at,
                processed_at
            FROM registration_requests
            ORDER BY
                CASE
                    WHEN status = 'pending' THEN 0
                    ELSE 1
                END,
                id DESC
            """
        ).fetchall()

        return {
            "status": "success",
            "requests": [
                dict(row)
                for row in rows
            ],
        }

    finally:
        conn.close()


@router.post("/admin/registration-requests/process")
def process_registration_request(
    req: AdminProcessRegistrationRequest,
):
    conn = get_connection()

    try:
        request = conn.execute(
            """
            SELECT *
            FROM registration_requests
            WHERE id = ?
            """,
            (req.request_id,),
        ).fetchone()

        if not request:
            raise HTTPException(
                status_code=404,
                detail="درخواست ثبت‌نام پیدا نشد.",
            )

        if request["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail="این درخواست قبلاً بررسی شده است.",
            )

        if not req.approve:
            conn.execute(
                """
                DELETE FROM registration_requests
                WHERE id = ?
                """,
                (req.request_id,),
            )

            conn.commit()

            return {
                "status": "success",
                "message": "درخواست ثبت‌نام رد و حذف شد.",
                "request_id": req.request_id,
                "approved": False,
            }

        user_type = request["user_type"]
        national_code = (request["requested_username"] or "").strip()

        if user_type not in ("student", "teacher"):
            raise HTTPException(
                status_code=400,
                detail="نوع کاربر در درخواست نامعتبر است.",
            )

        if not national_code.isdigit() or len(national_code) != 10:
            raise HTTPException(
                status_code=400,
                detail="کد ملی این درخواست معتبر نیست.",
            )

        default_password = "1234"

        if user_type == "teacher":
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

            cursor = conn.execute(
                """
                INSERT INTO teachers (
                    name,
                    username,
                    password,
                    password_hash,
                    prompt,
                    teacher_prompt,
                    is_approved
                )
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    request["name"],
                    national_code,
                    default_password,
                    default_password,
                    request["teacher_prompt"] or "",
                    request["teacher_prompt"] or "",
                ),
            )

        else:
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

            cursor = conn.execute(
                """
                INSERT INTO students (
                    name,
                    username,
                    password_hash,
                    level,
                    is_approved
                )
                VALUES (?, ?, ?, ?, 1)
                """,
                (
                    request["name"],
                    national_code,
                    default_password,
                    request["level"] or "مقدماتی",
                ),
            )

        user_id = cursor.lastrowid

        if user_type == "teacher":
            students = conn.execute(
                """
                SELECT id
                FROM students
                """
            ).fetchall()

            for student in students:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO student_teachers (
                        student_id,
                        teacher_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        student["id"],
                        user_id,
                    ),
                )

        else:
            teachers = conn.execute(
                """
                SELECT id
                FROM teachers
                """
            ).fetchall()

            for teacher in teachers:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO student_teachers (
                        student_id,
                        teacher_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        user_id,
                        teacher["id"],
                    ),
                )

        conn.execute(
            """
            DELETE FROM registration_requests
            WHERE id = ?
            """,
            (req.request_id,),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "درخواست ثبت‌نام تأیید و حذف شد.",
            "request_id": req.request_id,
            "approved": True,
            "user_type": user_type,
            "user_id": user_id,
            "username": national_code,
            "password": default_password,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"پردازش درخواست ثبت‌نام انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


from fastapi import APIRouter, HTTPException

from backend.database import get_connection


router = APIRouter()


# ============================================================
# Admin Users
# ============================================================

@router.get("/admin/users")
def get_admin_users():
    conn = get_connection()

    try:
        students = conn.execute(
            """
            SELECT
                id,
                name,
                username,
                level,
                is_approved,
                created_at
            FROM students
            ORDER BY id DESC
            """
        ).fetchall()

        teachers = conn.execute(
            """
            SELECT
                id,
                name,
                username,
                is_approved,
                created_at
            FROM teachers
            ORDER BY id DESC
            """
        ).fetchall()

        return {
            "status": "success",
            "students": [
                dict(row)
                for row in students
            ],
            "teachers": [
                dict(row)
                for row in teachers
            ],
        }

    finally:
        conn.close()


# ============================================================
# Delete Student
# ============================================================

@router.delete("/admin/users/student/{student_id}")
def delete_student(student_id: int):
    conn = get_connection()

    try:
        student = conn.execute(
            """
            SELECT
                id,
                name,
                username
            FROM students
            WHERE id = ?
            """,
            (student_id,),
        ).fetchone()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="هنرجو پیدا نشد.",
            )

        conn.execute(
            """
            DELETE FROM students
            WHERE id = ?
            """,
            (student_id,),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "هنرجو با موفقیت حذف شد.",
            "user_type": "student",
            "user_id": student_id,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"حذف هنرجو انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


# ============================================================
# Delete Teacher
# ============================================================

@router.delete("/admin/users/teacher/{teacher_id}")
def delete_teacher(teacher_id: int):
    conn = get_connection()

    try:
        teacher = conn.execute(
            """
            SELECT
                id,
                name,
                username
            FROM teachers
            WHERE id = ?
            """,
            (teacher_id,),
        ).fetchone()

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="استاد پیدا نشد.",
            )

        conn.execute(
            """
            DELETE FROM teachers
            WHERE id = ?
            """,
            (teacher_id,),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "استاد با موفقیت حذف شد.",
            "user_type": "teacher",
            "user_id": teacher_id,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"حذف استاد انجام نشد: {str(e)}",
        )

    finally:
        conn.close()

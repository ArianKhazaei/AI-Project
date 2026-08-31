from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database import get_connection


router = APIRouter()


class TeacherPromptRequest(BaseModel):
    prompt: str


@router.get("/teacher/prompt/{teacher_id}")
def get_teacher_prompt(teacher_id: int):
    conn = get_connection()

    try:
        teacher = conn.execute(
            """
            SELECT
                id,
                prompt,
                teacher_prompt
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

        prompt = (
            teacher["teacher_prompt"]
            or teacher["prompt"]
            or ""
        )

        return {
            "status": "success",
            "prompt": prompt,
        }

    finally:
        conn.close()


@router.put("/teacher/prompt/{teacher_id}")
def update_teacher_prompt(
    teacher_id: int,
    req: TeacherPromptRequest,
):
    prompt = req.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt نمی‌تواند خالی باشد.",
        )

    conn = get_connection()

    try:
        teacher = conn.execute(
            """
            SELECT id
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
            UPDATE teachers
            SET
                prompt = ?,
                teacher_prompt = ?
            WHERE id = ?
            """,
            (
                prompt,
                prompt,
                teacher_id,
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Prompt استاد با موفقیت ذخیره شد.",
            "prompt": prompt,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"ذخیره Prompt استاد انجام نشد: {str(e)}",
        )

    finally:
        conn.close()

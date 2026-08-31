from pathlib import Path
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from backend.database import get_connection


router = APIRouter()


NOTES_DIR = Path(__file__).resolve().parents[3] / "notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)


class LessonCreateRequest(BaseModel):
    name: str
    content: str = ""
    note_file: Optional[str] = None


class LessonUpdateRequest(BaseModel):
    name: str
    content: str = ""
    note_file: Optional[str] = None


class AssignLessonRequest(BaseModel):
    teacher_id: int
    lesson_id: int


def get_teacher(teacher_id: int, conn):
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

    return teacher


def get_teacher_lesson(teacher_id: int, lesson_id: int, conn):
    lesson = conn.execute(
        """
        SELECT
            l.id,
            l.code,
            l.name,
            l.lesson_prompt,
            l.content,
            l.pdf_file,
            l.created_at
        FROM lessons l
        INNER JOIN teacher_lessons tl
            ON tl.lesson_id = l.id
        WHERE tl.teacher_id = ?
        AND l.id = ?
        """,
        (teacher_id, lesson_id),
    ).fetchone()

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="درس موردنظر برای این استاد پیدا نشد.",
        )

    return lesson


def serialize_lesson(row):
    item = dict(row)

    pdf_file = item.get("pdf_file")

    item["note_url"] = (
        f"/notes/{pdf_file}"
        if pdf_file
        else None
    )

    return item


@router.post("/teacher/notes/upload/{teacher_id}")
async def upload_teacher_note(
    teacher_id: int,
    note: UploadFile = File(...),
):
    conn = get_connection()

    try:
        get_teacher(teacher_id, conn)

        filename = note.filename or ""

        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="فقط فایل PDF مجاز است.",
            )

        file_id = uuid.uuid4().hex
        saved_filename = f"teacher_{teacher_id}_{file_id}.pdf"
        file_path = NOTES_DIR / saved_filename

        content = await note.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="فایل PDF خالی است.",
            )

        file_path.write_bytes(content)

        return {
            "status": "success",
            "message": "PDF با موفقیت آپلود شد.",
            "note_file": saved_filename,
        }

    finally:
        conn.close()


@router.post("/teacher/lessons/{teacher_id}")
def create_teacher_lesson(
    teacher_id: int,
    req: LessonCreateRequest,
):
    name = req.name.strip()
    content = req.content.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="نام درس نمی‌تواند خالی باشد.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="محتوای درس نمی‌تواند خالی باشد.",
        )

    conn = get_connection()

    try:
        get_teacher(teacher_id, conn)

        code = f"T{teacher_id}-{uuid.uuid4().hex[:8].upper()}"

        cursor = conn.execute(
            """
            INSERT INTO lessons (
                code,
                name,
                lesson_prompt,
                content,
                pdf_file
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                code,
                name,
                "",
                content,
                req.note_file,
            ),
        )

        lesson_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO teacher_lessons (
                teacher_id,
                lesson_id
            )
            VALUES (?, ?)
            """,
            (
                teacher_id,
                lesson_id,
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "درس با موفقیت ساخته شد.",
            "id": lesson_id,
            "teacher_id": teacher_id,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"ساخت درس انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


@router.get("/teacher/lessons/{teacher_id}")
def get_teacher_lessons(teacher_id: int):
    conn = get_connection()

    try:
        get_teacher(teacher_id, conn)

        rows = conn.execute(
            """
            SELECT
                l.id,
                l.code,
                l.name,
                l.lesson_prompt,
                l.content,
                l.pdf_file,
                l.created_at
            FROM lessons l
            INNER JOIN teacher_lessons tl
                ON tl.lesson_id = l.id
            WHERE tl.teacher_id = ?
            ORDER BY l.id DESC
            """,
            (teacher_id,),
        ).fetchall()

        return [
            serialize_lesson(row)
            for row in rows
        ]

    finally:
        conn.close()


@router.put("/teacher/lessons/{teacher_id}/{lesson_id}")
def update_teacher_lesson(
    teacher_id: int,
    lesson_id: int,
    req: LessonUpdateRequest,
):
    name = req.name.strip()
    content = req.content.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="نام درس نمی‌تواند خالی باشد.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="محتوای درس نمی‌تواند خالی باشد.",
        )

    conn = get_connection()

    try:
        lesson = get_teacher_lesson(
            teacher_id,
            lesson_id,
            conn,
        )

        old_pdf = lesson["pdf_file"]
        new_pdf = req.note_file

        if new_pdf is None:
            new_pdf = old_pdf

        elif new_pdf == "":
            new_pdf = None

            if old_pdf:
                old_path = NOTES_DIR / old_pdf

                if old_path.is_file():
                    old_path.unlink()

        conn.execute(
            """
            UPDATE lessons
            SET
                name = ?,
                content = ?,
                pdf_file = ?
            WHERE id = ?
            """,
            (
                name,
                content,
                new_pdf,
                lesson_id,
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "درس با موفقیت ویرایش شد.",
            "id": lesson_id,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"ویرایش درس انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


@router.delete("/teacher/lessons/{teacher_id}/{lesson_id}")
def delete_teacher_lesson(
    teacher_id: int,
    lesson_id: int,
):
    conn = get_connection()

    try:
        lesson = get_teacher_lesson(
            teacher_id,
            lesson_id,
            conn,
        )

        pdf_file = lesson["pdf_file"]

        conn.execute(
            """
            DELETE FROM teacher_lessons
            WHERE teacher_id = ?
            AND lesson_id = ?
            """,
            (
                teacher_id,
                lesson_id,
            ),
        )

        remaining = conn.execute(
            """
            SELECT 1
            FROM teacher_lessons
            WHERE lesson_id = ?
            LIMIT 1
            """,
            (lesson_id,),
        ).fetchone()

        if not remaining:
            conn.execute(
                """
                DELETE FROM lessons
                WHERE id = ?
                """,
                (lesson_id,),
            )

        conn.commit()

        if pdf_file:
            pdf_path = NOTES_DIR / pdf_file

            if pdf_path.is_file():
                pdf_path.unlink()

        return {
            "status": "success",
            "message": "درس با موفقیت حذف شد.",
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"حذف درس انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


@router.post("/lessons")
def create_lesson(req: LessonCreateRequest):
    name = req.name.strip()
    content = req.content.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="نام درس نمی‌تواند خالی باشد.",
        )

    conn = get_connection()

    try:
        code = f"LESSON-{uuid.uuid4().hex[:8].upper()}"

        cursor = conn.execute(
            """
            INSERT INTO lessons (
                code,
                name,
                lesson_prompt,
                content,
                pdf_file
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                code,
                name,
                "",
                content,
                req.note_file,
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "درس با موفقیت ایجاد شد.",
            "id": cursor.lastrowid,
        }

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"ایجاد درس انجام نشد: {str(e)}",
        )

    finally:
        conn.close()


@router.get("/lessons")
def get_lessons():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                code,
                name,
                lesson_prompt,
                content,
                pdf_file,
                created_at
            FROM lessons
            ORDER BY id DESC
            """
        ).fetchall()

        return {
            "status": "success",
            "lessons": [
                serialize_lesson(row)
                for row in rows
            ],
        }

    finally:
        conn.close()


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int):
    conn = get_connection()

    try:
        lesson = conn.execute(
            """
            SELECT
                id,
                code,
                name,
                lesson_prompt,
                content,
                pdf_file,
                created_at
            FROM lessons
            WHERE id = ?
            """,
            (lesson_id,),
        ).fetchone()

        if not lesson:
            raise HTTPException(
                status_code=404,
                detail="درس پیدا نشد.",
            )

        return {
            "status": "success",
            "lesson": serialize_lesson(lesson),
        }

    finally:
        conn.close()


@router.post("/teacher/assign-lesson")
def assign_lesson_to_teacher(req: AssignLessonRequest):
    conn = get_connection()

    try:
        get_teacher(req.teacher_id, conn)

        lesson = conn.execute(
            """
            SELECT id
            FROM lessons
            WHERE id = ?
            """,
            (req.lesson_id,),
        ).fetchone()

        if not lesson:
            raise HTTPException(
                status_code=404,
                detail="درس پیدا نشد.",
            )

        conn.execute(
            """
            INSERT OR IGNORE INTO teacher_lessons (
                teacher_id,
                lesson_id
            )
            VALUES (?, ?)
            """,
            (
                req.teacher_id,
                req.lesson_id,
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "درس به استاد متصل شد.",
            "teacher_id": req.teacher_id,
            "lesson_id": req.lesson_id,
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"اتصال درس به استاد انجام نشد: {str(e)}",
        )

    finally:
        conn.close()

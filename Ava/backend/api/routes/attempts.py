from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.database import get_connection
from backend.ai.llm import ask_llm
from backend.tts.tts import text_to_speech


router = APIRouter()


AUDIO_DIR = Path(__file__).resolve().parents[3] / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/student/lessons/{student_id}/{lesson_id}/start")
def start_lesson(
    student_id: int,
    lesson_id: int,
):
    conn = get_connection()

    try:
        student = conn.execute(
            """
            SELECT id
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

        lesson = conn.execute(
            """
            SELECT
                l.id,
                l.name,
                l.lesson_prompt,
                l.content,
                l.pdf_file,
                t.id AS teacher_id,
                t.teacher_prompt
            FROM lessons l
            INNER JOIN teacher_lessons tl
                ON tl.lesson_id = l.id
            INNER JOIN teachers t
                ON t.id = tl.teacher_id
            INNER JOIN student_teachers st
                ON st.teacher_id = t.id
            WHERE l.id = ?
              AND st.student_id = ?
            LIMIT 1
            """,
            (lesson_id, student_id),
        ).fetchone()

        if not lesson:
            raise HTTPException(
                status_code=404,
                detail="این درس برای این هنرجو ثبت نشده است.",
            )

        previous_attempt = conn.execute(
            """
            SELECT COALESCE(MAX(attempt_number), 0)
            FROM lesson_attempts
            WHERE student_id = ?
              AND lesson_id = ?
            """,
            (student_id, lesson_id),
        ).fetchone()[0]

        attempt_number = previous_attempt + 1

        final_prompt = f"""
نقش و تنظیمات استاد:
{lesson["teacher_prompt"]}

هدف و دستور درس:
{lesson["lesson_prompt"]}

محتوای درس:
{lesson["content"]}

این یک جلسه آموزشی برای هنرجو است.
محتوای آموزشی را بر اساس اطلاعات بالا ارائه کن.
""".strip()

        response_text = ask_llm(final_prompt)

        audio_file = AUDIO_DIR / (
            f"lesson_{student_id}_{lesson_id}_attempt_{attempt_number}.mp3"
        )

        audio_path = text_to_speech(
            response_text,
            str(audio_file),
        )

        conn.execute(
            """
            INSERT INTO lesson_attempts (
                student_id,
                lesson_id,
                attempt_number,
                text_response,
                audio_path,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                lesson_id,
                attempt_number,
                response_text,
                str(audio_path),
                "completed",
            ),
        )

        conn.execute(
            """
            INSERT INTO student_lessons (
                student_id,
                lesson_id,
                current_attempt
            )
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, lesson_id)
            DO UPDATE SET current_attempt = excluded.current_attempt
            """,
            (
                student_id,
                lesson_id,
                attempt_number,
            ),
        )

        conn.commit()

        return {
            "status": "success",
            "lesson_name": lesson["name"],
            "attempt_number": attempt_number,
            "response": response_text,
            "audio": f"/audio/{audio_file.name}",
            "note_url": (
                f"/notes/{lesson['pdf_file']}"
                if lesson["pdf_file"]
                else None
            ),
        }

    except HTTPException:
        raise

    except Exception as error:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"خطا در شروع درس: {error}",
        ) from error

    finally:
        conn.close()

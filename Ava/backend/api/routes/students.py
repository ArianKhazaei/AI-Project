from fastapi import APIRouter, HTTPException

from backend.database import get_connection


router = APIRouter()


def get_student(student_id: int, conn):
    student = conn.execute(
        """
        SELECT
            id,
            name,
            username,
            level,
            is_approved
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

    return student


@router.get("/student/lessons/{student_id}")
def get_student_lessons(student_id: int):
    conn = get_connection()

    try:
        get_student(student_id, conn)

        rows = conn.execute(
            """
            SELECT DISTINCT
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
            INNER JOIN student_teachers st
                ON st.teacher_id = tl.teacher_id
            WHERE st.student_id = ?
            ORDER BY l.id DESC
            """,
            (student_id,),
        ).fetchall()

        lessons = []

        for row in rows:
            item = dict(row)

            pdf_file = item.get("pdf_file")

            item["note_url"] = (
                f"/notes/{pdf_file}"
                if pdf_file
                else None
            )

            attempt_rows = conn.execute(
                """
                SELECT
                    attempt_number,
                    text_response,
                    audio_path,
                    status,
                    created_at
                FROM lesson_attempts
                WHERE student_id = ?
                  AND lesson_id = ?
                ORDER BY attempt_number ASC
                """,
                (
                    student_id,
                    item["id"],
                ),
            ).fetchall()

            attempts = []

            for attempt in attempt_rows:
                attempt_item = dict(attempt)

                audio_path = attempt_item.get(
                    "audio_path"
                )

                if audio_path:
                    audio_path = audio_path.replace(
                        "\\",
                        "/"
                    )

                    if audio_path.startswith("/audio/"):
                        attempt_item["audio"] = audio_path
                    elif audio_path.startswith("audio/"):
                        attempt_item["audio"] = (
                            "/" + audio_path
                        )
                    else:
                        attempt_item["audio"] = (
                            f"/audio/{audio_path.split('/')[-1]}"
                        )
                else:
                    attempt_item["audio"] = None

                attempt_item["response"] = (
                    attempt_item.get("text_response")
                    or ""
                )

                attempts.append(attempt_item)

            item["attempts"] = attempts

            lessons.append(item)

        return lessons

    finally:
        conn.close()

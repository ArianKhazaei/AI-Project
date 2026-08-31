from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database import get_connection


router = APIRouter()


class AdminPromptRequest(BaseModel):
    system_prompt: str


def get_ava_system_prompt(conn):
    row = conn.execute(
        """
        SELECT value
        FROM system_settings
        WHERE key = 'ava_system_prompt'
        """
    ).fetchone()

    if row and row["value"]:
        return row["value"]

    row = conn.execute(
        """
        SELECT system_prompt
        FROM ava
        WHERE id = 1
        """
    ).fetchone()

    if row and row["system_prompt"]:
        return row["system_prompt"]

    return ""


@router.get("/admin/ava-prompt")
def get_admin_ava_prompt():
    conn = get_connection()

    try:
        prompt = get_ava_system_prompt(conn)

        return {
            "status": "success",
            "system_prompt": prompt,
        }

    finally:
        conn.close()


@router.put("/admin/ava-prompt")
def update_admin_ava_prompt(req: AdminPromptRequest):
    prompt = req.system_prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="System Prompt آوا نمی‌تواند خالی باشد.",
        )

    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE ava
            SET system_prompt = ?
            WHERE id = 1
            """,
            (prompt,),
        )

        conn.execute(
            """
            INSERT INTO system_settings (
                key,
                value
            )
            VALUES (
                'ava_system_prompt',
                ?
            )
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (prompt,),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "System Prompt آوا با موفقیت ذخیره شد.",
            "system_prompt": prompt,
        }

    finally:
        conn.close()

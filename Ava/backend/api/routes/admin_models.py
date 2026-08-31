from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import dotenv_values
import httpx

from backend.database import get_connection


router = APIRouter()


class AdminModelsRequest(BaseModel):
    text_model: str
    voice_model: str


def get_avalai_config():
    env = dotenv_values(".env")

    api_key = env.get("API_KEY")
    api_url = env.get(
        "API_URL",
        "https://api.avalai.ir/v1/chat/completions",
    )

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="خطا: کلید API تنظیم نشده است.",
        )

    models_url = api_url.removesuffix("/chat/completions") + "/models"

    return api_key, models_url


@router.get("/admin/models")
def get_admin_models():

    conn = get_connection()

    try:

        rows = conn.execute(
            """
            SELECT key, value
            FROM system_settings
            WHERE key IN (
                'ava_text_model',
                'ava_voice_model'
            )
            """
        ).fetchall()

        settings = {
            row["key"]: row["value"]
            for row in rows
        }

        return {
            "status": "success",
            "text_model": settings.get(
                "ava_text_model",
                "gpt-5.6-sol",
            ),
            "voice_model": settings.get(
                "ava_voice_model",
                "gpt-4o-mini-tts",
            ),
        }

    finally:
        conn.close()


@router.get("/admin/models/available")
def get_available_models():

    api_key, models_url = get_avalai_config()

    try:
        response = httpx.get(
            models_url,
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            timeout=30.0,
            trust_env=False,
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="خطا: اتصال به سرویس مدل‌های AvalAI برقرار نشد.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="خطا: سرویس AvalAI لیست مدل‌ها را برنگرداند.",
        )

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="خطا: پاسخ سرویس AvalAI معتبر نیست.",
        )

    models = data.get("data", [])

    model_ids = [
        model.get("id")
        for model in models
        if model.get("id")
    ]

    voice_keywords = (
        "tts",
        "audio",
        "voice",
        "eleven_",
        "playai-tts",
    )

    excluded_text_keywords = (
        "embedding",
        "rerank",
        "search",
        "image",
        "transcribe",
        "whisper",
        "moderation",
        "ocr",
        "video",
        "veo",
        "sora",
        "flux",
        "seedream",
        "imagen",
        "z-image",
        "qwen-image",
        "computer-use",
    )

    voice_models = sorted(
        [
            model_id
            for model_id in model_ids
            if any(
                keyword in model_id.lower()
                for keyword in voice_keywords
            )
        ],
        key=str.lower,
    )

    text_models = sorted(
        [
            model_id
            for model_id in model_ids
            if not any(
                keyword in model_id.lower()
                for keyword in voice_keywords
            )
            and not any(
                keyword in model_id.lower()
                for keyword in excluded_text_keywords
            )
        ],
        key=str.lower,
    )

    return {
        "status": "success",
        "text_models": text_models,
        "voice_models": voice_models,
    }


@router.put("/admin/models")
def update_admin_models(req: AdminModelsRequest):

    text_model = req.text_model.strip()
    voice_model = req.voice_model.strip()

    if not text_model:
        raise HTTPException(
            status_code=400,
            detail="مدل متنی آوا نمی‌تواند خالی باشد.",
        )

    if not voice_model:
        raise HTTPException(
            status_code=400,
            detail="مدل صوتی آوا نمی‌تواند خالی باشد.",
        )

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO system_settings (key, value)
            VALUES ('ava_text_model', ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (text_model,),
        )

        conn.execute(
            """
            INSERT INTO system_settings (key, value)
            VALUES ('ava_voice_model', ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (voice_model,),
        )

        conn.commit()

        return {
            "status": "success",
            "message": "مدل‌های آوا با موفقیت ذخیره شدند.",
            "text_model": text_model,
            "voice_model": voice_model,
        }

    finally:
        conn.close()

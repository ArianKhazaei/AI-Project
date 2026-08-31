from pathlib import Path
from os import getenv

import httpx
from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

API_KEY = getenv("API_KEY")
API_URL = getenv("API_URL", "https://api.avalai.ir/v1")
TTS_MODEL = getenv("TTS_MODEL", "gpt-4o-mini-tts")

if not API_KEY:
    raise RuntimeError("خطا: API_KEY در فایل .env تنظیم نشده است.")

http_client = httpx.Client(
    trust_env=False,
    timeout=60.0,
)

client = OpenAI(
    api_key=API_KEY,
    base_url=API_URL.removesuffix("/chat/completions"),
    http_client=http_client,
)


def text_to_speech(
    text: str,
    output_file: str = "audio/output.mp3",
) -> str:

    if not isinstance(text, str):
        raise TypeError("متن ورودی باید از نوع متن باشد.")

    text = text.strip()

    if not text:
        raise ValueError("متن برای تبدیل به صوت نمی‌تواند خالی باشد.")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(output_path)

    except Exception as error:
        raise RuntimeError(
            f"خطا در تبدیل متن به صوت: {error}"
        ) from error

    if not output_path.exists():
        raise RuntimeError("فایل صوتی ایجاد نشد.")

    return str(output_path)


def play_audio(audio_file: str) -> None:

    if not Path(audio_file).exists():
        raise FileNotFoundError(
            f"فایل صوتی پیدا نشد: {audio_file}"
        )

    try:
        import os
        os.startfile(str(Path(audio_file).resolve()))
    except Exception as error:
        raise RuntimeError(
            f"خطا در پخش فایل صوتی: {error}"
        ) from error

from pathlib import Path
from os import getenv

import httpx
from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


API_KEY = getenv("API_KEY")
API_URL = getenv(
    "API_URL",
    "https://api.avalai.ir/v1/chat/completions",
)
LLM_MODEL = getenv(
    "OPENAI_MODEL",
    "gpt-5.6-sol",
)


if not API_KEY:
    raise RuntimeError(
        "خطا: API_KEY در فایل .env تنظیم نشده است."
    )


http_client = httpx.Client(
    trust_env=False,
    timeout=60.0,
)


client = OpenAI(
    api_key=API_KEY,
    base_url=API_URL.removesuffix("/chat/completions"),
    http_client=http_client,
)


def ask_llm(final_prompt: str) -> str:

    if not isinstance(final_prompt, str):
        raise TypeError(
            "Final Prompt باید از نوع متن باشد."
        )

    final_prompt = final_prompt.strip()

    if not final_prompt:
        raise ValueError(
            "Final Prompt نمی‌تواند خالی باشد."
        )

    try:

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": final_prompt,
                }
            ],
        )

        if not response.choices:
            raise RuntimeError(
                "LLM هیچ پاسخی برنگرداند."
            )

        message = response.choices[0].message

        if not message.content:
            raise RuntimeError(
                "پاسخ LLM خالی است."
            )

        return message.content.strip()

    except Exception as error:

        raise RuntimeError(
            f"خطا در ارتباط با LLM: {error}"
        ) from error

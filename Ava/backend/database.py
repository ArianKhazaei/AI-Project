import sqlite3
from pathlib import Path


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "ava.db"


# ============================================================
# Default Ava Prompt
# ============================================================

DEFAULT_AVA_PROMPT = (
    "تو هسته هوشمند سامانه آموزشی آوا هستی.\n"
    "ابتدا مسئله و درخواست کاربر را تحلیل کن.\n"
    "هدف کاربر را به‌درستی تشخیص بده.\n"
    "در صورت نیاز نقش مناسب، وظیفه، محدودیت‌ها و لحن پاسخ را مشخص کن.\n"
    "اطلاعاتی را که کاربر ارائه نکرده است بدون دلیل به درخواست اضافه نکن.\n"
    "پاسخ نهایی باید واضح، روان، دقیق و مناسب تبدیل شدن به گفتار صوتی باشد."
)


# ============================================================
# Database Connection
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================
# Initialize Database
# ============================================================

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ========================================================
    # Ava
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ava (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_prompt TEXT NOT NULL DEFAULT ''
        )
        """
    )

    # ========================================================
    # Admins
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # Students
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE,
            password_hash TEXT,
            level TEXT DEFAULT '',
            is_approved INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # Teachers
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE,
            password TEXT,
            password_hash TEXT,
            prompt TEXT NOT NULL DEFAULT '',
            teacher_prompt TEXT NOT NULL DEFAULT '',
            is_approved INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # Registration Requests
    #
    # status:
    #   pending
    #   approved
    #   rejected
    #
    # user_type:
    #   student
    #   teacher
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS registration_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL,
            name TEXT NOT NULL,
            requested_username TEXT,
            level TEXT DEFAULT '',
            teacher_prompt TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            assigned_username TEXT,
            default_password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        )
        """
    )

    # ========================================================
    # Lessons
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            name TEXT NOT NULL,
            lesson_prompt TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            pdf_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ========================================================
    # Teacher <-> Lesson
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS teacher_lessons (
            teacher_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,

            PRIMARY KEY (teacher_id, lesson_id),

            FOREIGN KEY (teacher_id)
                REFERENCES teachers(id)
                ON DELETE CASCADE,

            FOREIGN KEY (lesson_id)
                REFERENCES lessons(id)
                ON DELETE CASCADE
        )
        """
    )

    # ========================================================
    # Student <-> Lesson
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_lessons (
            student_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            current_attempt INTEGER NOT NULL DEFAULT 0,

            PRIMARY KEY (student_id, lesson_id),

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

            FOREIGN KEY (lesson_id)
                REFERENCES lessons(id)
                ON DELETE CASCADE
        )
        """
    )

    # ========================================================
    # Student <-> Teacher
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_teachers (
            student_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,

            PRIMARY KEY (student_id, teacher_id),

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

            FOREIGN KEY (teacher_id)
                REFERENCES teachers(id)
                ON DELETE CASCADE
        )
        """
    )

    # ========================================================
    # Ava Enrollment
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ava_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            ava_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(student_id, teacher_id, ava_id),

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

            FOREIGN KEY (teacher_id)
                REFERENCES teachers(id)
                ON DELETE CASCADE,

            FOREIGN KEY (ava_id)
                REFERENCES ava(id)
                ON DELETE CASCADE
        )
        """
    )

    # ========================================================
    # Lesson Attempts
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,

            attempt_number INTEGER NOT NULL,

            text_response TEXT NOT NULL DEFAULT '',
            audio_path TEXT,

            status TEXT NOT NULL DEFAULT 'pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(student_id, lesson_id, attempt_number),

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

            FOREIGN KEY (lesson_id)
                REFERENCES lessons(id)
                ON DELETE CASCADE
        )
        """
    )

    # ========================================================
    # System Settings
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    # ========================================================
    # Default Ava Record
    # ========================================================

    cursor.execute(
        """
        INSERT OR IGNORE INTO ava (
            id,
            system_prompt
        )
        VALUES (
            1,
            ?
        )
        """,
        (DEFAULT_AVA_PROMPT,),
    )

    # ========================================================
    # Default Ava System Prompt
    # ========================================================

    cursor.execute(
        """
        INSERT OR IGNORE INTO system_settings (
            key,
            value
        )
        VALUES (
            'ava_system_prompt',
            ?
        )
        """,
        (DEFAULT_AVA_PROMPT,),
    )

    # ========================================================
    # Default Ava Models
    # ========================================================

    cursor.execute(
        """
        INSERT OR IGNORE INTO system_settings (
            key,
            value
        )
        VALUES (
            'ava_text_model',
            'gpt-5.6-sol'
        )
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO system_settings (
            key,
            value
        )
        VALUES (
            'ava_voice_model',
            'gpt-4o-mini-tts'
        )
        """
    )

    # ========================================================
    # Default Admin
    #
    # Username:
    # admin
    #
    # Password:
    # admin
    #
    # بعداً می‌توانیم رمز مدیر را تغییر دهیم.
    # ========================================================

    cursor.execute(
        """
        INSERT OR IGNORE INTO admins (
            username,
            password_hash,
            name
        )
        VALUES (
            'admin',
            'admin',
            'مدیر آوا'
        )
        """
    )

    conn.commit()
    conn.close()


# ============================================================
# Reset User / Lesson Data
#
# این تابع فقط برای پاک‌سازی اطلاعات فعلی پروژه استفاده می‌شود.
# ============================================================

def reset_application_data():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM lesson_attempts")
        cursor.execute("DELETE FROM ava_enrollments")
        cursor.execute("DELETE FROM student_lessons")
        cursor.execute("DELETE FROM teacher_lessons")
        cursor.execute("DELETE FROM student_teachers")
        cursor.execute("DELETE FROM lessons")
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM teachers")
        cursor.execute("DELETE FROM registration_requests")

        # فایل‌ها توسط این تابع حذف نمی‌شوند.
        # حذف فایل‌های صوتی را جداگانه انجام می‌دهیم
        # تا کنترل بیشتری روی فایل‌های پروژه داشته باشیم.

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# Alias
# ============================================================

initialize_database = init_db


# ============================================================
# Direct Execution
# ============================================================

if __name__ == "__main__":
    init_db()
    print("DATABASE_INITIALIZED_OK")

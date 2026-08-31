from backend.database import get_connection


def authenticate_user(
    username: str,
    password: str,
) -> dict:

    if not isinstance(username, str):
        raise TypeError(
            "نام کاربری باید از نوع متن باشد."
        )

    if not isinstance(password, str):
        raise TypeError(
            "رمز عبور باید از نوع متن باشد."
        )

    username = username.strip()

    if not username:
        raise ValueError(
            "نام کاربری نمی‌تواند خالی باشد."
        )

    if not password:
        raise ValueError(
            "رمز عبور نمی‌تواند خالی باشد."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                username,
                name
            FROM teachers
            WHERE username = ?
            AND password = ?
            """,
            (
                username,
                password,
            ),
        )

        teacher = cursor.fetchone()

        if teacher is not None:
            return {
                "id": teacher["id"],
                "username": teacher["username"],
                "name": teacher["name"],
                "role": "teacher",
            }

        cursor.execute(
            """
            SELECT
                id,
                username,
                name
            FROM students
            WHERE username = ?
            AND password = ?
            """,
            (
                username,
                password,
            ),
        )

        student = cursor.fetchone()

    finally:

        connection.close()

    if student is None:
        raise ValueError(
            "نام کاربری یا رمز عبور اشتباه است."
        )

    return {
        "id": student["id"],
        "username": student["username"],
        "name": student["name"],
        "role": "student",
    }

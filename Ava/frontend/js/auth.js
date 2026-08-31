
const usernameInput =
    document.getElementById("username");

const passwordInput =
    document.getElementById("password");

const loginButton =
    document.getElementById("loginButton");

const loginStatus =
    document.getElementById("loginStatus");


const showRegisterButton =
    document.getElementById("showRegisterButton");

const registerPanel =
    document.getElementById("registerPanel");

const registerUserType =
    document.getElementById("registerUserType");

const registerName =
    document.getElementById("registerName");

const registerNationalCode =
    document.getElementById("registerNationalCode");

const registerLevel =
    document.getElementById("registerLevel");

const studentRegisterFields =
    document.getElementById("studentRegisterFields");

const teacherRegisterFields =
    document.getElementById("teacherRegisterFields");

const registerButton =
    document.getElementById("registerButton");

const backToLoginButton =
    document.getElementById("backToLoginButton");

const registerStatus =
    document.getElementById("registerStatus");


/* =====================================================
   LOGIN
   ===================================================== */

loginButton.addEventListener(
    "click",
    async function () {

        const username =
            usernameInput.value.trim();

        const password =
            passwordInput.value;


        if (!username) {

            updateStatus(
                loginStatus,
                "لطفاً نام کاربری را وارد کنید.",
                "error"
            );

            return;
        }


        if (!password) {

            updateStatus(
                loginStatus,
                "لطفاً رمز عبور را وارد کنید.",
                "error"
            );

            return;
        }


        loginButton.disabled = true;

        updateStatus(
            loginStatus,
            "در حال ورود...",
            "loading"
        );


        try {

            let response =
                await fetch(
                    `${API_URL}/login`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            username,
                            password
                        })
                    }
                );


            let data =
                await response.json();


            /*
             * اگر ورود عادی ناموفق بود،
             * ورود مدیر را امتحان می‌کنیم.
             */

            if (!response.ok) {

                response =
                    await fetch(
                        `${API_URL}/admin/login`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                username,
                                password
                            })
                        }
                    );


                data =
                    await response.json();
            }


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "نام کاربری یا رمز عبور اشتباه است."
                );
            }


            currentUser = data;


            loginPanel.classList.add(
                "hidden"
            );


                          /* =================================================
                 ADMIN
                 ================================================= */

              if (
                  currentUser.role ===
                  "admin"
              ) {

                  if (!adminPanel) {

                      throw new Error(
                          "پنل مدیر در HTML پیدا نشد."
                      );
                  }


                  adminPanel.classList.remove(
                      "hidden"
                  );


                  await loadAdminPanel();

                  return;
              }


            /* =================================================
               TEACHER
               ================================================= */

            if (
                currentUser.role ===
                "teacher"
            ) {

                teacherPanel.classList.remove(
                    "hidden"
                );


                document.getElementById(
                    "teacherInfo"
                ).textContent =
                    `نام: ${currentUser.name}\nنام کاربری: ${currentUser.username}`;


                await loadTeacherPrompt();

                await loadTeacherLessons();

                return;
            }


            /* =================================================
               STUDENT
               ================================================= */

            if (
                currentUser.role ===
                "student"
            ) {

                studentPanel.classList.remove(
                    "hidden"
                );


                document.getElementById(
                    "studentInfo"
                ).textContent =
                    `نام: ${currentUser.name}\nنام کاربری: ${currentUser.username}`;


                await loadStudentLessons();

                return;
            }


            throw new Error(
                "نقش کاربر معتبر نیست."
            );

        }


        catch (error) {

            console.error(
                "خطا در ورود:",
                error
            );


            updateStatus(
                loginStatus,
                "خطا: " + error.message,
                "error"
            );

        }


        finally {

            loginButton.disabled = false;

        }

    }
);


/* =====================================================
   REGISTER PANEL
   ===================================================== */

showRegisterButton.addEventListener(
    "click",
    function () {

        document.querySelector(
            ".login-form"
        ).classList.add("hidden");


        registerPanel.classList.remove(
            "hidden"
        );


        updateStatus(
            registerStatus,
            "",
            ""
        );

    }
);


/* =====================================================
   BACK TO LOGIN
   ===================================================== */

backToLoginButton.addEventListener(
    "click",
    function () {

        registerPanel.classList.add(
            "hidden"
        );


        document.querySelector(
            ".login-form"
        ).classList.remove("hidden");


        updateStatus(
            registerStatus,
            "",
            ""
        );

    }
);


/* =====================================================
   REGISTER USER TYPE
   ===================================================== */

registerUserType.addEventListener(
    "change",
    function () {

        if (
            registerUserType.value ===
            "teacher"
        ) {

            studentRegisterFields.classList.add(
                "hidden"
            );


            teacherRegisterFields.classList.remove(
                "hidden"
            );

        }

        else {

            teacherRegisterFields.classList.add(
                "hidden"
            );


            studentRegisterFields.classList.remove(
                "hidden"
            );

        }

    }
);


/* =====================================================
   REGISTER
   ===================================================== */

registerButton.addEventListener(
    "click",
    async function () {

        const name =
            registerName.value.trim();

        const nationalCode =
            registerNationalCode.value.trim();

        const userType =
            registerUserType.value;


        if (!name) {

            updateStatus(
                registerStatus,
                "لطفاً نام خود را وارد کنید.",
                "error"
            );

            return;
        }


        if (!/^\d{10}$/.test(nationalCode)) {

            updateStatus(
                registerStatus,
                "کد ملی باید دقیقاً ۱۰ رقم و فقط شامل اعداد باشد.",
                "error"
            );

            return;
        }


        registerButton.disabled = true;


        updateStatus(
            registerStatus,
            "در حال ارسال درخواست ثبت‌نام...",
            "loading"
        );


        try {

            let endpoint;

            let body;


            if (
                userType ===
                "student"
            ) {

                endpoint =
                    `${API_URL}/register/student`;


                body = {
                    name,
                    national_code:
                        nationalCode,
                    level:
                        registerLevel.value
                };

            }

            else {

                endpoint =
                    `${API_URL}/register/teacher`;


                body = {
                    name,
                    national_code:
                        nationalCode
                };

            }


            const response =
                await fetch(
                    endpoint,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(body)
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "ثبت درخواست ثبت‌نام انجام نشد."
                );
            }


            updateStatus(
                registerStatus,
                `${data.message} کد درخواست: ${data.request_id}`,
                "success"
            );


            registerName.value = "";
}


        catch (error) {

            console.error(
                "خطا در ثبت‌نام:",
                error
            );


            updateStatus(
                registerStatus,
                "خطا: " + error.message,
                "error"
            );

        }


        finally {

            registerButton.disabled = false;

        }

    }
);





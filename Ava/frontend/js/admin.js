const adminInfo =
    document.getElementById("adminInfo");

const registrationRequestsList =
    document.getElementById(
        "registrationRequestsList"
    );

const adminUsersList =
    document.getElementById(
        "adminUsersList"
    );

const adminPrompt =
    document.getElementById("adminPrompt");

const saveAdminPromptButton =
    document.getElementById(
        "saveAdminPromptButton"
    );

const adminPromptStatus =
    document.getElementById(
        "adminPromptStatus"
    );


/* =====================================================
   REGISTRATION REQUESTS
   ===================================================== */

async function loadAdminRegistrationRequests() {

    if (!registrationRequestsList) {
        return;
    }

    setLoadingContent(
        registrationRequestsList,
        "در حال دریافت درخواست‌های ثبت‌نام..."
    );

    try {

        const response =
            await fetch(
                `${API_URL}/admin/registration-requests`
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "دریافت درخواست‌ها ناموفق بود."
            );
        }

        registrationRequestsList.innerHTML = "";

        const requests =
            Array.isArray(data.requests)
                ? data.requests
                : [];

        if (requests.length === 0) {

            updateStatus(
                registrationRequestsList,
                "هیچ درخواست ثبت‌نامی وجود ندارد."
            );

            return;
        }

        requests.forEach(
            function (request) {

                const card =
                    document.createElement("div");

                card.className = "lesson";

                const title =
                    document.createElement("div");

                title.className = "lesson-title";

                title.textContent =
                    request.name;

                const details =
                    document.createElement("div");

                details.className =
                    "lesson-output-text";

                const typeText =
                    request.user_type === "teacher"
                        ? "استاد"
                        : "هنرجو";

                const statusText =
                    request.status === "pending"
                        ? "در انتظار بررسی"
                        : request.status === "approved"
                            ? "تأیید شده"
                            : "رد شده";

                details.textContent =
                    `نوع: ${typeText} | ` +
                    `کد ملی: ${request.requested_username || "-"} | ` +
                    `وضعیت: ${statusText}`;

                card.appendChild(title);
                card.appendChild(details);

                if (request.level) {

                    const level =
                        document.createElement("div");

                    level.className =
                        "field-hint";

                    level.textContent =
                        `سطح: ${request.level}`;

                    card.appendChild(level);
                }

                if (
                    request.teacher_prompt
                ) {

                    const teacherPrompt =
                        document.createElement("div");

                    teacherPrompt.className =
                        "field-hint";

                    teacherPrompt.textContent =
                        `Prompt استاد: ${request.teacher_prompt}`;

                    card.appendChild(
                        teacherPrompt
                    );
                }

                if (
                    request.status === "pending"
                ) {

                    const actions =
                        document.createElement("div");

                    actions.className =
                        "form-actions";

                    const approveButton =
                        document.createElement("button");

                    approveButton.type = "button";
                    approveButton.className =
                        "primary-button";
                    approveButton.textContent =
                        "تأیید";

                    const rejectButton =
                        document.createElement("button");

                    rejectButton.type = "button";
                    rejectButton.className =
                        "ghost-button";
                    rejectButton.textContent =
                        "رد درخواست";

                    approveButton.addEventListener(
                        "click",
                        function () {
                            processRegistrationRequest(
                                request.id,
                                true,
                                approveButton,
                                rejectButton
                            );
                        }
                    );

                    rejectButton.addEventListener(
                        "click",
                        function () {
                            processRegistrationRequest(
                                request.id,
                                false,
                                approveButton,
                                rejectButton
                            );
                        }
                    );

                    actions.appendChild(
                        approveButton
                    );

                    actions.appendChild(
                        rejectButton
                    );

                    card.appendChild(actions);
                }

                if (
                    request.status === "approved"
                ) {

                    const accountInfo =
                        document.createElement("div");

                    accountInfo.className =
                        "save-status";

                    accountInfo.textContent =
                        `نام کاربری: ${request.assigned_username || request.requested_username || "-"} | رمز اولیه: ${request.default_password || "1234"}`;

                    card.appendChild(
                        accountInfo
                    );
                }

                registrationRequestsList.appendChild(
                    card
                );
            }
        );

    }

    catch (error) {

        console.error(
            "خطا در دریافت درخواست‌های ثبت‌نام:",
            error
        );

        updateStatus(
            registrationRequestsList,
            "خطا: " + error.message,
            "error"
        );
    }
}


/* =====================================================
   PROCESS REGISTRATION REQUEST
   ===================================================== */

async function processRegistrationRequest(
    requestId,
    approve,
    approveButton,
    rejectButton
) {

    const actionText =
        approve
            ? "تأیید"
            : "رد";

    if (
        approve &&
        !window.confirm(
            "آیا از تأیید این درخواست ثبت‌نام مطمئن هستید؟"
        )
    ) {
        return;
    }

    if (
        !approve &&
        !window.confirm(
            "آیا از رد این درخواست ثبت‌نام مطمئن هستید؟"
        )
    ) {
        return;
    }

    approveButton.disabled = true;
    rejectButton.disabled = true;

    try {

        const response =
            await fetch(
                `${API_URL}/admin/registration-requests/process`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        request_id: requestId,
                        approve: approve
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                `عملیات ${actionText} ناموفق بود.`
            );
        }

        if (
            approve &&
            data.username
        ) {

            alert(
                `ثبت‌نام تأیید شد.\n\n` +
                `نام کاربری: ${data.username}\n` +
                `رمز عبور: ${data.password || "1234"}`
            );
        }

        else if (!approve) {

            alert(
                "درخواست ثبت‌نام رد شد."
            );
        }

        await loadAdminRegistrationRequests();
        await loadAdminUsers();
    }

    catch (error) {

        console.error(
            "خطا در پردازش درخواست:",
            error
        );

        alert(
            "خطا: " + error.message
        );

        approveButton.disabled = false;
        rejectButton.disabled = false;
    }
}


/* =====================================================
   USER MANAGEMENT
   ===================================================== */

async function loadAdminUsers() {

    if (!adminUsersList) {
        return;
    }

    setLoadingContent(
        adminUsersList,
        "در حال دریافت فهرست استادها و هنرجوها..."
    );

    try {

        const response =
            await fetch(
                `${API_URL}/admin/users`
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "دریافت فهرست کاربران ناموفق بود."
            );
        }

        adminUsersList.innerHTML = "";

        const students =
            Array.isArray(data.students)
                ? data.students
                : [];

        const teachers =
            Array.isArray(data.teachers)
                ? data.teachers
                : [];


        /* =================================================
           STUDENTS
           ================================================= */

        if (students.length > 0) {

            const studentsTitle =
                document.createElement("div");

            studentsTitle.className =
                "section-kicker";

            studentsTitle.textContent =
                "هنرجوها";

            adminUsersList.appendChild(
                studentsTitle
            );


            students.forEach(
                function (student) {

                    const card =
                        createAdminUserCard(
                            student,
                            "student"
                        );

                    adminUsersList.appendChild(
                        card
                    );
                }
            );
        }


        /* =================================================
           TEACHERS
           ================================================= */

        if (teachers.length > 0) {

            const teachersTitle =
                document.createElement("div");

            teachersTitle.className =
                "section-kicker";

            teachersTitle.textContent =
                "استادها";

            adminUsersList.appendChild(
                teachersTitle
            );


            teachers.forEach(
                function (teacher) {

                    const card =
                        createAdminUserCard(
                            teacher,
                            "teacher"
                        );

                    adminUsersList.appendChild(
                        card
                    );
                }
            );
        }


        if (
            students.length === 0 &&
            teachers.length === 0
        ) {

            updateStatus(
                adminUsersList,
                "هیچ استاد یا هنرجویی ثبت نشده است."
            );
        }

    }

    catch (error) {

        console.error(
            "خطا در دریافت کاربران:",
            error
        );

        updateStatus(
            adminUsersList,
            "خطا: " + error.message,
            "error"
        );
    }
}


/* =====================================================
   CREATE USER CARD
   ===================================================== */

function createAdminUserCard(
    user,
    userType
) {

    const card =
        document.createElement("div");

    card.className = "lesson";


    const title =
        document.createElement("div");

    title.className = "lesson-title";

    title.textContent =
        user.name || "-";

    card.appendChild(title);


    const details =
        document.createElement("div");

    details.className =
        "lesson-output-text";

    const typeText =
        userType === "teacher"
            ? "استاد"
            : "هنرجو";

    details.textContent =
        `نوع: ${typeText} | ` +
        `کد ملی: ${user.username || "-"} | ` +
        `شناسه: ${user.id}`;

    card.appendChild(details);


    if (
        userType === "student" &&
        user.level
    ) {

        const level =
            document.createElement("div");

        level.className =
            "field-hint";

        level.textContent =
            `سطح: ${user.level}`;

        card.appendChild(level);
    }


    const actions =
        document.createElement("div");

    actions.className =
        "form-actions";


    const deleteButton =
        document.createElement("button");

    deleteButton.type = "button";
    deleteButton.className =
        "ghost-button";
    deleteButton.textContent =
        userType === "teacher"
            ? "حذف استاد"
            : "حذف هنرجو";


    deleteButton.addEventListener(
        "click",
        function () {

            deleteAdminUser(
                user.id,
                user.name,
                userType,
                deleteButton
            );

        }
    );


    actions.appendChild(
        deleteButton
    );

    card.appendChild(actions);


    return card;
}


/* =====================================================
   DELETE USER
   ===================================================== */

async function deleteAdminUser(
    userId,
    userName,
    userType,
    deleteButton
) {

    const typeText =
        userType === "teacher"
            ? "استاد"
            : "هنرجو";


    const confirmed =
        window.confirm(
            `آیا از حذف ${typeText} «${userName}» مطمئن هستید؟\n\n` +
            "تمام ارتباطات وابسته به این کاربر نیز حذف خواهد شد."
        );


    if (!confirmed) {
        return;
    }


    deleteButton.disabled = true;


    try {

        const endpoint =
            userType === "teacher"
                ? `${API_URL}/admin/users/teacher/${userId}`
                : `${API_URL}/admin/users/student/${userId}`;


        const response =
            await fetch(
                endpoint,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail ||
                `حذف ${typeText} ناموفق بود.`
            );
        }


        alert(
            data.message ||
            `${typeText} با موفقیت حذف شد.`
        );


        await loadAdminUsers();
        await loadAdminRegistrationRequests();

    }

    catch (error) {

        console.error(
            `خطا در حذف ${typeText}:`,
            error
        );

        alert(
            "خطا: " + error.message
        );

        deleteButton.disabled = false;
    }
}


/* =====================================================
   AVA SYSTEM PROMPT
   ===================================================== */

async function loadAdminPrompt() {

    if (!adminPrompt) {
        return;
    }

    updateStatus(
        adminPromptStatus,
        "در حال دریافت System Prompt...",
        "loading"
    );

    try {

        const response =
            await fetch(
                `${API_URL}/admin/ava-prompt`
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "دریافت System Prompt ناموفق بود."
            );
        }

        adminPrompt.value =
            data.system_prompt || "";

        updateStatus(
            adminPromptStatus,
            "System Prompt دریافت شد.",
            "success"
        );

    }

    catch (error) {

        console.error(
            "خطا در دریافت System Prompt:",
            error
        );

        updateStatus(
            adminPromptStatus,
            "خطا: " + error.message,
            "error"
        );
    }
}


async function saveAdminPrompt() {

    const prompt =
        adminPrompt.value.trim();

    if (!prompt) {

        updateStatus(
            adminPromptStatus,
            "System Prompt نمی‌تواند خالی باشد.",
            "error"
        );

        return;
    }

    saveAdminPromptButton.disabled = true;

    updateStatus(
        adminPromptStatus,
        "در حال ذخیره System Prompt...",
        "loading"
    );

    try {

        const response =
            await fetch(
                `${API_URL}/admin/ava-prompt`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        system_prompt: prompt
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "ذخیره System Prompt ناموفق بود."
            );
        }

        updateStatus(
            adminPromptStatus,
            data.message ||
                "System Prompt با موفقیت ذخیره شد.",
            "success"
        );
    }

    catch (error) {

        console.error(
            "خطا در ذخیره System Prompt:",
            error
        );

        updateStatus(
            adminPromptStatus,
            "خطا: " + error.message,
            "error"
        );
    }

    finally {

        saveAdminPromptButton.disabled = false;
    }
}


/* =====================================================
   ADMIN PANEL
   ===================================================== */

async function loadAdminPanel() {

    if (!currentUser) {
        return;
    }

    if (
        currentUser.role !==
        "admin"
    ) {
        return;
    }

    if (adminInfo) {

        adminInfo.textContent =
            `نام: ${currentUser.name}\nنام کاربری: ${currentUser.username}`;
    }

    await loadAdminRegistrationRequests();
    await loadAdminUsers();
    await loadAdminPrompt();
    await loadAvaModels();
}


if (saveAdminPromptButton) {

    saveAdminPromptButton.addEventListener(
        "click",
        saveAdminPrompt
    );
}


/* =====================================================
   AVA MODEL SELECTION
   ===================================================== */

const avaTextModel =
    document.getElementById("avaTextModel");

const avaVoiceModel =
    document.getElementById("avaVoiceModel");

const saveAvaModelsButton =
    document.getElementById("saveAvaModelsButton");

const avaModelsStatus =
    document.getElementById("avaModelsStatus");


async function loadAvaModels() {

    if (
        !avaTextModel ||
        !avaVoiceModel
    ) {
        return;
    }

    updateStatus(
        avaModelsStatus,
        "?? ??? ?????? ??????? ???...",
        "loading"
    );

    try {

        const availableResponse =
            await fetch(
                `${API_URL}/admin/models/available`
            );

        const availableData =
            await availableResponse.json();

        if (!availableResponse.ok) {
            throw new Error(
                availableData.detail ||
                "?????? ???? ??????? ??? ?????? ???."
            );
        }

        const currentResponse =
            await fetch(
                `${API_URL}/admin/models`
            );

        const currentData =
            await currentResponse.json();

        if (!currentResponse.ok) {
            throw new Error(
                currentData.detail ||
                "?????? ??????? ?????????? ??? ?????? ???."
            );
        }

        const textModel =
            currentData.text_model || "";

        const voiceModel =
            currentData.voice_model || "";

        const textModels =
            Array.isArray(availableData.text_models)
                ? availableData.text_models
                : [];

        const voiceModels =
            Array.isArray(availableData.voice_models)
                ? availableData.voice_models
                : [];

        avaTextModel.innerHTML = "";

        avaVoiceModel.innerHTML = "";

        const textPlaceholder =
            document.createElement("option");

        textPlaceholder.value = "";
        textPlaceholder.textContent =
            "?????? ??? ????";

        avaTextModel.appendChild(
            textPlaceholder
        );

        const avaRecommendedTextModels = [
            { id: "gpt-5.6-luna", name: "GPT-5.6 Luna", level: "خیلی قوی" },
            { id: "gpt-5.6-sol", name: "GPT-5.6 Sol", level: "قوی" },
            { id: "claude-opus-5", name: "Claude Opus 5", level: "قوی" },
            { id: "gemini-3.5-flash", name: "Gemini 3.5 Flash", level: "متوسط" },
            { id: "gpt-5-mini", name: "GPT-5 Mini", level: "ضعیف" }
        ];

        avaRecommendedTextModels.forEach((model) => {

            const option = document.createElement("option");
            option.value = model.id;
            option.textContent = `${model.name} — ${model.level}`;
            avaTextModel.appendChild(option);
        });

        const avaRecommendedVoiceModels = [
            { id: "eleven_v3", name: "Eleven V3", level: "خیلی قوی" },
            { id: "gpt-4o-mini-tts", name: "GPT-4o Mini TTS", level: "قوی" },
            { id: "gemini-2.5-pro-tts", name: "Gemini 2.5 Pro TTS", level: "قوی" },
            { id: "eleven_multilingual_v2", name: "Eleven Multilingual V2", level: "متوسط" },
            { id: "tts-1", name: "TTS-1", level: "ضعیف" }
        ];
        avaRecommendedVoiceModels.forEach((model) => {

            const option =
                document.createElement("option");

            option.value = model.id;
            option.textContent = `${model.name} — ${model.level}`;

            avaVoiceModel.appendChild(option);
        });

        if (textModel) {
            avaTextModel.value = textModel;
        }

        if (voiceModel) {
            avaVoiceModel.value = voiceModel;
        }

        updateStatus(
            avaModelsStatus,
            "??????? ??? ?????? ????.",
            "success"
        );

    }

    catch (error) {

        console.error(
            "??? ?? ?????? ??????? ???:",
            error
        );

        updateStatus(
            avaModelsStatus,
            "???: " + error.message,
            "error"
        );
    }
}

async function saveAvaModels() {

    const textModel =
        avaTextModel.value.trim();

    const voiceModel =
        avaVoiceModel.value.trim();

    if (!textModel) {

        updateStatus(
            avaModelsStatus,
            "لطفاً مدل متنی آوا را انتخاب کنید.",
            "error"
        );

        return;
    }

    if (!voiceModel) {

        updateStatus(
            avaModelsStatus,
            "لطفاً مدل صوتی آوا را انتخاب کنید.",
            "error"
        );

        return;
    }

    saveAvaModelsButton.disabled = true;

    updateStatus(
        avaModelsStatus,
        "در حال ذخیره مدل‌ها...",
        "loading"
    );

    try {

        const response =
            await fetch(
                `${API_URL}/admin/models`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        text_model: textModel,
                        voice_model: voiceModel
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "ذخیره مدل‌های آوا ناموفق بود."
            );
        }

        updateStatus(
            avaModelsStatus,
            data.message ||
                "مدل‌های آوا با موفقیت ذخیره شدند.",
            "success"
        );

    }

    catch (error) {

        console.error(
            "خطا در ذخیره مدل‌های آوا:",
            error
        );

        updateStatus(
            avaModelsStatus,
            "خطا: " + error.message,
            "error"
        );
    }

    finally {

        saveAvaModelsButton.disabled = false;
    }
}


if (saveAvaModelsButton) {

    saveAvaModelsButton.addEventListener(
        "click",
        saveAvaModels
    );
}










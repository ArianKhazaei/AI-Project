const teacherPrompt =
    document.getElementById(
        "teacherPrompt"
    );

const saveTeacherPromptButton =
    document.getElementById(
        "saveTeacherPromptButton"
    );

const teacherPromptStatus =
    document.getElementById(
        "teacherPromptStatus"
    );

const lessonName =
    document.getElementById(
        "lessonName"
    );

const lessonContent =
    document.getElementById(
        "lessonContent"
    );

const lessonNoteFile =
    document.getElementById(
        "lessonNoteFile"
    );

const lessonNoteInfo =
    document.getElementById(
        "lessonNoteInfo"
    );

const createLessonButton =
    document.getElementById(
        "createLessonButton"
    );

const lessonCreateStatus =
    document.getElementById(
        "lessonCreateStatus"
    );

const lessonsList =
    document.getElementById(
        "lessonsList"
    );

const saveLessonEditButton =
    document.getElementById(
        "saveLessonEditButton"
    );

const cancelLessonEditButton =
    document.getElementById(
        "cancelLessonEditButton"
    );

let editingLessonId = null;
let editingLessonHasNote = false;


async function uploadLessonNoteIfNeeded() {

    if (
        !lessonNoteFile ||
        !lessonNoteFile.files ||
        lessonNoteFile.files.length === 0
    ) {
        return null;
    }

    const selectedFile =
        lessonNoteFile.files[0];

    if (
        !selectedFile.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {
        throw new Error(
            "فقط فایل PDF مجاز است."
        );
    }

    const formData = new FormData();
    formData.append(
        "note",
        selectedFile
    );

    lessonNoteInfo.textContent =
        "";

    updateStatus(
        lessonNoteInfo,
        "در حال آپلود PDF...",
        "loading"
    );

    const response = await fetch(
        `${API_URL}/teacher/notes/upload/${currentUser.id}`,
        {
            method: "POST",
            body: formData
        }
    );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "آپلود PDF ناموفق بود."
        );
    }

    updateStatus(
        lessonNoteInfo,
        "PDF با موفقیت آپلود شد.",
        "success"
    );

    return data.note_file;
}


function setLessonStatus(
    message,
    type
) {
    if (type === "status-loading") {
        updateStatus(
            lessonCreateStatus,
            message,
            "loading"
        );

        return;
    }

    if (type === "status-success") {
        updateStatus(
            lessonCreateStatus,
            message,
            "success"
        );

        return;
    }

    if (type === "status-error") {
        updateStatus(
            lessonCreateStatus,
            message,
            "error"
        );

        return;
    }

    updateStatus(
        lessonCreateStatus,
        message
    );
}


function resetLessonEditor() {

    editingLessonId = null;
    editingLessonHasNote = false;

    lessonName.value = "";
    lessonContent.value = "";
    lessonNoteFile.value = "";

    lessonNoteInfo.textContent =
        "";

    updateStatus(
        lessonNoteInfo,
        "فایل PDF اختیاری است."
    );

    createLessonButton.classList.remove(
        "hidden"
    );

    saveLessonEditButton.classList.add(
        "hidden"
    );

    cancelLessonEditButton.classList.add(
        "hidden"
    );
}


function startEditingLesson(lesson) {

    editingLessonId = lesson.id;
    editingLessonHasNote =
        Boolean(lesson.note_url);

    lessonName.value = lesson.name;
    lessonContent.value = lesson.content;
    lessonNoteFile.value = "";

    if (lesson.note_url) {
        lessonNoteInfo.innerHTML =
            `نوت فعلی: <a class="lesson-note-link" href="${API_URL}${lesson.note_url}" target="_blank" rel="noopener noreferrer">مشاهده PDF</a>`;
    } else {
        lessonNoteInfo.textContent =
            "این درس نوت PDF ندارد.";
    }

    createLessonButton.classList.add(
        "hidden"
    );

    saveLessonEditButton.classList.remove(
        "hidden"
    );

    cancelLessonEditButton.classList.remove(
        "hidden"
    );

    setLessonStatus(
        "حالت ویرایش فعال شد.",
        "status-loading"
    );
}


async function loadTeacherPrompt() {

    teacherPromptStatus.textContent =
        "";

    updateStatus(
        teacherPromptStatus,
        "در حال دریافت Prompt...",
        "loading"
    );


    try {

        const response =
            await fetch(
                `${API_URL}/teacher/prompt/${currentUser.id}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "دریافت Prompt ناموفق بود."
            );
        }


        teacherPrompt.value =
            data.prompt || "";


        updateStatus(
            teacherPromptStatus,
            "Prompt با موفقیت دریافت شد.",
            "success"
        );

    }


    catch (error) {

        console.error(error);

        updateStatus(
            teacherPromptStatus,
            "خطا: " + error.message,
            "error"
        );

    }

}


saveTeacherPromptButton.addEventListener(
    "click",
    async function () {

        const prompt =
            teacherPrompt.value.trim();


        if (!prompt) {

            updateStatus(
                teacherPromptStatus,
                "Prompt نمی‌تواند خالی باشد.",
                "error"
            );

            return;
        }


        saveTeacherPromptButton.disabled =
            true;


        updateStatus(
            teacherPromptStatus,
            "در حال ذخیره...",
            "loading"
        );


        try {

            const response =
                await fetch(
                    `${API_URL}/teacher/prompt/${currentUser.id}`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            prompt
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "ذخیره Prompt ناموفق بود."
                );
            }


            teacherPrompt.value =
                data.prompt;


            updateStatus(
                teacherPromptStatus,
                "Prompt با موفقیت ذخیره شد.",
                "success"
            );

        }


        catch (error) {

            console.error(error);

            updateStatus(
                teacherPromptStatus,
                "خطا: " + error.message,
                "error"
            );

        }


        finally {

            saveTeacherPromptButton.disabled =
                false;

        }

    }
);


createLessonButton.addEventListener(
    "click",
    async function () {

        const name =
            lessonName.value.trim();

        const content =
            lessonContent.value.trim();


        if (!name) {

            setLessonStatus(
                "نام درس نمی‌تواند خالی باشد.",
                "status-error"
            );

            return;
        }


        if (!content) {

            setLessonStatus(
                "محتوای درس نمی‌تواند خالی باشد.",
                "status-error"
            );

            return;
        }


        createLessonButton.disabled =
            true;


        setLessonStatus(
            "در حال ساخت درس...",
            "status-loading"
        );


        try {

            const uploadedNoteFile =
                await uploadLessonNoteIfNeeded();

            const payload = {
                name,
                content
            };

            if (uploadedNoteFile !== null) {
                payload.note_file =
                    uploadedNoteFile;
            }

            const response =
                await fetch(
                    `${API_URL}/teacher/lessons/${currentUser.id}`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(
                            payload
                        )
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "ساخت درس ناموفق بود."
                );
            }


            setLessonStatus(
                "درس با موفقیت ساخته شد.",
                "status-success"
            );


            resetLessonEditor();


            await loadTeacherLessons();

        }


        catch (error) {

            console.error(error);

            setLessonStatus(
                "خطا: " + error.message,
                "status-error"
            );

        }


        finally {

            createLessonButton.disabled =
                false;

        }

    }
);


saveLessonEditButton.addEventListener(
    "click",
    async function () {

        if (editingLessonId === null) {

            setLessonStatus(
                "برای ذخیره، ابتدا یک درس را انتخاب کنید.",
                "status-error"
            );

            return;
        }

        const name =
            lessonName.value.trim();

        const content =
            lessonContent.value.trim();

        if (!name) {

            setLessonStatus(
                "نام درس نمی‌تواند خالی باشد.",
                "status-error"
            );

            return;
        }

        if (!content) {

            setLessonStatus(
                "محتوای درس نمی‌تواند خالی باشد.",
                "status-error"
            );

            return;
        }

        saveLessonEditButton.disabled =
            true;

        setLessonStatus(
            "در حال ذخیره ویرایش...",
            "status-loading"
        );

        try {

            const uploadedNoteFile =
                await uploadLessonNoteIfNeeded();

            const payload = {
                name,
                content
            };

            if (uploadedNoteFile !== null) {
                payload.note_file =
                    uploadedNoteFile;

                editingLessonHasNote = true;
            }

            else if (
                !editingLessonHasNote
            ) {
                payload.note_file = "";
            }

            const response =
                await fetch(
                    `${API_URL}/teacher/lessons/${currentUser.id}/${editingLessonId}`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(
                            payload
                        )
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "ویرایش درس ناموفق بود."
                );
            }

            setLessonStatus(
                "درس با موفقیت ویرایش شد.",
                "status-success"
            );

            resetLessonEditor();

            await loadTeacherLessons();

        }

        catch (error) {

            console.error(error);

            setLessonStatus(
                "خطا: " + error.message,
                "status-error"
            );

        }

        finally {

            saveLessonEditButton.disabled =
                false;

        }

    }
);


cancelLessonEditButton.addEventListener(
    "click",
    function () {

        resetLessonEditor();

        setLessonStatus(
            "ویرایش لغو شد.",
            "status-loading"
        );
    }
);


async function loadTeacherLessons() {

    setLoadingContent(
        lessonsList,
        "در حال دریافت درس‌ها..."
    );


    try {

        const response =
            await fetch(
                `${API_URL}/teacher/lessons/${currentUser.id}`
            );


        const lessons =
            await response.json();


        if (!response.ok) {

            throw new Error(
                lessons.detail ||
                "دریافت درس‌ها ناموفق بود."
            );
        }


        lessonsList.innerHTML = "";


        if (!lessons.length) {

            lessonsList.textContent =
                "هنوز درسی ساخته نشده است.";

            return;
        }


        lessons.forEach(
            function (lesson) {

                const lessonElement =
                    document.createElement(
                        "div"
                    );


                lessonElement.className =
                    "lesson";


                const titleElement =
                    document.createElement(
                        "div"
                    );


                titleElement.className =
                    "lesson-title";


                titleElement.textContent =
                    lesson.name;


                const contentElement =
                    document.createElement(
                        "div"
                    );


                contentElement.className =
                    "lesson-content";


                contentElement.textContent =
                    lesson.content;

                const noteLinkElement =
                    document.createElement(
                        "a"
                    );

                noteLinkElement.className =
                    "lesson-note-link";

                noteLinkElement.target =
                    "_blank";

                noteLinkElement.rel =
                    "noopener noreferrer";

                if (lesson.note_url) {
                    noteLinkElement.textContent =
                        "مشاهده نوت PDF";

                    noteLinkElement.href =
                        `${API_URL}${lesson.note_url}`;
                } else {
                    noteLinkElement.textContent =
                        "نوت PDF ندارد";

                    noteLinkElement.removeAttribute(
                        "href"
                    );
                    noteLinkElement.style.opacity =
                        "0.7";
                    noteLinkElement.style.cursor =
                        "default";
                }


                lessonElement.appendChild(
                    titleElement
                );


                lessonElement.appendChild(
                    contentElement
                );

                lessonElement.appendChild(
                    noteLinkElement
                );


                const actionsElement =
                    document.createElement(
                        "div"
                    );


                actionsElement.className =
                    "lesson-actions";


                const editButton =
                    document.createElement(
                        "button"
                    );


                editButton.textContent =
                    "ویرایش";

                editButton.className =
                    "button-secondary";


                editButton.addEventListener(
                    "click",
                    function () {
                        startEditingLesson(
                            lesson
                        );
                    }
                );


                const deleteButton =
                    document.createElement(
                        "button"
                    );


                deleteButton.textContent =
                    "حذف";

                deleteButton.className =
                    "button-danger";


                deleteButton.addEventListener(
                    "click",
                    async function () {

                        const confirmed =
                            confirm(
                                `آیا از حذف درس «${lesson.name}» مطمئن هستید؟`
                            );


                        if (!confirmed) {
                            return;
                        }


                        deleteButton.disabled =
                            true;


                        setLessonStatus(
                            "در حال حذف درس...",
                            "status-loading"
                        );


                        try {

                            const response =
                                await fetch(
                                    `${API_URL}/teacher/lessons/${currentUser.id}/${lesson.id}`,
                                    {
                                        method: "DELETE"
                                    }
                                );


                            const data =
                                await response.json();


                            if (!response.ok) {

                                throw new Error(
                                    data.detail ||
                                    "حذف درس ناموفق بود."
                                );
                            }


                            setLessonStatus(
                                data.message ||
                                "درس با موفقیت حذف شد.",
                                "status-success"
                            );

                            if (
                                editingLessonId ===
                                lesson.id
                            ) {
                                resetLessonEditor();
                            }


                            await loadTeacherLessons();

                        }


                        catch (error) {

                            console.error(error);

                            setLessonStatus(
                                "خطا: " + error.message,
                                "status-error"
                            );

                        }


                        finally {

                            deleteButton.disabled =
                                false;

                        }

                    }
                );


                actionsElement.appendChild(
                    editButton
                );


                actionsElement.appendChild(
                    deleteButton
                );


                lessonElement.appendChild(
                    actionsElement
                );


                lessonsList.appendChild(
                    lessonElement
                );

            }
        );

    }


    catch (error) {

        console.error(error);

        lessonsList.textContent =
            "خطا: " + error.message;

        setLessonStatus(
            "خطا در دریافت لیست درس‌ها.",
            "status-error"
        );

    }

}

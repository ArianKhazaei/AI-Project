const studentLessonsList =
    document.getElementById(
        "studentLessonsList"
    );

const studentLessonOutput =
    document.getElementById(
        "studentLessonOutput"
    );

let lessonAudioPollTimer = null;
let visualizerAnimationId = null;
let visualizerContext = null;
let visualizerAnalyser = null;
let visualizerData = null;


function stopAudioPolling() {

    if (lessonAudioPollTimer !== null) {
        clearInterval(
            lessonAudioPollTimer
        );

        lessonAudioPollTimer = null;
    }
}


function formatTime(seconds) {

    if (!Number.isFinite(seconds)) {
        return "00:00";
    }

    const totalSeconds =
        Math.max(0, Math.floor(seconds));

    const minutes =
        Math.floor(totalSeconds / 60);

    const remaining =
        totalSeconds % 60;

    return `${String(minutes).padStart(2, "0")}:${String(remaining).padStart(2, "0")}`;
}


function stopVisualizerAnimation() {

    if (visualizerAnimationId !== null) {
        cancelAnimationFrame(
            visualizerAnimationId
        );

        visualizerAnimationId = null;
    }
}


function updateBars(
    bars,
    values
) {

    bars.forEach(
        function (bar, index) {

            const value =
                values[index] || 0;

            const scale =
                Math.max(0.18, value / 255);

            bar.style.transform =
                `scaleY(${scale})`;
        }
    );
}


function attachAudioReactiveAnimation(
    audioElement,
    bars
) {

    try {

        if (visualizerContext === null) {

            const AudioContextClass =
                window.AudioContext ||
                window.webkitAudioContext;

            if (!AudioContextClass) {
                return;
            }

            visualizerContext =
                new AudioContextClass();
        }

        const source =
            visualizerContext.createMediaElementSource(
                audioElement
            );

        visualizerAnalyser =
            visualizerContext.createAnalyser();

        visualizerAnalyser.fftSize = 64;

        source.connect(
            visualizerAnalyser
        );

        visualizerAnalyser.connect(
            visualizerContext.destination
        );

        visualizerData =
            new Uint8Array(
                visualizerAnalyser.frequencyBinCount
            );

        function draw() {

            if (
                !visualizerAnalyser ||
                !visualizerData
            ) {
                return;
            }

            visualizerAnalyser.getByteFrequencyData(
                visualizerData
            );

            updateBars(
                bars,
                Array.from(
                    visualizerData
                ).slice(
                    0,
                    bars.length
                )
            );

            if (!audioElement.paused) {

                visualizerAnimationId =
                    requestAnimationFrame(
                        draw
                    );
            }
        }

        audioElement.addEventListener(
            "play",
            async function () {

                bars.forEach(
                    function (bar) {
                        bar.classList.add(
                            "active"
                        );
                    }
                );

                if (
                    visualizerContext &&
                    visualizerContext.state ===
                        "suspended"
                ) {

                    await visualizerContext.resume();
                }

                stopVisualizerAnimation();

                draw();
            }
        );

        function stopBars() {

            bars.forEach(
                function (bar) {

                    bar.classList.remove(
                        "active"
                    );

                    bar.style.transform =
                        "scaleY(0.18)";
                }
            );

            stopVisualizerAnimation();
        }

        audioElement.addEventListener(
            "pause",
            stopBars
        );

        audioElement.addEventListener(
            "ended",
            stopBars
        );

        audioElement.addEventListener(
            "error",
            stopBars
        );

    }

    catch (error) {

        console.error(
            "خطا در فعال‌سازی Audio Reactive Animation:",
            error
        );
    }
}


function createCompactAudioPlayer(
    audioUrl,
    audioStatusElement
) {

    const player =
        document.createElement("div");

    player.className =
        "audio-player";

    const playButton =
        document.createElement("button");

    playButton.type = "button";

    playButton.className =
        "audio-play-button";

    playButton.textContent =
        "Play";

    playButton.disabled = true;

    const progress =
        document.createElement("input");

    progress.type = "range";
    progress.min = "0";
    progress.max = "100";
    progress.step = "0.1";
    progress.value = "0";

    progress.className =
        "audio-progress";

    const timeElement =
        document.createElement("span");

    timeElement.className =
        "audio-time";

    timeElement.textContent =
        "00:00 / 00:00";

    const bars =
        Array.from(
            { length: 14 },
            function () {

                const bar =
                    document.createElement(
                        "span"
                    );

                bar.className =
                    "audio-bar";

                return bar;
            }
        );

    const barsContainer =
        document.createElement("div");

    barsContainer.className =
        "audio-bars";

    bars.forEach(
        function (bar) {
            barsContainer.appendChild(
                bar
            );
        }
    );

    const hiddenAudio =
        document.createElement("audio");

    hiddenAudio.crossOrigin =
        "anonymous";

    hiddenAudio.preload =
        "metadata";

    hiddenAudio.muted =
        false;

    hiddenAudio.volume =
        1;

    playButton.addEventListener(
        "click",
        async function () {

            try {

                if (hiddenAudio.paused) {

                    await hiddenAudio.play();

                    playButton.textContent =
                        "Pause";
                }

                else {

                    hiddenAudio.pause();

                    playButton.textContent =
                        "Play";
                }

            }

            catch (error) {

                console.error(
                    "خطا در پخش Audio:",
                    error
                );

                updateStatus(
                    audioStatusElement,
                    "پخش صدا توسط مرورگر محدود شد. دوباره تلاش کنید.",
                    "error"
                );
            }
        }
    );

    hiddenAudio.addEventListener(
        "loadedmetadata",
        function () {

            playButton.disabled =
                false;

            timeElement.textContent =
                `${formatTime(hiddenAudio.currentTime)} / ${formatTime(hiddenAudio.duration)}`;

            updateStatus(
                audioStatusElement,
                "فایل صوتی آماده پخش است.",
                "success"
            );
        }
    );

    hiddenAudio.addEventListener(
        "timeupdate",
        function () {

            const duration =
                hiddenAudio.duration || 0;

            const current =
                hiddenAudio.currentTime || 0;

            if (duration > 0) {

                progress.value =
                    String(
                        (current / duration) * 100
                    );
            }

            timeElement.textContent =
                `${formatTime(current)} / ${formatTime(duration)}`;
        }
    );

    hiddenAudio.addEventListener(
        "ended",
        function () {

            playButton.textContent =
                "Play";

            progress.value =
                "0";
        }
    );

    hiddenAudio.addEventListener(
        "pause",
        function () {

            if (hiddenAudio.ended) {
                return;
            }

            playButton.textContent =
                "Play";
        }
    );

    hiddenAudio.addEventListener(
        "error",
        function () {

            updateStatus(
                audioStatusElement,
                "خطا در بارگذاری فایل صوتی.",
                "error"
            );
        }
    );

    progress.addEventListener(
        "input",
        function () {

            const duration =
                hiddenAudio.duration || 0;

            if (duration <= 0) {
                return;
            }

            hiddenAudio.currentTime =
                (
                    Number(progress.value) /
                    100
                ) * duration;
        }
    );

    player.appendChild(
        playButton
    );

    player.appendChild(
        progress
    );

    player.appendChild(
        timeElement
    );

    player.appendChild(
        barsContainer
    );

    player.appendChild(
        hiddenAudio
    );

    attachAudioReactiveAnimation(
        hiddenAudio,
        bars
    );

    hiddenAudio.src =
        `${audioUrl}?t=${Date.now()}`;

    hiddenAudio.load();

    return player;
}


function createAttemptElement(
    attempt,
    index
) {

    const attemptSection =
        document.createElement("div");

    attemptSection.className =
        "lesson-output-section lesson-attempt";

    const title =
        document.createElement("h4");

    title.textContent =
        `تلاش ${index + 1}`;

    attemptSection.appendChild(
        title
    );

    const responseLabel =
        document.createElement("div");

    responseLabel.className =
        "lesson-output-attempt";

    responseLabel.textContent =
        "پاسخ Ava";

    attemptSection.appendChild(
        responseLabel
    );

    const responseText =
        document.createElement("p");

    responseText.className =
        "lesson-output-text";

    responseText.textContent =
        attempt.response ||
        attempt.text_response ||
        "پاسخ متنی موجود نیست.";

    attemptSection.appendChild(
        responseText
    );

    if (attempt.audio) {

        const audioLabel =
            document.createElement("div");

        audioLabel.className =
            "lesson-output-attempt";

        audioLabel.textContent =
            "صوت Ava";

        attemptSection.appendChild(
            audioLabel
        );

        const audioStatus =
            document.createElement("div");

        audioStatus.className =
            "lesson-output-attempt";

        audioStatus.textContent =
            "در حال آماده‌سازی فایل صوتی...";

        attemptSection.appendChild(
            audioStatus
        );

        const audioUrl =
            `${API_URL}${attempt.audio}`;

        attemptSection.appendChild(
            createCompactAudioPlayer(
                audioUrl,
                audioStatus
            )
        );
    }

    return attemptSection;
}


function renderLessonDetails(
    lesson
) {

    if (!studentLessonOutput) {
        return;
    }

    stopAudioPolling();
    stopVisualizerAnimation();

    studentLessonOutput.innerHTML =
        "";

    const title =
        document.createElement("h3");

    title.textContent =
        `درس: ${lesson.name}`;

    studentLessonOutput.appendChild(
        title
    );

    const attempts =
        Array.isArray(lesson.attempts)
            ? lesson.attempts
            : [];

    if (attempts.length > 0) {

        attempts.forEach(
            function (attempt, index) {

                studentLessonOutput.appendChild(
                    createAttemptElement(
                        attempt,
                        index
                    )
                );
            }
        );

    }

    else {

        const emptyAttempts =
            document.createElement("div");

        emptyAttempts.className =
            "empty-state";

        emptyAttempts.textContent =
            "هنوز تلاشی برای این درس ثبت نشده است.";

        studentLessonOutput.appendChild(
            emptyAttempts
        );
    }

    const newAttemptSection =
        document.createElement("div");

    newAttemptSection.className =
        "lesson-output-section";

    const newAttemptButton =
        document.createElement("button");

    newAttemptButton.type =
        "button";

    newAttemptButton.className =
        "start-lesson-button";

    newAttemptButton.innerHTML =
        '<span class="start-lesson-icon" aria-hidden="true"></span>' +
        '<span>تلاش جدید</span>';

    newAttemptButton.addEventListener(
        "click",
        function () {

            startLesson(
                lesson,
                newAttemptButton
            );
        }
    );

    newAttemptSection.appendChild(
        newAttemptButton
    );

    studentLessonOutput.appendChild(
        newAttemptSection
    );
}


function renderNewAttempt(
    result,
    lesson
) {

    if (!studentLessonOutput) {
        return;
    }

    const attempts =
        Array.isArray(lesson.attempts)
            ? lesson.attempts.slice()
            : [];

    attempts.push({
        attempt_number:
            result.attempt_number,

        response:
            result.response,

        audio:
            result.audio,

        status:
            "completed"
    });

    lesson.attempts =
        attempts;

    renderLessonDetails(
        lesson
    );

    if (result.note_url) {

        const noteSection =
            document.createElement("div");

        noteSection.className =
            "lesson-output-section";

        const noteLabel =
            document.createElement("h4");

        noteLabel.textContent =
            "نوت PDF";

        const noteText =
            document.createElement("p");

        noteText.className =
            "lesson-output-text";

        noteText.textContent =
            "نوت PDF این درس:";

        const noteViewer =
            document.createElement("iframe");

        noteViewer.className =
            "lesson-pdf-viewer";

        noteViewer.src =
            `${API_URL}${result.note_url}`;

        noteViewer.title =
            "نوت PDF درس";

        noteSection.appendChild(
            noteLabel
        );

        noteSection.appendChild(
            noteText
        );

        noteSection.appendChild(
            noteViewer
        );

        studentLessonOutput.appendChild(
            noteSection
        );
    }
}


async function startLesson(
    lesson,
    buttonElement
) {

    if (!currentUser) {
        return;
    }

    stopAudioPolling();
    stopVisualizerAnimation();

    setLoadingContent(
        studentLessonOutput,
        `در حال شروع تلاش جدید برای درس «${lesson.name}»...`
    );

    buttonElement.disabled =
        true;

    try {

        const response =
            await fetch(
                `${API_URL}/student/lessons/${currentUser.id}/${lesson.id}/start`,
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "شروع درس ناموفق بود."
            );
        }

        renderNewAttempt(
            data,
            lesson
        );

    }

    catch (error) {

        console.error(
            "خطا در شروع درس:",
            error
        );

        updateStatus(
            studentLessonOutput,
            "خطا در شروع درس: " +
                error.message,
            "error"
        );
    }

    finally {

        buttonElement.disabled =
            false;
    }
}


async function loadStudentLessons() {

    if (!studentLessonsList) {

        console.error(
            "عنصر studentLessonsList در HTML پیدا نشد."
        );

        return;
    }

    if (!currentUser) {

        console.error(
            "کاربر وارد نشده است."
        );

        return;
    }

    setLoadingContent(
        studentLessonsList,
        "در حال دریافت درس‌ها..."
    );

    try {

        const response =
            await fetch(
                `${API_URL}/student/lessons/${currentUser.id}`
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "دریافت درس‌ها ناموفق بود."
            );
        }

        studentLessonsList.innerHTML =
            "";

        if (
            !Array.isArray(data) ||
            data.length === 0
        ) {

            updateStatus(
                studentLessonsList,
                "هنوز درسی برای شما ایجاد نشده است."
            );

            return;
        }

        data.forEach(
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

                const openButton =
                    document.createElement(
                        "button"
                    );

                openButton.type =
                    "button";

                openButton.className =
                    "start-lesson-button";

                openButton.innerHTML =
                    '<span>مشاهده درس</span>';

                openButton.addEventListener(
                    "click",
                    function () {

                        renderLessonDetails(
                            lesson
                        );
                    }
                );

                lessonElement.appendChild(
                    titleElement
                );

                lessonElement.appendChild(
                    openButton
                );

                studentLessonsList.appendChild(
                    lessonElement
                );
            }
        );

    }

    catch (error) {

        console.error(
            "خطا در دریافت درس‌های هنرجو:",
            error
        );

        updateStatus(
            studentLessonsList,
            "خطا در دریافت درس‌ها: " +
                error.message,
            "error"
        );
    }
}

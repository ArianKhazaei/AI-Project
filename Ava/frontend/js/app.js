const API_URL = "http://127.0.0.1:8000";

let currentUser = null;


const loginPanel =
    document.getElementById("loginPanel");

const adminPanel =
    document.getElementById("adminPanel");

const teacherPanel =
    document.getElementById("teacherPanel");

const studentPanel =
    document.getElementById("studentPanel");


function updateStatus(
    element,
    message,
    state = "idle"
) {

    if (!element) {
        return;
    }

    element.classList.remove(
        "status-inline",
        "status-loading",
        "status-success",
        "status-error"
    );

    if (state === "loading") {

        element.classList.add(
            "status-inline",
            "status-loading"
        );

        element.innerHTML =
            '<span class="spinner" aria-hidden="true"></span>' +
            `<span>${message}</span>`;

        return;
    }

    element.textContent = message;

    if (state === "success") {
        element.classList.add("status-success");
    }

    if (state === "error") {
        element.classList.add("status-error");
    }
}


function setLoadingContent(
    element,
    message
) {

    if (!element) {
        return;
    }

    element.innerHTML =
        '<div class="status-inline status-loading">' +
        '<span class="spinner" aria-hidden="true"></span>' +
        `<span>${message}</span>` +
        "</div>";
}



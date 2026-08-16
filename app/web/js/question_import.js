let bridge = null;

let currentPage = 0;
let pageCount = 0;
let zoom = 1.0;
let documentType = "pdf";
let documentMimeType = "image/png";
let extractionInProgress = false;

let documentLoaded = false;

const openButton =
    document.getElementById("openButton");

const previousButton =
    document.getElementById("previousButton");

const nextButton =
    document.getElementById("nextButton");

const zoomOutButton =
    document.getElementById("zoomOutButton");

const zoomInButton =
    document.getElementById("zoomInButton");

const resetButton =
    document.getElementById("resetButton");

const extractButton =
    document.getElementById("extractButton");

const importYearInput =
    document.getElementById("importYearInput");

const importSubjectInput =
    document.getElementById("importSubjectInput");

const sourceName =
    document.getElementById("sourceName");

window.selectedDiagramQuestion = null;

const pageCountElement =
    document.getElementById("pageCount");

const pageInfo =
    document.getElementById("pageInfo");

const pages =
    document.getElementById("pages");

const documentArea =
    document.getElementById("documentArea");

const zoomLabel =
    document.getElementById("zoomLabel");

const status =
    document.getElementById("status");

const reviewContent =
    document.getElementById("reviewContent");

if (importYearInput) {
    importYearInput.value =
        String(
            new Date().getFullYear()
        );
}

if (importSubjectInput) {
    importSubjectInput.value =
        "Imported Questions";
}

function escapeHtml(value = "") {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getMimeTypeFromFilename(name = "") {

    const normalized =
        String(name).toLowerCase();

    if (normalized.endsWith(".jpg") || normalized.endsWith(".jpeg")) {
        return "image/jpeg";
    }

    if (normalized.endsWith(".webp")) {
        return "image/webp";
    }

    return "image/png";
}

function resolveImportImagePath(path = "") {

    const normalized =
        String(path)
            .trim()
            .replace(/\\/g, "/");

    if (!normalized) {
        return "";
    }

    if (/^(data:|https?:|file:|qrc:)/i.test(normalized)) {
        return normalized;
    }

    return encodeURI(
        `../../${normalized.replace(/^\/+/, "")}`
    );
}

function clearSelectionOverlay() {

    if (selection) {
        selection.remove();
        selection = null;
    }
}

function renderReviewEmptyState(
    title = "Nothing to review yet",
    message = "Open a question paper and run OCR/question extraction."
) {

    reviewContent.innerHTML = `
        <div class="review-empty">

            <div class="review-empty-icon">
                ✓
            </div>

            <h3>
                ${escapeHtml(title)}
            </h3>

            <p>
                ${escapeHtml(message)}
            </p>

        </div>
    `;
}

function getImportSettings() {

    const year =
        Number.parseInt(
            importYearInput?.value || "",
            10
        );

    const subject =
        (importSubjectInput?.value || "")
            .trim();

    if (
        !Number.isInteger(year) ||
        year < 1900 ||
        year > 2100
    ) {

        showImportToast(
            "Enter a valid exam year before running OCR.",
            "error"
        );

        importYearInput?.focus();
        return null;
    }

    if (!subject) {

        showImportToast(
            "Enter a subject name before running OCR.",
            "error"
        );

        importSubjectInput?.focus();
        return null;
    }

    return {
        year,
        subject,
    };
}

function persistDiagramSelection(
    questionNumber,
    x,
    y,
    width,
    height
) {

    bridge.save_diagram(
        String(questionNumber),
        Math.round(x),
        Math.round(y),
        Math.round(width),
        Math.round(height),

        function(response) {

            const result =
                JSON.parse(
                    response
                );

            if (!result.success) {

                showImportToast(
                    result.error,
                    "error"
                );

                return;
            }

            window.selectedDiagramQuestion =
                null;

            clearSelectionOverlay();

            showImportToast(
                `Diagram attached to Question ${result.question_number}.`,
                "success"
            );

            refreshImportReview();
        }
    );
}


/* ============================================================
   WEB CHANNEL
============================================================ */

new QWebChannel(
    qt.webChannelTransport,
    function(channel) {

        bridge =
            channel.objects.questionImportBridge;

        if (!bridge) {

            setStatus(
                "Question import bridge unavailable."
            );

            return;
        }

        setStatus(
            "Ready"
        );

        openButton.disabled = false;

        console.log(
            "QuestionImportBridge connected."
        );
    }
);


/* ============================================================
   OPEN
============================================================ */

openButton.addEventListener(
    "click",
    openQuestionPaper
);


function openQuestionPaper() {

    if (!bridge) {

        setStatus(
            "Question import bridge is not connected."
        );

        return;
    }

    bridge.open_question_paper(
        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {

                setStatus(
                    result.error
                );

                return;
            }

            if (result.cancelled) {
                return;
            }

            loadDocument(
                result
            );
        }
    );
}


/* ============================================================
   LOAD DOCUMENT
============================================================ */

function loadDocument(data) {

    documentLoaded = true;
    documentType =
        data.type || "pdf";
    documentMimeType =
        documentType === "pdf" ?
            "image/png" :
            getMimeTypeFromFilename(
                data.name
            );

    currentPage = 0;

    pageCount =
        data.page_count;

    sourceName.textContent =
        data.name;

    pageCountElement.textContent =
        `${pageCount} page${pageCount === 1 ? "" : "s"}`;

    previousButton.disabled =
        pageCount <= 1;

    nextButton.disabled =
        pageCount <= 1;

    zoomOutButton.disabled =
        false;

    zoomInButton.disabled =
        false;

    extractButton.disabled =
        false;

    resetButton.disabled =
        false;

    buildThumbnails();

    loadPage(
        currentPage
    );

    setStatus(
        "Document loaded. Extracting questions..."
    );

    setTimeout(
        triggerAutoExtraction,
        300
    );
}


/* ============================================================
   THUMBNAILS
============================================================ */

function buildThumbnails() {

    pages.innerHTML = "";

    for (
        let i = 0;
        i < pageCount;
        i++
    ) {

        const wrapper =
            document.createElement(
                "div"
            );

        wrapper.className =
            "page-thumbnail";

        wrapper.dataset.page =
            i;

        wrapper.innerHTML = `
            <img
                alt="Page ${i + 1}"
            >
            <div class="page-label">
                Page ${i + 1}
            </div>
        `;

        wrapper.addEventListener(
            "click",
            () => {

                loadPage(i);

            }
        );

        pages.appendChild(
            wrapper
        );

        if (documentType === "image") {

            wrapper.classList.add(
                "active"
            );

            bridge.get_page(
                0,
                function(response) {

                    const result =
                        JSON.parse(response);

                    if (!result.success) {
                        return;
                    }

                    const image =
                        wrapper.querySelector(
                            "img"
                        );

                    image.src =
                        `data:${documentMimeType};base64,${result.image}`;
                }
            );

            continue;
        }

        bridge.get_thumbnail(
            i,
            function(response) {

                const result =
                    JSON.parse(response);

                if (!result.success) {
                    return;
                }

                const image =
                    wrapper.querySelector(
                        "img"
                    );

                image.src =
                    "data:image/png;base64," +
                    result.image;
            }
        );
    }
}


/* ============================================================
   PAGE
============================================================ */

function loadPage(page) {

    if (
        !documentLoaded ||
        page < 0 ||
        page >= pageCount
    ) {
        return;
    }

    bridge.get_page(
        page,
        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {

                setStatus(
                    result.error
                );

                return;
            }

            currentPage =
                result.page;

            renderPage(
                result.image
            );

            updatePageControls();

            updateActiveThumbnail();
        }
    );
}


/* ============================================================
   RENDER PAGE
============================================================ */

function renderPage(base64) {

    documentArea.innerHTML = "";

    const img =
        document.createElement(
            "img"
        );

    img.className =
        "document-page";

    img.src =
        `data:${documentMimeType};base64,${base64}`;

    documentArea.appendChild(
        img
    );

    enableCropSelection(
        img
    );
}


/* ============================================================
   PAGE CONTROLS
============================================================ */

previousButton.addEventListener(
    "click",
    previousPage
);

nextButton.addEventListener(
    "click",
    nextPage
);


function previousPage() {

    if (currentPage > 0) {

        loadPage(
            currentPage - 1
        );
    }
}


function nextPage() {

    if (
        currentPage <
        pageCount - 1
    ) {

        loadPage(
            currentPage + 1
        );
    }
}


/* ============================================================
   UPDATE CONTROLS
============================================================ */

function updatePageControls() {

    pageInfo.textContent =
        `Page ${currentPage + 1} of ${pageCount}`;

    previousButton.disabled =
        currentPage <= 0;

    nextButton.disabled =
        currentPage >= pageCount - 1;

    zoomLabel.textContent =
        `${Math.round(zoom * 100)}%`;
}


function updateActiveThumbnail() {

    document
        .querySelectorAll(
            ".page-thumbnail"
        )
        .forEach(
            element => {

                element.classList.toggle(
                    "active",
                    Number(
                        element.dataset.page
                    ) === currentPage
                );

            }
        );
}


/* ============================================================
   ZOOM
============================================================ */

zoomInButton.addEventListener(
    "click",
    () => {

        zoom = Math.min(
            3,
            zoom + 0.25
        );

        applyZoom();
    }
);


zoomOutButton.addEventListener(
    "click",
    () => {

        zoom = Math.max(
            0.5,
            zoom - 0.25
        );

        applyZoom();
    }
);


function applyZoom() {

    bridge.set_zoom(
        zoom,
        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {
                return;
            }

            renderPage(
                result.image
            );

            updatePageControls();
        }
    );
}


/* ============================================================
   CROP / SELECTION
============================================================ */

let cropMode = false;
let cropStartX = 0;
let cropStartY = 0;

let selection = null;


function enableCropSelection(img) {

    img.style.cursor =
        "crosshair";

    img.addEventListener(
        "mousedown",
        startSelection
    );

    img.addEventListener(
        "mousemove",
        moveSelection
    );

    img.addEventListener(
        "mouseup",
        finishSelection
    );
}


function startSelection(event) {

    cropMode = true;

    const rect =
        event.currentTarget.getBoundingClientRect();

    cropStartX =
        event.clientX - rect.left;

    cropStartY =
        event.clientY - rect.top;

    if (selection) {
        selection.remove();
    }

    selection =
        document.createElement(
            "div"
        );

    selection.style.position =
        "absolute";

    selection.style.border =
        "2px solid #2563eb";

    selection.style.background =
        "rgba(37, 99, 235, 0.12)";

    selection.style.pointerEvents =
        "none";

    documentArea.appendChild(
        selection
    );
}


function moveSelection(event) {

    if (!cropMode) {
        return;
    }

    const img =
        event.currentTarget;

    const rect =
        img.getBoundingClientRect();

    const currentX =
        event.clientX - rect.left;

    const currentY =
        event.clientY - rect.top;

    const x =
        Math.min(
            cropStartX,
            currentX
        );

    const y =
        Math.min(
            cropStartY,
            currentY
        );

    const width =
        Math.abs(
            currentX - cropStartX
        );

    const height =
        Math.abs(
            currentY - cropStartY
        );

    selection.style.left =
        `${img.offsetLeft + x}px`;

    selection.style.top =
        `${img.offsetTop + y}px`;

    selection.style.width =
        `${width}px`;

    selection.style.height =
        `${height}px`;
}


function finishSelection(event) {

    if (!cropMode) {
        return;
    }

    cropMode = false;

    const img =
        event.currentTarget;

    const rect =
        img.getBoundingClientRect();

    const endX =
        event.clientX - rect.left;

    const endY =
        event.clientY - rect.top;

    const x =
        Math.min(
            cropStartX,
            endX
        );

    const y =
        Math.min(
            cropStartY,
            endY
        );

    const width =
        Math.abs(
            endX - cropStartX
        );

    const height =
        Math.abs(
            endY - cropStartY
        );

    if (
        width < 10 ||
        height < 10
    ) {

        clearSelectionOverlay();

        return;
    }

    showCropReview(
        x,
        y,
        width,
        height
    );
}


/* ============================================================
   CROP REVIEW
============================================================ */

function showCropReview(
    x,
    y,
    width,
    height
) {

    setStatus(
        "Diagram selected."
    );

    bridge.crop_region(
        Math.round(x),
        Math.round(y),
        Math.round(width),
        Math.round(height),

        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {

                setStatus(
                    result.error
                );

                return;
            }

            reviewContent.innerHTML = `

                <div class="info-card">

                    <div class="info-label">
                        Diagram Selection
                    </div>

                    <img
                        src="data:image/png;base64,${result.image}"
                        style="
                            width:100%;
                            border-radius:8px;
                            border:1px solid #e5e7eb;
                            margin-bottom:12px;
                        "
                    >

                    <button
                        class="primary"
                        id="saveDiagramButton"
                        style="width:100%;"
                    >
                        Save Diagram
                    </button>

                    <button
                        class="secondary"
                        id="cancelCropButton"
                        style="
                            width:100%;
                            margin-top:8px;
                        "
                    >
                        Cancel
                    </button>

                </div>
            `;

            document
                .getElementById(
                    "saveDiagramButton"
                )
                .addEventListener(
                    "click",
                    () => {

                        saveDiagram(
                            x,
                            y,
                            width,
                            height
                        );

                    }
                );

            document
                .getElementById(
                    "cancelCropButton"
                )
                .addEventListener(
                    "click",
                    clearReview
                );
        }
    );
}


/* ============================================================
   SAVE DIAGRAM
============================================================ */
function saveDiagram(
    x,
    y,
    width,
    height
) {

    const selectedQuestion =
        Number.parseInt(
            window.selectedDiagramQuestion,
            10
        );

    if (
        Number.isInteger(
            selectedQuestion
        ) &&
        selectedQuestion > 0
    ) {

        persistDiagramSelection(
            selectedQuestion,
            x,
            y,
            width,
            height
        );

        return;
    }

    showQuestionNumberInputModal(
        x,
        y,
        width,
        height
    );
}

function showQuestionNumberInputModal(
    x,
    y,
    width,
    height
) {

    const modal =
        document.getElementById(
            "questionNumberModal"
        );

    const input =
        document.getElementById(
            "questionNumberInput"
        );

    const error =
        document.getElementById(
            "questionNumberError"
        );

    const closeButton =
        document.getElementById(
            "closeQuestionNumberModal"
        );

    const cancelButton =
        document.getElementById(
            "cancelQuestionNumber"
        );

    const confirmButton =
        document.getElementById(
            "confirmQuestionNumber"
        );

    if (!modal || !input || !error || !closeButton || !cancelButton || !confirmButton) {
        return;
    }

    input.value =
        window.selectedDiagramQuestion ?
            String(
                window.selectedDiagramQuestion
            ) :
            "";
    error.classList.add("hidden");
    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");
    input.focus();

    const closeModal = () => {
        modal.classList.add("hidden");
        modal.setAttribute("aria-hidden", "true");
    };

    closeButton.onclick = closeModal;
    cancelButton.onclick = closeModal;

    const backdrop =
        modal.querySelector(
            ".modal-backdrop"
        );

    if (backdrop) {
        backdrop.onclick = closeModal;
    }

    confirmButton.onclick = () => {

        const questionNumber =
            parseInt(
                input.value,
                10
            );

        if (
            !questionNumber ||
            questionNumber <= 0
        ) {

            error.classList.remove("hidden");
            input.focus();
            return;
        }

        closeModal();

        persistDiagramSelection(
            questionNumber,
            x,
            y,
            width,
            height
        );
    };
}

/* ============================================================
   RESET
============================================================ */

resetButton.addEventListener(
    "click",
    resetDocument
);


function resetDocument() {

    if (!bridge) {
        return;
    }

    bridge.reset_document(
        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {

                setStatus(
                    result.error
                );

                return;
            }

            documentLoaded =
                false;

            currentPage = 0;
            pageCount = 0;
            zoom = 1.0;
            documentType = "pdf";
            documentMimeType = "image/png";
            extractionInProgress = false;
            window.selectedDiagramQuestion = null;
            window.importReviewQuestions = [];

            sourceName.textContent =
                "No document loaded";

            pageCountElement.textContent =
                "—";

            pageInfo.textContent =
                "Page —";

            zoomLabel.textContent =
                "100%";

            pages.innerHTML = `
                <div class="empty-state">
                    Open a scanned
                    question paper.
                </div>
            `;

            documentArea.innerHTML = `
                <div class="empty-state">

                    <div>

                        <h2>
                            No question paper loaded
                        </h2>

                        <p>
                            Select a PDF or scanned image
                            to begin reviewing questions.
                        </p>

                    </div>

                </div>
            `;

            reviewContent.innerHTML = `
                <div class="empty-state">

                    <div>

                        The question review
                        panel will appear here.

                        <br><br>

                        OCR and question extraction
                        will be added next.

                    </div>

                </div>
            `;

            previousButton.disabled = true;
            nextButton.disabled = true;
            zoomOutButton.disabled = true;
            zoomInButton.disabled = true;
            extractButton.disabled = true;
            resetButton.disabled = true;

            clearSelectionOverlay();

            renderReviewEmptyState();

            setStatus(
                "Ready"
            );
        }
    );
}


/* ============================================================
   REVIEW
============================================================ */

function clearReview() {

    window.selectedDiagramQuestion =
        null;

    clearSelectionOverlay();

    renderReviewEmptyState(
        "Nothing to review yet",
        "Select a diagram region or run OCR/question extraction."
    );
}



/* ============================================================
   IMPORT REVIEW
============================================================ */

function renderImportReview(data) {

    if (!data || !data.questions) {
        return;
    }

    const questions = data.questions;

    if (importYearInput) {
        importYearInput.value =
            String(
                data.year ||
                window.importReviewYear ||
                importYearInput.value
            );
    }

    if (importSubjectInput) {
        importSubjectInput.value =
            data.subject ||
            window.importReviewSubject ||
            importSubjectInput.value;
    }

    reviewContent.innerHTML = `
        <div class="import-review">

            <div class="review-header">

                <div>
                    <div class="info-label">
                        IMPORT REVIEW
                    </div>

                    <div class="review-subtitle">
                        Review and edit extracted questions
                        before saving them to the question bank.
                    </div>
                </div>

                <button
                    class="btn btn-success"
                    id="approveImportButton"
                >
                    Approve & Save
                </button>

            </div>

            <div class="review-summary">

                <div class="summary-chip">
                    ${questions.length} question${questions.length === 1 ? "" : "s"}
                </div>

                <div class="summary-chip">
                    ${escapeHtml(importSubjectInput?.value || "Imported Questions")}
                </div>

                <div class="summary-chip">
                    ${escapeHtml(String(importYearInput?.value || ""))}
                </div>

            </div>

            <div id="questionReviewList">
            </div>

        </div>
    `;

    const container =
        document.getElementById(
            "questionReviewList"
        );

    questions.forEach(
        (question, index) => {

            container.appendChild(
                createQuestionReview(
                    question,
                    index
                )
            );
        }
    );

    document
        .getElementById(
            "approveImportButton"
        )
        .addEventListener(
            "click",
            approveImport
        );
}


// CREATE QUESTION REVIEW CARD
// 

function createQuestionReview(question, index) {
    const card = document.createElement("div");
    card.className = "question-review-card";
    card.dataset.index = index;

    card.innerHTML = `
        <div class="question-review-header">
            <strong>Question ${escapeHtml(String(question.number))}</strong>
            <div class="question-actions">
                <button type="button" class="btn btn-sm btn-edit" data-index="${index}">Edit</button>
                <button type="button" class="btn btn-sm btn-discard" data-index="${index}">Discard</button>
                <button type="button" class="btn btn-sm btn-approve" data-index="${index}">Approve</button>
            </div>
        </div>
        
        <div class="question-meta-grid">
            <label class="field-stack">
                <span>Question Number</span>
                <input type="number" min="1" class="question-number-input" 
                       value="${escapeHtml(String(question.number || index + 1))}">
            </label>
            <div class="question-source-meta">
                <span>${escapeHtml(question.source_reference || "Imported file")}</span>
                <strong>${question.source_page ? `Page ${escapeHtml(String(question.source_page))}` : "Page not set"}</strong>
            </div>
        </div>

        <label>Question text</label>
        <textarea class="question-text" rows="4">${escapeHtml(question.text || "")}</textarea>

        <div class="options-review">
            ${renderOptions(question.options || [], index)}
        </div>

        <div class="diagram-review">
            <div class="diagram-title">Diagram</div>
            <div class="diagram-list">
                ${renderQuestionImages(question.images || [])}
            </div>
            <button type="button" class="secondary crop-question-diagram">Add Diagram</button>
        </div>
    `;

    // Add event listeners for action buttons
    card.querySelector('.btn-edit').addEventListener('click', () => toggleEditMode(card));
    card.querySelector('.btn-discard').addEventListener('click', () => discardQuestion(index));
    card.querySelector('.btn-approve').addEventListener('click', () => approveQuestion(index));
    card.querySelector('.crop-question-diagram').addEventListener('click', () => {
        selectQuestionForDiagram(question.number);
    });

    return card;
}

// Add these new functions
function toggleEditMode(card) {
    const isEditing = card.classList.toggle('editing');
    const inputs = card.querySelectorAll('input, textarea');
    inputs.forEach(input => input.disabled = !isEditing);
}

function discardQuestion(index) {
    if (confirm('Are you sure you want to discard this question?')) {
        window.importReviewQuestions.splice(index, 1);
        refreshImportReview();
    }
}

function approveQuestion(index) {
    const question = window.importReviewQuestions[index];
    // Mark as approved and visually indicate
    const card = document.querySelector(`.question-review-card[data-index="${index}"]`);
    card.classList.add('approved');


}

// ============================================================
//   render options for a question
// ============================================================

function renderOptions(
    options,
    questionIndex = 0
) {

    return options.map(
        (option, index) => {

            const label =
                option.label ||
                String.fromCharCode(
                    65 + index
                );

            const checked =
                option.is_correct ?
                    "checked" :
                    "";

            return `

                <div class="option-review">

                    <div class="option-label">
                        ${label}
                    </div>

                    <textarea
                        class="option-text"
                        data-option-index="${index}"
                        rows="2"
                    >${escapeHtml(
                        option.text || ""
                    )}</textarea>

                    <label class="correct-option">

                        <input
                            type="radio"
                            name="correct-option-${questionIndex}"
                            ${checked}
                        >

                        Correct

                    </label>

                </div>

            `;
        }
    ).join("");
}


/* ============================================================
   render question images
============================================================ */
function renderQuestionImages(
    images
) {

    if (!images.length) {

        return `
            <div class="empty-diagram">
                No diagram attached.
            </div>
        `;
    }

    return images.map(
        image => `

            <div class="diagram-item">

                <img
                    src="${resolveImportImagePath(image.path)}"
                    alt="Question diagram"
                >

                <div class="diagram-item-meta">
                    ${image.page ? `Page ${escapeHtml(String(image.page))}` : "Attached diagram"}
                </div>

            </div>

        `
    ).join("");
}



/* ============================================================
// REFERESH IMPORT REVIEW
// ============================================================ */
function refreshImportReview() {

    if (!bridge || typeof bridge.get_review !== "function") {
        console.error("Bridge not available for get_review");
        renderReviewEmptyState("Bridge not available", "Question import bridge is not connected.");
        return;
    }

    bridge.get_review(
        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {
                return;
            }

            const review =
                result.review || {
                    subjects: [
                        {
                            name:
                                window.importReviewSubject ||
                                "Imported Questions",
                            questions:
                                window.importReviewQuestions || [],
                        }
                    ]
                };

            if (
                review.subjects &&
                review.subjects.length
            ) {

                window.importReviewYear =
                    review.year ||
                    window.importReviewYear;

                window.importReviewSubject =
                    review.subjects[0].name ||
                    window.importReviewSubject;


                const questions =
                    review.subjects[0].questions ||
                    [];

                if (questions.length) {
                    window.importReviewQuestions =
                        questions;

                    renderImportReview({
                        year:
                            review.year,
                        subject:
                            review.subjects[0].name,
                        questions
                    });

                    return;
                }
            }

            renderReviewEmptyState();
        }
    );
}


/* ============================================================
// COLLECT QUESTION REVIEW DATA
// ============================================================ */
function collectReviewData() {

    const cards =
        document.querySelectorAll(
            ".question-review-card"
        );

    const questions = [];

    cards.forEach(
        card => {

            const index =
                Number(
                    card.dataset.index
                );

            const original =
                (window.importReviewQuestions || [])[
                    index
                ] || {
                    number: index + 1,
                    text: "",
                    options: [],
                    images: [],
                    source_page: null,
                };

            const questionText =
                card.querySelector(
                    ".question-text"
                ).value.trim();

            const questionNumber =
                Number.parseInt(
                    card.querySelector(
                        ".question-number-input"
                    ).value,
                    10
                );

            const optionElements =
                card.querySelectorAll(
                    ".option-review"
                );

            const options = [];

            optionElements.forEach(
                optionElement => {

                    const optionIndex =
                        Number(
                            optionElement
                                .querySelector(
                                    ".option-text"
                                )
                                .dataset
                                .optionIndex
                        );

                    const originalOptions =
                        original.options || [];

                    const originalOption =
                        originalOptions[
                            optionIndex
                        ] || {
                            label:
                                String.fromCharCode(
                                    65 + optionIndex
                                ),
                        };

                    const text =
                        optionElement
                            .querySelector(
                                ".option-text"
                            )
                            .value
                            .trim();

                    const correct =
                        optionElement
                            .querySelector(
                                "input[type=radio]"
                            )
                            .checked;

                    if (!text) {
                        return;
                    }

                    options.push({
                        label:
                            originalOption.label,

                        text,

                        is_correct:
                            correct,
                    });
                }
            );

            questions.push({

                number:
                    Number.isInteger(
                        questionNumber
                    ) && questionNumber > 0 ?
                        questionNumber :
                        original.number,

                question_number:
                    Number.isInteger(
                        questionNumber
                    ) && questionNumber > 0 ?
                        questionNumber :
                        original.number,

                text:
                    questionText,

                options,

                images:
                    original.images || [],

                explanation:
                    original.explanation || null,

                source_reference:
                    original.source_reference || null,

                source_page:
                    original.source_page || null,
            });
        }
    );

    questions.sort(
        (left, right) =>
            left.number - right.number
    );

    const settings =
        getImportSettings();

    if (!settings) {
        return null;
    }

    return {
        year:
            settings.year,

        subjects: [
            {
                name:
                    settings.subject,

                questions,
            }
        ],
    };
}


/* ============================================================
   APPROVE IMPORT
=========================================================== */  

function approveImport() {

    const data =
        collectReviewData();

    if (!data) {
        return;
    }

    const questions =
        data.subjects[0].questions;

    if (!questions.length) {

        showImportToast(
            "There are no questions to save.",
            "error"
        );

        return;
    }

    for (const question of questions) {

        if (!question.text.trim()) {

            showImportToast(
                `Question ${question.number} has no text.`,
                "error"
            );

            return;
        }

        const filledOptions =
            question.options.filter(
                option =>
                    option.text.trim()
            );

        const correctCount =
            filledOptions.filter(
                option =>
                    option.is_correct
            ).length;

        if (filledOptions.length < 2) {

            showImportToast(
                `Question ${question.number} needs at least two filled options.`,
                "error"
            );

            return;
        }

        if (correctCount !== 1) {

            showImportToast(
                `Question ${question.number} must have exactly one correct answer among the filled options.`,
                "error"
            );

            return;
        }
    }

    bridge.save_review(
        JSON.stringify(data),

        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {

                showImportToast(
                    result.error,
                    "error"
                );

                return;
            }

            showImportToast(
                `${result.imported} questions saved successfully.`,
                "success"
            );

            setStatus(
                "Question import completed."
            );
        }
    );
}


/* ============================================================
// SHOW TOAST
// ============================================================ */

function showImportToast(
    message,
    type = "info"
) {

    let container =
        document.getElementById(
            "toastContainer"
        );

    if (!container) {

        container =
            document.createElement(
                "div"
            );

        container.id = "toastContainer";
        container.className =
            "toast-container";

        document.body.appendChild(
            container
        );
    }

    const toast =
        document.createElement(
            "div"
        );

    toast.className =
        `toast ${type}`;

    toast.textContent =
        message;

    container.appendChild(
        toast
    );

    setTimeout(
        () => {

            toast.remove();

        },
        3500
    );
}


/* ============================================================
//  EXTRACT QUESTION BUTTON
============================================================ */ 

function triggerAutoExtraction() {

    if (
        !bridge ||
        !documentLoaded ||
        extractionInProgress
    ) {
        return;
    }

    const settings =
        getImportSettings();

    if (!settings) {
        return;
    }

    extractionInProgress = true;
    extractButton.disabled = true;

    setStatus(
        "Running OCR and extracting questions..."
    );

    bridge.extract_questions(
        settings.year,
        settings.subject,

        function(response) {

            const result =
                JSON.parse(response);

            if (!result.success) {

                showImportToast(
                    result.error,
                    "error"
                );

                setStatus(
                    "Extraction failed. Please verify the document is readable."
                );

                extractionInProgress = false;
                extractButton.disabled = false;

                return;
            }

            window.importReviewYear =
                result.year;

            window.importReviewSubject =
                result.subject;

            window.importReviewQuestions =
                result.questions;

            renderImportReview({
                year:
                    result.year,

                subject:
                    result.subject,

                questions:
                    result.questions,
            });

            setStatus(
                `${result.questions.length} questions extracted.`
            );

            extractionInProgress = false;
            extractButton.disabled = false;
        }
    );
}

function extractQuestions() {
    triggerAutoExtraction();
}

extractButton.addEventListener(
    "click",
    triggerAutoExtraction
);

// Make selectQuestionForDiagram globally available
window.selectQuestionForDiagram = function(questionNumber) {

    window.selectedDiagramQuestion = questionNumber;

    showImportToast(
        `Select the diagram region for Question ${questionNumber}.`,
        "info"
    );

    setStatus(
        `Ready to crop diagram for Question ${questionNumber}.`
    );
};

// /* ============================================================
//    GIVING  QUESTION NUMBER FOR DIAGRAM
// ============================================================ */

// let selectedDiagramQuestion = null;


// function selectQuestionForDiagram(
//     questionNumber
// ) {

//     selectedDiagramQuestion =
//         questionNumber;

//     showQuestionNumberModal(
//         questionNumber
//     );
// }


// /* ============================================================
// //   MODAL FOR QUESTION NUMBER
// ============================================================ */

// function showQuestionNumberModal(
//     questionNumber
// ) {

//     const existing =
//         document.getElementById(
//             "questionNumberModal"
//         );

//     if (existing) {
//         existing.remove();
//     }

//     const modal =
//         document.createElement(
//             "div"
//         );

//     modal.id =
//         "questionNumberModal";

//     modal.className =
//         "import-modal-overlay";

//     modal.innerHTML = `

//         <div class="import-modal">

//             <div class="info-label">
//                 ATTACH DIAGRAM
//             </div>

//             <h3>
//                 Question ${questionNumber}
//             </h3>

//             <p>
//                 This diagram will be attached
//                 to Question ${questionNumber}.
//             </p>

//             <div class="modal-actions">

//                 <button
//                     type="button"
//                     class="secondary"
//                     id="cancelQuestionDiagram"
//                 >
//                     Cancel
//                 </button>

//                 <button
//                     type="button"
//                     class="primary"
//                     id="confirmQuestionDiagram"
//                 >
//                     Continue
//                 </button>

//             </div>

//         </div>

//     `;

//     document.body.appendChild(
//         modal
//     );

//     document
//         .getElementById(
//             "cancelQuestionDiagram"
//         )
//         .addEventListener(
//             "click",
//             () => modal.remove()
//         );

//     document
//         .getElementById(
//             "confirmQuestionDiagram"
//         )
//         .addEventListener(
//             "click",
//             () => {

//                 modal.remove();

//                 setStatus(
//                     `Crop the diagram for Question ${questionNumber}.`
//                 );

//             }
//         );
// }
/* ============================================================
   STATUS
============================================================ */

function setStatus(message) {

    status.textContent =
        message;
}

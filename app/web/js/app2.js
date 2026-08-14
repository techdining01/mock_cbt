document.addEventListener("alpine:init", () => {

    console.log("Alpine initialized.");

    Alpine.data("examApp", () => ({

        // =========================================================
        // APPLICATION STATE
        // =========================================================

        screen: "selection",

        loading: true,

        loadingMessage: "Loading examination years...",

        error: null,


        // =========================================================
        // DATABASE / SELECTION STATE
        // =========================================================

        years: [],

        subjects: [],

        selectedYear: null,

        selectedSubjectIds: [],

        studentName: "",

        durationMinutes: 120,

        subjectsLoading: false,

        creatingExam: false,


        // =========================================================
        // EXAM STATE
        // =========================================================

        exam: null,

        examId: null,

        subjectIndex: 0,

        questionIndex: 0,


        // =========================================================
        // CLOCK
        // =========================================================

        remainingSeconds: 0,

        timerInterval: null,

        clockSyncInterval: null,

        timeExpiredHandled: false,


        // =========================================================
        // TIMEOUT
        // =========================================================

        showTimeoutOverlay: false,

        timeoutCompleting: false,

        timeoutResultReady: false,


        // =========================================================
        // RESULT
        // =========================================================

        result: null,

        resultLoading: false,

        resultChart: null,


        // =========================================================
        // FINISH
        // =========================================================

        showFinishModal: false,

        finishingExam: false,


        // =========================================================
        // INITIALIZATION
        // =========================================================

        init() {

            console.log("examApp initialized.");

            this.waitForBridge();

        },


        // =========================================================
        // WAIT FOR QWEBCHANNEL
        // =========================================================

        waitForBridge() {

            if (
                window.examBridge &&
                typeof window.examBridge.get_years === "function"
            ) {

                console.log("examBridge is ready.");

                this.loadYears();

                return;
            }


            console.log("Waiting for examBridge...");


            setTimeout(() => {

                this.waitForBridge();

            }, 100);

        },


        // =========================================================
        // LOAD YEARS
        // =========================================================

        loadYears() {

            this.loading = true;

            this.loadingMessage =
                "Loading examination years...";

            this.error = null;


            if (
                !window.examBridge ||
                typeof window.examBridge.get_years !== "function"
            ) {

                this.setError(
                    "Python examination bridge is not available."
                );

                return;
            }


            window.examBridge.get_years(
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.setError(
                                data.error ||
                                "Unable to load examination years."
                            );

                            return;
                        }


                        this.years =
                            Array.isArray(data.years)
                                ? data.years
                                : [];


                        this.loading = false;

                        this.screen = "selection";


                        console.log(
                            "Available years:",
                            this.years
                        );

                    }
                    catch (error) {

                        console.error(
                            "Year response error:",
                            error
                        );

                        this.setError(
                            "Invalid response received while loading years."
                        );

                    }

                }
            );

        },


        // =========================================================
        // SELECT YEAR
        // =========================================================

        selectYear(year) {

            if (!year) {
                return;
            }


            this.selectedYear =
                Number(year);


            this.selectedSubjectIds = [];

            this.subjects = [];


            this.loadSubjectsForYear(
                this.selectedYear
            );

        },


        // =========================================================
        // LOAD SUBJECTS
        // =========================================================

        loadSubjectsForYear(year) {

            this.subjectsLoading = true;

            this.error = null;


            if (
                !window.examBridge ||
                typeof window.examBridge.get_subjects_for_year !== "function"
            ) {

                this.subjectsLoading = false;

                this.setError(
                    "Python examination bridge cannot load subjects."
                );

                return;
            }


            window.examBridge.get_subjects_for_year(
                Number(year),
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.subjectsLoading = false;

                            this.setError(
                                data.error ||
                                "Unable to load subjects."
                            );

                            return;
                        }


                        this.subjects =
                            Array.isArray(data.subjects)
                                ? data.subjects
                                : [];


                        this.subjects =
                            this.subjects.map(
                                (subject) => ({

                                    ...subject,

                                    question_count:
                                        Number(
                                            subject.question_count ??
                                            subject.count ??
                                            0
                                        ),

                                })
                            );


                        this.subjectsLoading = false;


                        console.log(
                            "Subjects for",
                            year,
                            this.subjects
                        );

                    }
                    catch (error) {

                        console.error(
                            "Subject response error:",
                            error
                        );

                        this.subjectsLoading = false;

                        this.setError(
                            "Invalid response received while loading subjects."
                        );

                    }

                }
            );

        },


        // =========================================================
        // SUBJECT SELECTION
        // =========================================================

        toggleSubject(subjectId) {

            const id =
                Number(subjectId);


            const index =
                this.selectedSubjectIds.indexOf(id);


            if (index === -1) {

                this.selectedSubjectIds.push(id);

            }
            else {

                this.selectedSubjectIds.splice(
                    index,
                    1
                );

            }

        },


        // =========================================================
        // SELECT ALL
        // =========================================================

        selectAllSubjects() {

            this.selectedSubjectIds =
                this.subjects.map(
                    subject =>
                        Number(subject.id)
                );

        },


        // =========================================================
        // CLEAR SUBJECTS
        // =========================================================

        clearSubjects() {

            this.selectedSubjectIds = [];

        },


        // =========================================================
        // SUBJECT SELECTED
        // =========================================================

        isSubjectSelected(subjectId) {

            return this.selectedSubjectIds.includes(
                Number(subjectId)
            );

        },


        // =========================================================
        // SELECTED SUBJECTS
        // =========================================================

        get selectedSubjects() {

            return this.subjects.filter(
                subject =>
                    this.selectedSubjectIds.includes(
                        Number(subject.id)
                    )
            );

        },


        // =========================================================
        // SELECTED QUESTION COUNT
        // =========================================================

        get selectedQuestionCount() {

            return this.selectedSubjects.reduce(
                (total, subject) => {

                    return (
                        total +
                        Number(
                            subject.question_count || 0
                        )
                    );

                },
                0
            );

        },


        // =========================================================
        // CREATE EXAM
        // =========================================================

        createExam() {

            if (this.creatingExam) {
                return;
            }


            if (!this.selectedYear) {

                this.setError(
                    "Please select an examination year."
                );

                return;
            }


            if (!this.selectedSubjectIds.length) {

                this.setError(
                    "Please select at least one subject."
                );

                return;
            }


            if (
                !Number.isInteger(
                    Number(this.durationMinutes)
                ) ||
                Number(this.durationMinutes) <= 0
            ) {

                this.setError(
                    "Exam duration must be greater than zero."
                );

                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.create_exam !== "function"
            ) {

                this.setError(
                    "The Python bridge does not currently expose create_exam()."
                );

                return;
            }


            this.creatingExam = true;

            this.error = null;


            const year =
                Number(this.selectedYear);


            const subjectIds =
                this.selectedSubjectIds.map(
                    id => Number(id)
                );


            const duration =
                Number(this.durationMinutes);


            const name =
                String(
                    this.studentName || ""
                ).trim();


            window.examBridge.create_exam(
                year,
                subjectIds,
                duration,
                name,
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.creatingExam = false;

                            this.setError(
                                data.error ||
                                "Unable to create examination."
                            );

                            return;
                        }


                        this.examId =
                            Number(data.exam_id);


                        if (!this.examId) {

                            this.creatingExam = false;

                            this.setError(
                                "The examination session was created without a valid ID."
                            );

                            return;
                        }


                        this.startExam();

                    }
                    catch (error) {

                        console.error(
                            "Create exam response error:",
                            error
                        );

                        this.creatingExam = false;

                        this.setError(
                            "Invalid response received while creating the examination."
                        );

                    }

                }
            );

        },


        // =========================================================
        // START EXAM
        // =========================================================

        startExam() {

            if (!this.examId) {

                this.creatingExam = false;

                this.setError(
                    "No examination session ID is available."
                );

                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.start_exam !== "function"
            ) {

                this.creatingExam = false;

                this.setError(
                    "The Python bridge does not currently expose start_exam()."
                );

                return;
            }


            window.examBridge.start_exam(
                this.examId,
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.creatingExam = false;

                            this.setError(
                                data.error ||
                                "Unable to start examination."
                            );

                            return;
                        }


                        this.loadExam();

                    }
                    catch (error) {

                        console.error(
                            "Start exam response error:",
                            error
                        );

                        this.creatingExam = false;

                        this.setError(
                            "Invalid response received while starting the examination."
                        );

                    }

                }
            );

        },


        // =========================================================
        // LOAD EXAM
        // =========================================================

        loadExam() {

            if (!this.examId) {

                this.creatingExam = false;

                this.setError(
                    "No examination session ID was supplied."
                );

                return;
            }


            this.loading = true;

            this.loadingMessage =
                "Loading examination questions...";

            this.error = null;


            if (
                !window.examBridge ||
                typeof window.examBridge.get_exam !== "function"
            ) {

                this.creatingExam = false;

                this.setError(
                    "Python examination bridge is not available."
                );

                return;
            }


            window.examBridge.get_exam(
                this.examId,
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.creatingExam = false;

                            this.setError(
                                data.error ||
                                "Unable to load examination."
                            );

                            return;
                        }


                        if (!data.exam) {

                            this.creatingExam = false;

                            this.setError(
                                "The examination response contained no exam data."
                            );

                            return;
                        }


                        this.exam =
                            data.exam;


                        this.remainingSeconds =
                            Number(
                                this.exam.remaining_seconds || 0
                            );


                        this.restorePosition();


                        this.screen =
                            "exam";


                        this.loading = false;

                        this.creatingExam = false;

                        this.timeExpiredHandled = false;


                        this.showTimeoutOverlay = false;

                        this.timeoutCompleting = false;

                        this.timeoutResultReady = false;


                        this.startDisplayTimer();

                    }
                    catch (error) {

                        console.error(
                            "Exam response error:",
                            error
                        );

                        this.creatingExam = false;

                        this.setError(
                            "Invalid response received from Python."
                        );

                    }

                }
            );

        },


        // =========================================================
        // RESTORE POSITION
        // =========================================================

        restorePosition() {

            if (
                !this.exam ||
                !Array.isArray(this.exam.subjects) ||
                !this.exam.subjects.length
            ) {

                this.subjectIndex = 0;

                this.questionIndex = 0;

                return;
            }


            for (
                let i = 0;
                i < this.exam.subjects.length;
                i++
            ) {

                const subject =
                    this.exam.subjects[i];


                const position =
                    Number(
                        subject.current_question_position || 0
                    );


                if (
                    position > 0 &&
                    Array.isArray(subject.questions) &&
                    position < subject.questions.length
                ) {

                    this.subjectIndex = i;

                    this.questionIndex = position;

                    return;
                }

            }


            this.subjectIndex = 0;

            this.questionIndex = 0;

        },


        // =========================================================
        // CURRENT SUBJECT
        // =========================================================

        get currentSubject() {

            if (
                !this.exam ||
                !Array.isArray(this.exam.subjects)
            ) {

                return null;
            }


            return (
                this.exam.subjects[
                    this.subjectIndex
                ] || null
            );

        },


        // =========================================================
        // CURRENT QUESTION
        // =========================================================

        get currentQuestion() {

            const subject =
                this.currentSubject;


            if (!subject) {
                return null;
            }


            if (
                !Array.isArray(subject.questions)
            ) {

                return null;
            }


            return (
                subject.questions[
                    this.questionIndex
                ] || null
            );

        },


        // =========================================================
        // DISPLAY QUESTION NUMBER
        // =========================================================

        get displayQuestionNumber() {

            if (!this.currentQuestion) {
                return 0;
            }


            return Number(
                this.currentQuestion.number ??
                this.questionIndex + 1
            );

        },


        // =========================================================
        // SELECT SUBJECT
        // =========================================================

        selectSubject(index) {

            if (!this.exam) {
                return;
            }


            const targetIndex =
                Number(index);


            if (
                targetIndex < 0 ||
                targetIndex >= this.exam.subjects.length
            ) {

                return;
            }


            if (
                targetIndex === this.subjectIndex
            ) {

                return;
            }


            this.saveCurrentPosition();


            this.subjectIndex =
                targetIndex;


            const subject =
                this.currentSubject;


            this.questionIndex =
                Math.min(
                    Number(
                        subject.current_question_position || 0
                    ),
                    Math.max(
                        subject.questions.length - 1,
                        0
                    )
                );


            this.saveCurrentPosition();

        },


        // =========================================================
        // SELECT QUESTION
        // =========================================================

        selectQuestion(index) {

            const subject =
                this.currentSubject;


            if (!subject) {
                return;
            }


            const targetIndex =
                Number(index);


            if (
                targetIndex < 0 ||
                targetIndex >= subject.questions.length
            ) {

                return;
            }


            this.questionIndex =
                targetIndex;


            this.saveCurrentPosition();

        },


        // =========================================================
        // NEXT QUESTION
        // =========================================================

        nextQuestion() {

            const subject =
                this.currentSubject;


            if (!subject) {
                return;
            }


            if (
                this.questionIndex <
                subject.questions.length - 1
            ) {

                this.questionIndex++;

                this.saveCurrentPosition();

                return;
            }


            if (
                this.subjectIndex <
                this.exam.subjects.length - 1
            ) {

                this.saveCurrentPosition();


                this.subjectIndex++;


                const nextSubject =
                    this.currentSubject;


                this.questionIndex =
                    Math.min(
                        Number(
                            nextSubject.current_question_position || 0
                        ),
                        Math.max(
                            nextSubject.questions.length - 1,
                            0
                        )
                    );


                this.saveCurrentPosition();

            }

        },


        // =========================================================
        // PREVIOUS QUESTION
        // =========================================================

        previousQuestion() {

            if (this.questionIndex > 0) {

                this.questionIndex--;

                this.saveCurrentPosition();

                return;
            }


            if (this.subjectIndex > 0) {

                this.saveCurrentPosition();


                this.subjectIndex--;


                const previousSubject =
                    this.currentSubject;


                this.questionIndex =
                    Math.max(
                        previousSubject.questions.length - 1,
                        0
                    );


                this.saveCurrentPosition();

            }

        },


        // =========================================================
        // SAVE ANSWER
        // =========================================================

        selectAnswer(optionId) {

            if (
                this.timeExpiredHandled ||
                this.remainingSeconds <= 0
            ) {

                return;
            }


            const question =
                this.currentQuestion;


            if (!question) {
                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.save_answer !== "function"
            ) {

                this.setError(
                    "Unable to save answer because the Python bridge is unavailable."
                );

                return;
            }


            const selectedOptionId =
                Number(optionId);


            question.selected_option_id =
                selectedOptionId;


            question.answered =
                true;


            window.examBridge.save_answer(
                Number(question.id),
                selectedOptionId,
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            console.error(
                                "Save answer failed:",
                                data.error
                            );

                            return;
                        }


                        question.selected_option_id =
                            Number(
                                data.selected_option_id
                            );


                        question.answered =
                            true;

                    }
                    catch (error) {

                        console.error(
                            "Save answer response error:",
                            error
                        );

                    }

                }
            );

        },


        // =========================================================
        // SAVE POSITION
        // =========================================================

        saveCurrentPosition() {

            const subject =
                this.currentSubject;


            if (!subject) {
                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.save_question_position !== "function"
            ) {

                return;
            }


            const position =
                Number(this.questionIndex);


            subject.current_question_position =
                position;


            window.examBridge.save_question_position(
                Number(subject.id),
                position,
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            console.error(
                                "Save position failed:",
                                data.error
                            );

                        }

                    }
                    catch (error) {

                        console.error(
                            "Save position response error:",
                            error
                        );

                    }

                }
            );

        },


        // =========================================================
        // TIMER
        // =========================================================

        startDisplayTimer() {

            this.stopTimers();


            this.timerInterval =
                setInterval(() => {

                    if (
                        this.remainingSeconds > 0
                    ) {

                        this.remainingSeconds--;

                    }


                    if (
                        this.remainingSeconds <= 0
                    ) {

                        this.remainingSeconds = 0;

                        this.handleTimeExpired();

                    }

                }, 1000);


            this.clockSyncInterval =
                setInterval(() => {

                    this.syncClock();

                }, 5000);

        },


        // =========================================================
        // SYNC MASTER CLOCK
        // =========================================================

        syncClock() {

            if (!this.examId) {
                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.get_remaining_time !== "function"
            ) {

                return;
            }


            window.examBridge.get_remaining_time(
                Number(this.examId),
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            return;
                        }


                        this.remainingSeconds =
                            Math.max(
                                0,
                                Number(
                                    data.remaining_seconds || 0
                                )
                            );


                        if (data.expired) {

                            this.handleTimeExpired();

                        }

                    }
                    catch (error) {

                        console.error(
                            "Clock response error:",
                            error
                        );

                    }

                }
            );

        },


        // =========================================================
        // TIME EXPIRED
        // =========================================================

        handleTimeExpired() {

            if (this.timeExpiredHandled) {
                return;
            }


            this.timeExpiredHandled =
                true;


            this.stopTimers();

            this.remainingSeconds = 0;


            this.showTimeoutOverlay = true;

            this.timeoutCompleting = true;

            this.timeoutResultReady = false;


            /*
             * Automatically complete the exam.
             */

            if (
                !window.examBridge ||
                typeof window.examBridge.complete_exam !== "function"
            ) {

                this.timeoutCompleting = false;

                this.setError(
                    "The Python bridge does not expose complete_exam()."
                );

                return;
            }


            window.examBridge.complete_exam(
                Number(this.examId),
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            console.error(
                                "Automatic completion failed:",
                                data.error
                            );

                            this.timeoutCompleting = false;

                            return;
                        }


                        /*
                         * THIS IS THE IMPORTANT PART.
                         *
                         * ExamBridge already returns:
                         *
                         * {
                         *     success: true,
                         *     result: {...}
                         * }
                         */

                        this.result =
                            data.result || null;


                        this.timeoutCompleting = false;

                        this.timeoutResultReady =
                            !!this.result;


                    }
                    catch (error) {

                        console.error(
                            "Timeout completion error:",
                            error
                        );

                        this.timeoutCompleting = false;

                    }

                }
            );

        },


        // =========================================================
        // VIEW RESULT AFTER TIMEOUT
        // =========================================================

        viewTimeoutResult() {

            if (
                this.timeoutCompleting
            ) {

                return;
            }


            if (!this.result) {

                this.loadResult();

                return;
            }


            this.showTimeoutOverlay =
                false;


            this.screen =
                "result";


            this.$nextTick(() => {

                this.renderResultChart();

            });

        },


        // =========================================================
        // LOAD RESULT
        // =========================================================

        loadResult() {

            if (!this.examId) {
                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.get_result !== "function"
            ) {

                this.setError(
                    "The Python bridge does not expose get_result()."
                );

                return;
            }


            this.resultLoading = true;


            window.examBridge.get_result(
                Number(this.examId),
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.resultLoading = false;

                            this.setError(
                                data.error ||
                                "Unable to load examination result."
                            );

                            return;
                        }


                        this.result =
                            data.result || null;


                        this.resultLoading = false;


                        if (!this.result) {

                            this.setError(
                                "No result data was returned."
                            );

                            return;
                        }


                        this.screen =
                            "result";


                        this.$nextTick(() => {

                            this.renderResultChart();

                        });

                    }
                    catch (error) {

                        console.error(
                            "Result response error:",
                            error
                        );

                        this.resultLoading = false;

                        this.setError(
                            "Invalid result response received from Python."
                        );

                    }

                }
            );

        },


        // =========================================================
        // FINISH EXAM
        // =========================================================

        finishExam() {

            if (
                this.finishingExam ||
                !this.exam
            ) {

                return;
            }


            this.saveCurrentPosition();


            this.showFinishModal =
                true;

        },


        // =========================================================
        // CONFIRM FINISH
        // =========================================================

        confirmFinishExam() {

            if (
                this.finishingExam ||
                !this.examId
            ) {

                return;
            }


            this.finishingExam =
                true;


            this.showFinishModal =
                false;


            this.stopTimers();


            if (
                !window.examBridge ||
                typeof window.examBridge.complete_exam !== "function"
            ) {

                this.finishingExam = false;

                this.setError(
                    "The Python bridge does not currently expose complete_exam()."
                );

                return;
            }


            window.examBridge.complete_exam(
                Number(this.examId),
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.finishingExam = false;

                            this.setError(
                                data.error ||
                                "Unable to complete examination."
                            );

                            return;
                        }


                        /*
                         * ExamBridge returns:
                         *
                         * response.result
                         */

                        this.result =
                            data.result || null;


                        if (!this.result) {

                            this.finishingExam = false;

                            this.setError(
                                "The examination was completed but no result was returned."
                            );

                            return;
                        }


                        this.exam =
                            this.exam || {};


                        this.exam.is_completed =
                            true;


                        this.finishingExam = false;


                        this.screen =
                            "result";


                        this.$nextTick(() => {

                            this.renderResultChart();

                        });

                    }
                    catch (error) {

                        console.error(
                            "Complete exam response error:",
                            error
                        );

                        this.finishingExam = false;

                        this.setError(
                            "Invalid response received while completing the examination."
                        );

                    }

                }
            );

        },


        // =========================================================
        // FORMAT TIME
        // =========================================================

        formatTime(seconds) {

            const total =
                Math.max(
                    0,
                    Number(seconds) || 0
                );


            const hours =
                Math.floor(
                    total / 3600
                );


            const minutes =
                Math.floor(
                    (total % 3600) / 60
                );


            const secs =
                total % 60;


            return [
                String(hours).padStart(2, "0"),
                String(minutes).padStart(2, "0"),
                String(secs).padStart(2, "0"),
            ].join(":");

        },


        // =========================================================
        // FORMAT PERCENTAGE
        // =========================================================

        formatPercentage(value) {

            const number =
                Number(value);


            if (!Number.isFinite(number)) {
                return "0%";
            }


            return `${number.toFixed(2)}%`;

        },


        // =========================================================
        // RESULT HELPERS
        // =========================================================

        get resultTotal() {

            return Number(
                this.result?.total || 0
            );

        },


        get resultCorrect() {

            return Number(
                this.result?.correct || 0
            );

        },


        get resultWrong() {

            return Number(
                this.result?.wrong || 0
            );

        },


        get resultUnanswered() {

            return Number(
                this.result?.unanswered || 0
            );

        },


        get resultPercentage() {

            return Number(
                this.result?.percentage || 0
            );

        },


        // =========================================================
        // ANSWERED COUNT
        // =========================================================

        get answeredCount() {

            if (!this.exam) {
                return 0;
            }


            return this.exam.subjects.reduce(
                (total, subject) => {

                    const questions =
                        Array.isArray(subject.questions)
                            ? subject.questions
                            : [];


                    return (
                        total +
                        questions.filter(
                            question =>
                                question.selected_option_id !== null &&
                                question.selected_option_id !== undefined
                        ).length
                    );

                },
                0
            );

        },


        // =========================================================
        // TOTAL QUESTIONS
        // =========================================================

        get totalQuestionCount() {

            if (!this.exam) {
                return 0;
            }


            return this.exam.subjects.reduce(
                (total, subject) => {

                    return (
                        total +
                        (
                            Array.isArray(subject.questions)
                                ? subject.questions.length
                                : 0
                        )
                    );

                },
                0
            );

        },


        // =========================================================
        // UNANSWERED COUNT
        // =========================================================

        get unansweredCount() {

            return Math.max(
                0,
                this.totalQuestionCount -
                this.answeredCount
            );

        },


        // =========================================================
        // SUBJECT ANSWERED COUNT
        // =========================================================

        subjectAnsweredCount(subject) {

            if (!subject) {
                return 0;
            }


            const questions =
                Array.isArray(subject.questions)
                    ? subject.questions
                    : [];


            return questions.filter(
                question =>
                    question.selected_option_id !== null &&
                    question.selected_option_id !== undefined
            ).length;

        },


        // =========================================================
        // SUBJECT PROGRESS
        // =========================================================

        subjectProgressText(subject) {

            if (!subject) {
                return "0/0";
            }


            const total =
                Array.isArray(subject.questions)
                    ? subject.questions.length
                    : Number(
                        subject.question_count || 0
                    );


            return (
                `${this.subjectAnsweredCount(subject)}/${total}`
            );

        },


        // =========================================================
        // PREVIOUS BUTTON STATE
        // =========================================================

        get canGoPrevious() {

            return (
                this.subjectIndex > 0 ||
                this.questionIndex > 0
            );

        },


        // =========================================================
        // RESULT REVIEW
        // =========================================================

        questionIsUnanswered(question) {

            if (!question) {
                return true;
            }


            return (
                !question.is_answered &&
                (
                    question.selected_option_id === null ||
                    question.selected_option_id === undefined
                )
            );

        },


        // =========================================================
        // QUESTION IS CORRECT
        // =========================================================

        questionIsCorrect(question) {

            if (!question) {
                return false;
            }


            /*
             * Backend has already calculated this.
             *
             * DO NOT recalculate the grade from the
             * frontend if is_correct exists.
             */

            return (
                question.is_answered === true &&
                question.is_correct === true
            );

        },


        // =========================================================
        // QUESTION IS WRONG
        // =========================================================

        questionIsWrong(question) {

            if (!question) {
                return false;
            }


            return (
                question.is_answered === true &&
                question.is_correct === false
            );

        },


        // =========================================================
        // REVIEW STATUS TEXT
        // =========================================================

        reviewStatusText(question) {

            if (
                this.questionIsUnanswered(question)
            ) {

                return "Unanswered";

            }


            if (
                this.questionIsCorrect(question)
            ) {

                return "Correct";

            }


            return "Wrong";

        },


        // =========================================================
        // REVIEW STATUS CLASS
        // =========================================================

        reviewStatusClass(question) {

            if (
                this.questionIsUnanswered(question)
            ) {

                return "bg-amber-100 text-amber-800";

            }


            if (
                this.questionIsCorrect(question)
            ) {

                return "bg-green-100 text-green-800";

            }


            return "bg-red-100 text-red-800";

        },


        // =========================================================
        // REVIEW OPTION CLASS
        // =========================================================

        reviewOptionClass(question, option) {

            if (!question || !option) {

                return "border-gray-200 bg-white text-gray-700";

            }


            const optionId =
                Number(option.id);


            const correctId =
                Number(question.correct_option_id);


            const selectedId =
                question.selected_option_id === null ||
                question.selected_option_id === undefined
                    ? null
                    : Number(
                        question.selected_option_id
                    );


            /*
             * CORRECT ANSWER ALWAYS GETS GREEN.
             */

            if (
                Number.isFinite(correctId) &&
                optionId === correctId
            ) {

                return [
                    "border-green-500",
                    "bg-green-50",
                    "text-green-900",
                    "ring-1",
                    "ring-green-300",
                ].join(" ");

            }


            /*
             * If the student's selected answer is wrong,
             * make ONLY that selected option red.
             */

            if (
                selectedId !== null &&
                optionId === selectedId
            ) {

                return [
                    "border-red-500",
                    "bg-red-50",
                    "text-red-900",
                    "ring-1",
                    "ring-red-300",
                ].join(" ");

            }


            /*
             * Everything else stays normal.
             */

            return [
                "border-gray-200",
                "bg-white",
                "text-gray-700",
            ].join(" ");

        },


        // =========================================================
        // STUDENT ANSWER TEXT
        // =========================================================

        studentAnswerText(question) {

            if (!question) {
                return "Not answered";
            }


            const selectedId =
                question.selected_option_id;


            if (
                selectedId === null ||
                selectedId === undefined
            ) {

                return "Not answered";

            }


            const option =
                this.findOption(
                    question,
                    selectedId
                );


            if (!option) {

                return "Selected answer";

            }


            return `${option.label}. ${option.text}`;

        },


        // =========================================================
        // CORRECT ANSWER TEXT
        // =========================================================

        correctAnswerText(question) {

            if (!question) {
                return "Correct answer not supplied.";
            }


            const correctId =
                question.correct_option_id;


            if (
                correctId === null ||
                correctId === undefined
            ) {

                return "Correct answer not supplied.";

            }


            const option =
                this.findOption(
                    question,
                    correctId
                );


            if (!option) {

                return "Correct answer not supplied.";

            }


            return `${option.label}. ${option.text}`;

        },


        // =========================================================
        // FIND OPTION
        // =========================================================

        findOption(question, optionId) {

            if (
                !question ||
                !Array.isArray(question.options)
            ) {

                return null;
            }


            const id =
                Number(optionId);


            return (
                question.options.find(
                    option =>
                        Number(option.id) === id
                ) || null
            );

        },


        // =========================================================
        // OPTION IS CORRECT
        // =========================================================

        isCorrectOption(option) {

            return !!option;

        },


        // =========================================================
        // OPTION IS STUDENT ANSWER
        // =========================================================

        isStudentOption(question, option) {

            if (
                !question ||
                !option
            ) {

                return false;
            }


            if (
                question.selected_option_id === null ||
                question.selected_option_id === undefined
            ) {

                return false;
            }


            return (
                Number(question.selected_option_id) ===
                Number(option.id)
            );

        },


        // =========================================================
        // REVIEW CARD CLASS
        // =========================================================

        reviewCardClass(question) {

            if (
                this.questionIsUnanswered(question)
            ) {

                return "border-amber-200 bg-amber-50";

            }


            if (
                this.questionIsCorrect(question)
            ) {

                return "border-green-200 bg-green-50";

            }


            return "border-red-200 bg-red-50";

        },


        // =========================================================
        // REVIEW HEADER CLASS
        // =========================================================

        reviewHeaderClass(question) {

            if (
                this.questionIsUnanswered(question)
            ) {

                return "text-amber-900";

            }


            if (
                this.questionIsCorrect(question)
            ) {

                return "text-green-900";

            }


            return "text-red-900";

        },


        // =========================================================
        // SUBJECT RESULT
        // =========================================================

        get resultSubjects() {

            return Array.isArray(
                this.result?.subjects
            )
                ? this.result.subjects
                : [];

        },


        // =========================================================
        // REVIEW QUESTIONS
        // =========================================================

        get reviewQuestions() {

            return Array.isArray(
                this.result?.review
            )
                ? this.result.review
                : [];

        },


        // =========================================================
        // RESULT CHART
        // =========================================================

        renderResultChart() {

            /*
             * Wait until the DOM has actually rendered.
             */

            this.$nextTick(() => {

                const canvas =
                    document.getElementById(
                        "resultSubjectChart"
                    );


                if (!canvas) {

                    console.warn(
                        "Result chart canvas not found."
                    );

                    return;
                }


                if (
                    typeof Chart === "undefined"
                ) {

                    console.warn(
                        "Chart.js is not loaded."
                    );

                    return;
                }


                if (this.resultChart) {

                    try {

                        this.resultChart.destroy();

                    }
                    catch (error) {

                        console.warn(
                            "Unable to destroy previous chart:",
                            error
                        );

                    }

                    this.resultChart = null;

                }


                const subjects =
                    this.resultSubjects;


                const labels =
                    subjects.map(
                        subject =>
                            subject.subject_name
                    );


                const percentages =
                    subjects.map(
                        subject =>
                            Number(
                                subject.percentage || 0
                            )
                    );


                this.resultChart =
                    new Chart(
                        canvas.getContext("2d"),
                        {
                            type: "bar",

                            data: {

                                labels,

                                datasets: [
                                    {
                                        label: "Percentage",

                                        data: percentages,

                                        borderWidth: 1,
                                    }
                                ],

                            },

                            options: {

                                responsive: true,

                                maintainAspectRatio: false,

                                scales: {

                                    y: {

                                        beginAtZero: true,

                                        max: 100,

                                        ticks: {

                                            callback:
                                                value =>
                                                    `${value}%`,

                                        },

                                    },

                                },

                                plugins: {

                                    legend: {

                                        display: false,

                                    },

                                    tooltip: {

                                        callbacks: {

                                            label:
                                                context =>
                                                    `${context.parsed.y}%`,

                                        },

                                    },

                                },

                            },

                        }
                    );

            });

        },


        // =========================================================
        // PRINT RESULT
        // =========================================================

        printResult() {

            /*
             * Give Alpine/browser one moment to finish
             * rendering the result page.
             */

            this.$nextTick(() => {

                window.print();

            });

        },


        // =========================================================
        // RESTART APPLICATION
        // =========================================================

        restartApplication() {

            if (
                !window.examBridge ||
                typeof window.examBridge.restart_application !== "function"
            ) {

                console.error(
                    "examBridge.restart_application is unavailable."
                );

                return;
            }


            window.examBridge.restart_application(
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            console.error(
                                "Restart failed:",
                                data.error
                            );

                            return;
                        }


                        /*
                         * Python launches the new process.
                         *
                         * Close this process/window.
                         */

                        window.close();

                    }
                    catch (error) {

                        console.error(
                            "Restart response error:",
                            error
                        );

                    }

                }
            );

        },


        // =========================================================
        // ERROR
        // =========================================================

        setError(message) {

            this.error =
                String(
                    message ||
                    "An unexpected error occurred."
                );


            this.loading = false;

        },


        // =========================================================
        // CLEAR ERROR
        // =========================================================

        clearError() {

            this.error = null;


            if (!this.exam) {

                this.screen =
                    "selection";

                this.loadYears();

                return;
            }


            this.screen =
                "exam";

        },


        // =========================================================
        // PARSE BRIDGE RESPONSE
        // =========================================================

        parseBridgeResponse(response) {

            if (
                typeof response === "string"
            ) {

                return JSON.parse(response);

            }


            if (
                response &&
                typeof response === "object"
            ) {

                return response;

            }


            throw new Error(
                "Empty response from Python bridge."
            );

        },


        // =========================================================
        // STOP TIMERS
        // =========================================================

        stopTimers() {

            if (this.timerInterval) {

                clearInterval(
                    this.timerInterval
                );

                this.timerInterval =
                    null;

            }


            if (this.clockSyncInterval) {

                clearInterval(
                    this.clockSyncInterval
                );

                this.clockSyncInterval =
                    null;

            }

        },


        // =========================================================
        // CLEANUP
        // =========================================================

        destroy() {

            this.stopTimers();


            if (this.resultChart) {

                try {

                    this.resultChart.destroy();

                }
                catch (error) {

                    console.warn(
                        "Chart cleanup error:",
                        error
                    );

                }

                this.resultChart = null;

            }

        },

    }));

});
document.addEventListener("alpine:init", () => {

    console.log("Alpine initialized.");

    Alpine.data("examApp", () => ({

        // =========================================================
        // APPLICATION STATE & NAVIGATION
        // =========================================================

        screen: "selection", // 'selection' | 'exam' | 'result' | 'admin'

        loading: true,

        loadingMessage: "Loading examination years...",

        error: null,

        // =========================================================
        // TOAST NOTIFICATIONS SYSTEM
        // =========================================================

        toasts: [],

        showToast(message, type = "info", duration = 3500) {
            const id = Date.now() + Math.random().toString(36).substring(2, 6);
            const toast = { id, message, type };
            this.toasts.push(toast);

            setTimeout(() => {
                this.removeToast(id);
            }, duration);
        },

        removeToast(id) {
            this.toasts = this.toasts.filter(t => t.id !== id);
        },

        // =========================================================
        // AUTHENTICATION & USER STATE
        // =========================================================

        currentUser: null, // { id, username, full_name, role }

        showLoginModal: false,

        loginForm: {
            username: "",
            password: "",
            loading: false,
            error: "",
        },

        get isAdmin() {
            return this.currentUser && this.currentUser.role === "admin";
        },

        openLoginModal() {
            this.loginForm.username = "";
            this.loginForm.password = "";
            this.loginForm.error = "";
            this.loginForm.loading = false;
            this.showLoginModal = true;
        },

        closeLoginModal() {
            this.showLoginModal = false;
        },

        loginAdmin() {
            if (!this.loginForm.username.trim() || !this.loginForm.password.trim()) {
                this.loginForm.error = "Please enter both username and password.";
                this.showToast("Please enter username and password.", "warning");
                return;
            }

            if (!window.examBridge || typeof window.examBridge.login_admin !== "function") {
                this.showToast("Authentication service unavailable.", "error");
                return;
            }

            this.loginForm.loading = true;
            this.loginForm.error = "";

            window.examBridge.login_admin(
                this.loginForm.username.trim(),
                this.loginForm.password.trim(),
                (response) => {
                    this.loginForm.loading = false;
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            this.currentUser = data.user;
                            this.showLoginModal = false;
                            this.showToast(`Welcome back, ${data.user.full_name}!`, "success");
                            this.screen = "admin";
                            this.loadAdminData();
                        } else {
                            this.loginForm.error = data.error || "Login failed.";
                            this.showToast(data.error || "Login failed.", "error");
                        }
                    } catch (err) {
                        this.loginForm.error = "Invalid response from server.";
                        this.showToast("Login error occurred.", "error");
                    }
                }
            );
        },

        logoutAdmin() {
            const name = this.currentUser?.full_name || "Admin";
            this.currentUser = null;
            this.screen = "selection";
            this.showToast(`${name} has been logged out successfully.`, "info");
        },

        // =========================================================
        // STUDENT IDENTIFICATION & REGISTRATION ON EXAM SETUP
        // =========================================================

        studentIdentifier: "",

        studentFullName: "",

        studentClass: "",

        studentAdmissionYear: null,

        studentStatus: null, // null | 'checking' | 'verified' | 'not_found' | 'admin'

        studentLookupTimeout: null,

        showStudentRegisterModal: false,

        studentRegisterForm: {
            role: "student",
            username: "",
            full_name: "",
            student_class: "",
            admission_year: new Date().getFullYear(),
            password: "",
            loading: false,
            error: "",
        },

        onStudentIdentifierInput() {
            clearTimeout(this.studentLookupTimeout);
            const val = this.studentIdentifier.trim();
            if (!val) {
                this.studentStatus = null;
                this.studentFullName = "";
                this.studentClass = "";
                this.studentAdmissionYear = null;
                return;
            }

            this.studentStatus = "checking";
            this.studentLookupTimeout = setTimeout(() => {
                this.verifyStudentCandidate(val);
            }, 350);
        },

        verifyStudentCandidate(identifier) {
            if (!window.examBridge || typeof window.examBridge.check_username !== "function") {
                this.studentStatus = null;
                return;
            }

            window.examBridge.check_username(identifier, (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success && data.exists) {
                        if (data.is_admin) {
                            this.studentStatus = "admin";
                            this.studentFullName = data.user.full_name;
                            this.showToast("Admin accounts cannot take exams. Please use a student account.", "warning");
                        } else {
                            this.studentStatus = "verified";
                            this.studentFullName = data.user.full_name;
                            this.studentClass = data.user.student_class || "";
                            this.studentAdmissionYear = data.user.admission_year;
                            this.showToast(`Candidate verified: ${data.user.full_name} (${data.user.student_class || "No Class"})`, "success");
                        }
                    } else {
                        this.studentStatus = "not_found";
                        this.studentFullName = "";
                        this.studentClass = "";
                        this.studentAdmissionYear = null;
                    }
                } catch (err) {
                    this.studentStatus = null;
                }
            });
        },

        openStudentRegisterModal() {
            this.studentRegisterForm = {
                role: "student",
                username: this.studentIdentifier.trim() || "",
                full_name: "",
                student_class: "SS3",
                admission_year: new Date().getFullYear(),
                password: "",
                loading: false,
                error: "",
            };
            this.showStudentRegisterModal = true;
        },

        closeStudentRegisterModal() {
            this.showStudentRegisterModal = false;
        },

        registerStudent() {
            const form = this.studentRegisterForm;
            if (!form.username.trim() || !form.full_name.trim()) {
                form.error = "Username and Full Name are required.";
                this.showToast("Username and Full Name are required.", "warning");
                return;
            }

            if (!window.examBridge || typeof window.examBridge.register_student !== "function") {
                this.showToast("Registration bridge unavailable.", "error");
                return;
            }

            form.loading = true;
            form.error = "";

            window.examBridge.register_user(
                form.username.trim(),
                form.password.trim() || "cbt123",
                form.full_name.trim(),
                form.role || "student",
                form.student_class.trim(),
                String(form.admission_year || ""),
                (response) => {
                    form.loading = false;
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            this.showToast(`Student registered successfully: ${data.user.full_name}`, "success");
                            this.studentIdentifier = data.user.username;
                            this.studentFullName = data.user.full_name;
                            this.studentClass = data.user.student_class || "";
                            this.studentAdmissionYear = data.user.admission_year;
                            this.studentStatus = "verified";
                            this.showStudentRegisterModal = false;
                        } else {
                            form.error = data.error || "Registration failed.";
                            this.showToast(data.error || "Registration failed.", "error");
                        }
                    } catch (err) {
                        form.error = "Error parsing registration response.";
                        this.showToast("Registration error occurred.", "error");
                    }
                }
            );
        },

        // =========================================================
        // DATABASE / SELECTION STATE
        // =========================================================

        years: [],

        subjects: [],

        selectedYear: null,

        selectedSubjectIds: [],

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
        // MASTER CLOCK
        // =========================================================

        remainingSeconds: 0,

        timerInterval: null,

        clockSyncInterval: null,

        timeExpiredHandled: false,

        // =========================================================
        // FINISH & TIMEOUT
        // =========================================================

        showFinishModal: false,

        finishingExam: false,

        showTimeoutOverlay: false,

        timeoutCompleting: false,

        timeoutComplete: false,

        // =========================================================
        // RESULT
        // =========================================================

        result: null,

        resultChart: null,

        resultReviewFilter: "all", // 'all' | 'correct' | 'wrong' | 'unanswered'

        resultReviewSubjectFilter: "all",

        resultReviewExpandedId: null,

        // =========================================================
        // ADMIN DASHBOARD STATE
        // =========================================================

        adminActiveTab: "students", // 'students' | 'users'

        // Tab 1: Student Exam Records
        adminStudents: [],
        adminSearchQuery: "",
        adminClassFilter: "all",
        adminCurrentPage: 1,
        adminItemsPerPage: 10,
        selectedStudentHistory: null,
        showStudentHistoryModal: false,
        historyLoading: false,

        // Tab 2: User Accounts CRUD
        allUsers: [],
        userSearchQuery: "",
        userRoleFilter: "all",
        userClassFilter: "all",
        userCurrentPage: 1,
        userItemsPerPage: 10,
        showUserModal: false,
        userModalMode: "create", // 'create' | 'edit'
        editingUserId: null,
        userForm: {
            username: "",
            password: "",
            full_name: "",
            role: "student",
            student_class: "",
            admission_year: new Date().getFullYear(),
            is_active: true,
            loading: false,
            error: "",
        },

        showDeleteConfirmModal: false,
        deleteConfirmData: {
            type: "", // 'user' | 'student'
            id: null,
            name: "",
            loading: false,
        },

        // =========================================================
        // INITIALIZATION
        // =========================================================

        init() {
            console.log("examApp initialized with enhanced Features & Toasts.");
            window.showToast = (msg, type, dur) => this.showToast(msg, type, dur);
            this.waitForBridge();
        },

        waitForBridge() {
            if (
                window.examBridge &&
                typeof window.examBridge.get_years === "function"
            ) {
                console.log("examBridge is ready.");
                this.loadYears();
                return;
            }

            setTimeout(() => {
                this.waitForBridge();
            }, 100);
        },

        // =========================================================
        // LOAD YEARS
        // =========================================================

        loadYears() {
            this.loading = true;
            this.loadingMessage = "Loading examination years...";
            this.error = null;

            if (!window.examBridge || typeof window.examBridge.get_years !== "function") {
                this.setError("The Python bridge is not ready.");
                return;
            }

            window.examBridge.get_years((response) => {
                this.loading = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (!data.success) {
                        this.setError(data.error || "Failed to load examination years.");
                        return;
                    }

                    this.years = Array.isArray(data.years) ? data.years : [];
                    if (this.years.length > 0) {
                        this.selectedYear = this.years[0];
                        this.loadSubjectsForYear(this.selectedYear);
                    }
                } catch (error) {
                    this.setError("Failed to parse examination years response.");
                }
            });
        },

        // =========================================================
        // LOAD SUBJECTS FOR YEAR
        // =========================================================

        loadSubjectsForYear(year) {
            if (!year) return;
            this.subjectsLoading = true;
            this.selectedSubjectIds = [];

            if (!window.examBridge || typeof window.examBridge.get_subjects_for_year !== "function") {
                this.subjectsLoading = false;
                return;
            }

            window.examBridge.get_subjects_for_year(Number(year), (response) => {
                this.subjectsLoading = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (!data.success) {
                        this.setError(data.error || "Failed to load subjects for this year.");
                        return;
                    }
                    this.subjects = Array.isArray(data.subjects) ? data.subjects : [];
                } catch (error) {
                    this.setError("Failed to parse subjects response.");
                }
            });
        },

        // =========================================================
        // SUBJECT TOGGLE
        // =========================================================

        toggleSubject(subjectId) {
            const id = Number(subjectId);
            const index = this.selectedSubjectIds.indexOf(id);
            if (index >= 0) {
                this.selectedSubjectIds.splice(index, 1);
            } else {
                this.selectedSubjectIds.push(id);
            }
        },

        selectAllSubjects() {
            this.selectedSubjectIds = this.subjects.map(s => Number(s.id));
            this.showToast(`Selected all ${this.subjects.length} subjects`, "info");
        },

        clearAllSubjects() {
            this.selectedSubjectIds = [];
        },

        get selectedTotalQuestions() {
            return this.subjects
                .filter(s => this.selectedSubjectIds.includes(Number(s.id)))
                .reduce((sum, s) => sum + Number(s.question_count || 0), 0);
        },

        // =========================================================
        // START EXAMINATION
        // =========================================================

        startExamination() {
            if (!this.selectedYear) {
                this.showToast("Please select an examination year.", "warning");
                return;
            }

            if (this.selectedSubjectIds.length === 0) {
                this.showToast("Please select at least one subject.", "warning");
                return;
            }

            // Verify Candidate identity
            const identifier = this.studentIdentifier.trim();
            if (!identifier) {
                this.showToast("Please enter your Student Username or Full Name.", "warning");
                return;
            }

            if (this.studentStatus === "admin") {
                this.showToast("Admin accounts cannot take exams. Please use a student account.", "error");
                return;
            }

            if (this.studentStatus === "not_found") {
                this.showToast("You are not registered in the database. Please register below.", "warning");
                this.openStudentRegisterModal();
                return;
            }

            this.creatingExam = true;
            this.error = null;

            const studentNameParam = this.studentFullName || identifier;

            window.examBridge.create_exam(
                Number(this.selectedYear),
                this.selectedSubjectIds,
                Number(this.durationMinutes),
                studentNameParam,
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (!data.success) {
                            this.creatingExam = false;
                            this.setError(data.error || "Failed to create exam session.");
                            this.showToast(data.error || "Failed to create exam session.", "error");
                            return;
                        }

                        this.examId = Number(data.exam_id);
                        this.startExamSession(this.examId);
                    } catch (error) {
                        this.creatingExam = false;
                        this.setError("Failed to parse create exam response.");
                    }
                }
            );
        },

        startExamSession(examId) {
            window.examBridge.start_exam(Number(examId), (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (!data.success) {
                        this.creatingExam = false;
                        this.setError(data.error || "Failed to start exam session.");
                        return;
                    }

                    this.remainingSeconds = Number(data.remaining_seconds || 0);
                    this.loadExamPayload(examId);
                } catch (error) {
                    this.creatingExam = false;
                    this.setError("Failed to parse start exam response.");
                }
            });
        },

        loadExamPayload(examId) {
            window.examBridge.get_exam(Number(examId), (response) => {
                this.creatingExam = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (!data.success) {
                        this.setError(data.error || "Failed to load exam payload.");
                        return;
                    }

                    this.exam = data.exam;
                    this.subjectIndex = 0;
                    this.questionIndex = 0;
                    this.screen = "exam";
                    this.startMasterClock();
                    this.showToast("Examination started. Good luck!", "success");
                } catch (error) {
                    this.setError("Failed to parse exam payload.");
                }
            });
        },

        // =========================================================
        // MASTER CLOCK
        // =========================================================

        startMasterClock() {
            this.stopTimers();
            this.timeExpiredHandled = false;

            this.timerInterval = setInterval(() => {
                if (this.remainingSeconds > 0) {
                    this.remainingSeconds -= 1;
                    if (this.remainingSeconds === 300) {
                        this.showToast("⚠️ Warning: 5 minutes remaining!", "warning", 5000);
                    }
                    if (this.remainingSeconds === 60) {
                        this.showToast("⚠️ Urgent: 1 minute remaining!", "error", 5000);
                    }
                } else {
                    this.handleTimeExpired();
                }
            }, 1000);

            this.clockSyncInterval = setInterval(() => {
                this.syncClock();
            }, 5000);
        },

        syncClock() {
            if (!this.examId || !window.examBridge || typeof window.examBridge.get_remaining_time !== "function") return;

            window.examBridge.get_remaining_time(Number(this.examId), (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.remainingSeconds = Math.max(0, Number(data.remaining_seconds || 0));
                        if (data.expired) {
                            this.handleTimeExpired();
                        }
                    }
                } catch (e) {}
            });
        },

        handleTimeExpired() {
            if (this.timeExpiredHandled) return;
            this.timeExpiredHandled = true;
            this.remainingSeconds = 0;
            this.stopTimers();
            this.showTimeoutOverlay = true;
            this.timeoutCompleting = true;
            this.timeoutComplete = false;
            this.showToast("Time has expired! Automatically submitting your examination...", "warning", 6000);
            this.completeExamAfterTimeout();
        },

        completeExamAfterTimeout() {
            if (!this.examId || !window.examBridge) {
                this.timeoutCompleting = false;
                return;
            }

            window.examBridge.complete_exam(Number(this.examId), (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.result = data.result || null;
                        this.timeoutCompleting = false;
                        this.timeoutComplete = true;
                        if (this.exam) this.exam.is_completed = true;
                        this.prepareResultChart();
                    }
                } catch (e) {
                    this.timeoutCompleting = false;
                }
            });
        },

        viewTimeoutResult() {
            if (this.timeoutCompleting || !this.result) return;
            this.showTimeoutOverlay = false;
            this.screen = "result";
            this.prepareResultChart();
        },

        stopTimers() {
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
                this.timerInterval = null;
            }
            if (this.clockSyncInterval) {
                clearInterval(this.clockSyncInterval);
                this.clockSyncInterval = null;
            }
        },

        formatTime(seconds) {
            const total = Math.max(0, Number(seconds) || 0);
            const hours = Math.floor(total / 3600);
            const minutes = Math.floor((total % 3600) / 60);
            const secs = total % 60;
            return [
                String(hours).padStart(2, "0"),
                String(minutes).padStart(2, "0"),
                String(secs).padStart(2, "0"),
            ].join(":");
        },

        // =========================================================
        // QUESTION NAVIGATION & AUTO ADVANCE
        // =========================================================

        get currentSubject() {
            if (!this.exam || !Array.isArray(this.exam.subjects)) return null;
            return this.exam.subjects[this.subjectIndex] || null;
        },

        get currentQuestion() {
            const subject = this.currentSubject;
            if (!subject || !Array.isArray(subject.questions)) return null;
            return subject.questions[this.questionIndex] || null;
        },

        get displayQuestionNumber() {
            if (!this.currentQuestion) return 0;
            return Number(this.currentQuestion.number ?? this.questionIndex + 1);
        },

        selectSubject(index) {
            if (!this.exam) return;
            const targetIndex = Number(index);
            if (targetIndex < 0 || targetIndex >= this.exam.subjects.length || targetIndex === this.subjectIndex) return;

            this.saveCurrentPosition();
            this.subjectIndex = targetIndex;
            const subject = this.currentSubject;
            this.questionIndex = Math.min(
                Number(subject.current_question_position || 0),
                Math.max((subject.questions?.length || 1) - 1, 0)
            );
            this.saveCurrentPosition();
        },

        selectQuestion(index) {
            const subject = this.currentSubject;
            if (!subject) return;
            const targetIndex = Number(index);
            if (targetIndex < 0 || targetIndex >= subject.questions.length) return;

            this.questionIndex = targetIndex;
            this.saveCurrentPosition();
        },

        nextQuestion() {
            const subject = this.currentSubject;
            if (!subject || !Array.isArray(subject.questions)) return;

            if (this.questionIndex < subject.questions.length - 1) {
                this.questionIndex += 1;
                this.saveCurrentPosition();
                return;
            }

            if (this.subjectIndex < this.exam.subjects.length - 1) {
                this.selectSubject(this.subjectIndex + 1);
            }
        },

        previousQuestion() {
            if (this.questionIndex > 0) {
                this.questionIndex -= 1;
                this.saveCurrentPosition();
                return;
            }

            if (this.subjectIndex > 0) {
                this.subjectIndex -= 1;
                const prevSubject = this.currentSubject;
                if (prevSubject && Array.isArray(prevSubject.questions)) {
                    this.questionIndex = Math.max(0, prevSubject.questions.length - 1);
                }
                this.saveCurrentPosition();
            }
        },

        selectAnswer(optionId) {
            if (this.exam?.is_completed || this.timeExpiredHandled) return;
            const question = this.currentQuestion;
            if (!question) return;

            const selectedOptionId = Number(optionId);
            question.selected_option_id = selectedOptionId;
            question.answered = true;

            if (window.examBridge && typeof window.examBridge.save_answer === "function") {
                window.examBridge.save_answer(Number(question.id), selectedOptionId, (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            question.selected_option_id = Number(data.selected_option_id);
                            question.answered = true;
                        }
                    } catch (e) {}
                });
            }

            // Auto-advance to next question smoothly
            if (!this.isLastQuestion) {
                clearTimeout(this._autoNextTimer);
                this._autoNextTimer = setTimeout(() => {
                    this.nextQuestion();
                }, 220);
            }
        },

        saveCurrentPosition() {
            const subject = this.currentSubject;
            if (!subject || !subject.exam_subject_id || !window.examBridge) return;
            window.examBridge.save_question_position(Number(subject.exam_subject_id), Number(this.questionIndex), () => {});
        },

        // =========================================================
        // PROGRESS & GETTERS
        // =========================================================

        get answeredCount() {
            if (!this.exam || !Array.isArray(this.exam.subjects)) return 0;
            return this.exam.subjects.reduce((total, subject) => {
                const questions = Array.isArray(subject.questions) ? subject.questions : [];
                return total + questions.filter(q => q.selected_option_id !== null && q.selected_option_id !== undefined).length;
            }, 0);
        },

        get totalQuestionCount() {
            if (!this.exam || !Array.isArray(this.exam.subjects)) return 0;
            return this.exam.subjects.reduce((total, subject) => {
                return total + (Array.isArray(subject.questions) ? subject.questions.length : 0);
            }, 0);
        },

        get unansweredCount() {
            return Math.max(0, this.totalQuestionCount - this.answeredCount);
        },

        get overallProgressPercent() {
            const total = this.totalQuestionCount;
            return total > 0 ? Math.round((this.answeredCount / total) * 100) : 0;
        },

        subjectAnsweredCount(subject) {
            if (!subject || !Array.isArray(subject.questions)) return 0;
            return subject.questions.filter(q => q.selected_option_id !== null && q.selected_option_id !== undefined).length;
        },

        subjectProgressText(subject) {
            if (!subject) return "0/0";
            const total = Array.isArray(subject.questions) ? subject.questions.length : Number(subject.question_count || 0);
            return `${this.subjectAnsweredCount(subject)}/${total}`;
        },

        subjectProgressPercent(subject) {
            if (!subject) return 0;
            const total = Array.isArray(subject.questions) ? subject.questions.length : Number(subject.question_count || 0);
            if (total <= 0) return 0;
            return Math.round((this.subjectAnsweredCount(subject) / total) * 100);
        },

        get canGoPrevious() {
            return this.subjectIndex > 0 || this.questionIndex > 0;
        },

        get isLastQuestion() {
            if (!this.exam || !Array.isArray(this.exam.subjects) || !this.currentSubject) return false;
            const isLastSub = this.subjectIndex >= this.exam.subjects.length - 1;
            const qCount = Array.isArray(this.currentSubject.questions) ? this.currentSubject.questions.length : 1;
            const isLastQ = this.questionIndex >= qCount - 1;
            return isLastSub && isLastQ;
        },

        // =========================================================
        // FINISH EXAMINATION & RESULTS
        // =========================================================

        finishExam() {
            if (this.finishingExam || !this.exam) return;
            this.saveCurrentPosition();
            this.showFinishModal = true;
        },

        confirmFinishExam() {
            if (this.finishingExam || !this.examId) return;
            this.finishingExam = true;
            this.showFinishModal = false;
            this.stopTimers();

            window.examBridge.complete_exam(Number(this.examId), (response) => {
                this.finishingExam = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (!data.success) {
                        this.setError(data.error || "Failed to complete exam.");
                        this.showToast(data.error || "Failed to complete exam.", "error");
                        return;
                    }

                    this.result = data.result || null;
                    if (this.exam) this.exam.is_completed = true;
                    this.screen = "result";
                    this.prepareResultChart();
                    this.showToast("Examination completed successfully!", "success");
                } catch (error) {
                    this.setError("Failed to parse completion response.");
                }
            });
        },

        prepareResultChart() {
            if (!this.result) return;
            this.$nextTick(() => {
                const canvas = document.getElementById("resultBreakdownChart");
                if (!canvas || typeof Chart === "undefined") return;

                if (this.resultChart) {
                    this.resultChart.destroy();
                }

                const ctx = canvas.getContext("2d");
                this.resultChart = new Chart(ctx, {
                    type: "doughnut",
                    data: {
                        labels: ["Correct", "Wrong", "Unanswered"],
                        datasets: [{
                            data: [
                                Number(this.result.correct || 0),
                                Number(this.result.wrong || 0),
                                Number(this.result.unanswered || 0),
                            ],
                            backgroundColor: ["#16a34a", "#dc2626", "#9ca3af"],
                            borderWidth: 2,
                            borderColor: "#ffffff",
                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: "bottom",
                                labels: { boxWidth: 12, padding: 14 },
                            },
                        },
                    },
                });
            });
        },

        get filteredReviewQuestions() {
            if (!this.result || !Array.isArray(this.result.review)) return [];
            let list = this.result.review;

            if (this.resultReviewSubjectFilter !== "all") {
                list = list.filter(q => Number(q.subject_id) === Number(this.resultReviewSubjectFilter));
            }

            if (this.resultReviewFilter === "correct") {
                list = list.filter(q => q.is_correct === true);
            } else if (this.resultReviewFilter === "wrong") {
                list = list.filter(q => q.is_answered && !q.is_correct);
            } else if (this.resultReviewFilter === "unanswered") {
                list = list.filter(q => !q.is_answered);
            }

            return list;
        },

        printResult() {
            if (!this.result) return;
            this.showToast("Opening native print dialog...", "info");
            if (window.examBridge && typeof window.examBridge.print_current_page === "function") {
                window.examBridge.print_current_page((response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data && data.success) {
                            this.showToast("Document sent to printer successfully!", "success");
                        }
                    } catch (e) {}
                });
            } else {
                this.$nextTick(() => {
                    window.print();
                });
            }
        },

        downloadResultPDF() {
            if (!this.result) return;
            const currentExamId = Number(this.examId || this.result.exam_id);

            if (!window.examBridge || typeof window.examBridge.generate_result_pdf_reportlab !== "function") {
                this.printResult();
                return;
            }

            this.loading = true;
            this.loadingMessage = "Generating PDF transcript using ReportLab...";

            window.examBridge.generate_result_pdf_reportlab(currentExamId, (response) => {
                this.loading = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.showToast(`Result PDF transcript saved & opened!`, "success", 5000);
                    } else {
                        this.setError(data.error || "Unable to generate PDF.");
                        this.showToast(data.error || "Unable to generate PDF.", "error");
                    }
                } catch (err) {
                    this.setError("Error parsing PDF response.");
                }
            });
        },

        returnToApp() {
            this.showTimeoutOverlay = false;
            this.timeoutCompleting = false;
            this.timeoutComplete = false;
            this.result = null;
            this.exam = null;
            this.examId = null;
            this.subjectIndex = 0;
            this.questionIndex = 0;
            this.remainingSeconds = 0;
            this.timeExpiredHandled = false;
            this.stopTimers();
            this.screen = "selection";
            this.loadYears();
        },

        restartApplication() {
            if (!window.examBridge || typeof window.examBridge.restart_application !== "function") {
                this.returnToApp();
                return;
            }
            this.showToast("Restarting application...", "info");
            window.examBridge.restart_application(() => {});
        },

        // =========================================================
        // ADMIN DASHBOARD LOGIC (STUDENT HISTORY & USER CRUD)
        // =========================================================

        loadAdminData() {
            this.loadAllStudents();
            this.loadAllUsers();
        },

        // --- TAB 1: STUDENT RECORDS & TRANSCRIPTS ---

        loadAllStudents() {
            if (!window.examBridge || typeof window.examBridge.get_all_student_records !== "function") return;

            window.examBridge.get_all_student_records((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.adminStudents = data.students || [];
                    }
                } catch (err) {
                    console.error("Error loading student records:", err);
                }
            });
        },

        get filteredStudents() {
            let list = this.adminStudents;
            const q = this.adminSearchQuery.trim().toLowerCase();
            if (q) {
                list = list.filter(s =>
                    (s.name && s.name.toLowerCase().includes(q)) ||
                    (s.student_class && s.student_class.toLowerCase().includes(q))
                );
            }
            if (this.adminClassFilter !== "all") {
                list = list.filter(s => (s.student_class || "").toLowerCase() === this.adminClassFilter.toLowerCase());
            }
            return list;
        },

        get paginatedStudents() {
            const start = (this.adminCurrentPage - 1) * this.adminItemsPerPage;
            return this.filteredStudents.slice(start, start + this.adminItemsPerPage);
        },

        get totalStudentPages() {
            return Math.max(1, Math.ceil(this.filteredStudents.length / this.adminItemsPerPage));
        },

        get distinctStudentClasses() {
            const set = new Set();
            this.adminStudents.forEach(s => {
                if (s.student_class) set.add(s.student_class);
            });
            return Array.from(set).sort();
        },

        viewStudentHistory(studentName) {
            if (!window.examBridge || typeof window.examBridge.get_student_history !== "function") return;

            this.historyLoading = true;
            this.showStudentHistoryModal = true;
            this.selectedStudentHistory = null;

            window.examBridge.get_student_history(studentName, (response) => {
                this.historyLoading = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.selectedStudentHistory = data;
                    } else {
                        this.showToast(data.error || "Failed to load student history.", "error");
                    }
                } catch (err) {
                    this.historyLoading = false;
                    this.showToast("Error reading student history.", "error");
                }
            });
        },

        closeStudentHistoryModal() {
            this.showStudentHistoryModal = false;
            this.selectedStudentHistory = null;
        },

        promptDeleteStudentRecords(studentName) {
            this.deleteConfirmData = {
                type: "student",
                id: studentName,
                name: studentName,
                loading: false,
            };
            this.showDeleteConfirmModal = true;
        },

        deleteStudentRecords(studentName) {
            if (!window.examBridge || typeof window.examBridge.delete_student_records !== "function") return;

            this.deleteConfirmData.loading = true;
            window.examBridge.delete_student_records(studentName, (response) => {
                this.showDeleteConfirmModal = false;
                this.deleteConfirmData.loading = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.showToast(data.message || `Exam records for candidate '${studentName}' deleted.`, "success");
                        this.loadAllStudents();
                        if (this.showStudentHistoryModal) {
                            this.closeStudentHistoryModal();
                        }
                    } else {
                        this.showToast(data.error || "Failed to delete student records.", "error");
                    }
                } catch (e) {
                    this.showToast("Error deleting records.", "error");
                }
            });
        },

        printStudentHistory() {
            this.showToast("Opening candidate history print dialog...", "info");
            if (window.examBridge && typeof window.examBridge.print_current_page === "function") {
                window.examBridge.print_current_page((response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data && data.success) {
                            this.showToast("Candidate history sent to printer!", "success");
                        }
                    } catch (e) {}
                });
            } else {
                this.$nextTick(() => {
                    window.print();
                });
            }
        },

        downloadStudentHistoryPDF() {
            if (!this.selectedStudentHistory) return;
            const name = this.selectedStudentHistory.student_name;

            if (!window.examBridge || typeof window.examBridge.generate_student_history_pdf !== "function") {
                this.printStudentHistory();
                return;
            }

            this.showToast("Generating student transcript PDF...", "info");

            window.examBridge.generate_student_history_pdf(name, (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.showToast("Student transcript PDF saved and opened!", "success", 5000);
                    } else {
                        this.showToast(data.error || "Could not generate history PDF.", "error");
                    }
                } catch (err) {
                    this.showToast("PDF error occurred.", "error");
                }
            });
        },

        // --- TAB 2: USER MANAGEMENT CRUD ---

        loadAllUsers() {
            if (!window.examBridge || typeof window.examBridge.get_all_users !== "function") return;

            window.examBridge.get_all_users((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.allUsers = data.users || [];
                    }
                } catch (e) {
                    console.error("Error loading users:", e);
                }
            });
        },

        get filteredUsers() {
            let list = this.allUsers;
            const q = this.userSearchQuery.trim().toLowerCase();
            if (q) {
                list = list.filter(u =>
                    (u.username && u.username.toLowerCase().includes(q)) ||
                    (u.full_name && u.full_name.toLowerCase().includes(q)) ||
                    (u.student_class && u.student_class.toLowerCase().includes(q))
                );
            }
            if (this.userRoleFilter !== "all") {
                list = list.filter(u => u.role === this.userRoleFilter);
            }
            if (this.userClassFilter !== "all") {
                list = list.filter(u => (u.student_class || "").toLowerCase() === this.userClassFilter.toLowerCase());
            }
            return list;
        },

        get paginatedUsers() {
            const start = (this.userCurrentPage - 1) * this.userItemsPerPage;
            return this.filteredUsers.slice(start, start + this.userItemsPerPage);
        },

        get totalUserPages() {
            return Math.max(1, Math.ceil(this.filteredUsers.length / this.userItemsPerPage));
        },

        openAddUserModal() {
            this.userModalMode = "create";
            this.editingUserId = null;
            this.userForm = {
                username: "",
                password: "",
                full_name: "",
                role: "student",
                student_class: "SS3",
                admission_year: new Date().getFullYear(),
                is_active: true,
                loading: false,
                error: "",
            };
            this.showUserModal = true;
        },

        openEditUserModal(user) {
            this.userModalMode = "edit";
            this.editingUserId = user.id;
            this.userForm = {
                username: user.username,
                password: "",
                full_name: user.full_name,
                role: user.role,
                student_class: user.student_class || "",
                admission_year: user.admission_year || new Date().getFullYear(),
                is_active: Boolean(user.is_active),
                loading: false,
                error: "",
            };
            this.showUserModal = true;
        },

        closeUserModal() {
            this.showUserModal = false;
        },

        saveUser() {
            const form = this.userForm;
            if (!form.username.trim() || !form.full_name.trim()) {
                form.error = "Username and Full Name are required.";
                this.showToast("Username and Full Name are required.", "warning");
                return;
            }

            form.loading = true;
            form.error = "";

            if (this.userModalMode === "create") {
                if (!window.examBridge || typeof window.examBridge.register_user !== "function") return;

                window.examBridge.register_user(
                    form.username.trim(),
                    form.password.trim() || "cbt123",
                    form.full_name.trim(),
                    form.role,
                    form.student_class.trim(),
                    String(form.admission_year || ""),
                    (response) => {
                        form.loading = false;
                        try {
                            const data = this.parseBridgeResponse(response);
                            if (data.success) {
                                this.showToast(`User '${data.user.username}' created successfully!`, "success");
                                this.showUserModal = false;
                                this.loadAllUsers();
                            } else {
                                form.error = data.error || "Failed to create user.";
                                this.showToast(data.error || "Failed to create user.", "error");
                            }
                        } catch (err) {
                            form.error = "Error creating user.";
                        }
                    }
                );
            } else {
                if (!window.examBridge || typeof window.examBridge.update_user !== "function") return;

                window.examBridge.update_user(
                    Number(this.editingUserId),
                    form.username.trim(),
                    form.password.trim(),
                    form.full_name.trim(),
                    form.role,
                    form.student_class.trim(),
                    String(form.admission_year || ""),
                    String(form.is_active),
                    (response) => {
                        form.loading = false;
                        try {
                            const data = this.parseBridgeResponse(response);
                            if (data.success) {
                                this.showToast(`User '${data.user.username}' updated successfully!`, "success");
                                this.showUserModal = false;
                                this.loadAllUsers();
                            } else {
                                form.error = data.error || "Failed to update user.";
                                this.showToast(data.error || "Failed to update user.", "error");
                            }
                        } catch (err) {
                            form.error = "Error updating user.";
                        }
                    }
                );
            }
        },

        promptDeleteUser(user) {
            this.deleteConfirmData = {
                type: "user",
                id: user.id,
                name: user.full_name || user.username,
                loading: false,
            };
            this.showDeleteConfirmModal = true;
        },

        deleteUser(userId) {
            const user = this.allUsers.find(u => u.id === userId);
            const name = user ? (user.full_name || user.username) : "User";

            if (!window.examBridge || typeof window.examBridge.delete_user !== "function") return;

            this.deleteConfirmData.loading = true;
            window.examBridge.delete_user(Number(userId), (response) => {
                this.showDeleteConfirmModal = false;
                this.deleteConfirmData.loading = false;
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.showToast(`User account '${name}' deleted successfully.`, "success");
                        this.loadAllUsers();
                    } else {
                        this.showToast(data.error || "Failed to delete user.", "error");
                    }
                } catch (e) {
                    this.showToast("Error deleting user.", "error");
                }
            });
        },

        confirmDeleteAction() {
            if (this.deleteConfirmData.type === "student") {
                this.deleteStudentRecords(this.deleteConfirmData.id);
            } else if (this.deleteConfirmData.type === "user") {
                this.deleteUser(this.deleteConfirmData.id);
            }
        },

        cancelDeleteAction() {
            this.showDeleteConfirmModal = false;
            this.showToast("Deletion cancelled.", "info");
        },

        // =========================================================
        // HELPERS
        // =========================================================

        setError(message) {
            this.error = message;
            this.showToast(message, "error");
        },

        clearError() {
            this.error = null;
        },

        parseBridgeResponse(response) {
            if (typeof response === "string") {
                return JSON.parse(response);
            }
            return response;
        },

    }));

});
document.addEventListener("alpine:init", () => {

    console.log("Alpine initialized.");

   

    Alpine.data("examApp", () => ({

        // =========================================================
        // APPLICATION STATE
        // =========================================================

        screen: "selection",

        // Question import state
        showQuestionImport: false,

        // Authentication state (admin only)
        currentUser: null,
        isLoggedIn: false,
        showLoginModal: false,
        loginUsername: "",
        loginPassword: "",
        showLoginPassword: false,

        // Student identity & verification state
        studentUsername: "",
        studentFullName: "",
        currentUserStudent: null,
        checkingUsername: false,
        showStudentRegisterModal: false,
        showStudentRegisterPassword: false,
        studentRegisterForm: {
            role: "student",
            username: "",
            password: "",
            full_name: "",
            student_class: "",
            admission_year: new Date().getFullYear(),
        },

        studentRegistered: false,
        welcomeMessage: null,
        showWelcome: false,

        loading: true,
        loadingMessage: "Loading examination years...",
        error: null,

        // User management state (admin only)
        users: [],
        userSearchQuery: "",
        userRoleFilter: "all",
        userClassFilter: "all",
        showUserModal: false,
        showUserPassword: false,
        userModalMode: "create",
        editingUserId: null,
        userForm: {
            username: "",
            password: "",
            full_name: "",
            role: "student",
            student_class: "",
            admission_year: "",
            is_active: true,
        },

        // App settings (admin only)
        appSettings: {
            school_name: "Mock CBT Examination",
            school_address: "",
            school_logo_path: "",
            theme: "light",
        },
        logoVersion: Date.now(),
        showSettingsModal: false,
        settingsForm: {
            school_name: "",
            school_address: "",
            school_logo_path: "",
            theme: "light",
        },
        userCurrentPage: 1,
        userItemsPerPage: 10,

        // Admin state
        adminActiveTab: "students", // 'students' | 'users' | 'questions'
        adminSearchName: "",
        adminStudents: [],
        adminCurrentPage: 1,
        adminItemsPerPage: 10,
        showStudentHistory: false,
        selectedStudentName: "",
        studentHistory: [],
        showDeleteConfirmModal: false,
        userToDelete: null,
        showDeleteStudentConfirmModal: false,
        studentToDelete: null,

        // Subject Management State
        allSubjects: [],
        showSubjectModal: false,
        subjectModalMode: "create", // 'create' | 'edit'
        editingSubjectId: null,
        subjectForm: {
            name: "",
            code: "",
        },

        // Question Bank & Manual Entry State
        qbExamBodyFilter: "all",
        qbYearFilter: "all",
        qbSubjectFilter: "all",
        qbSearchQuery: "",
        qbQuestions: [],
        qbTotalQuestions: 0,
        qbPage: 1,
        qbTotalPages: 1,
        qbPageSize: 10,
        qbLoading: false,

        showQuestionModal: false,
        questionModalMode: "create", // 'create' | 'edit'
        editingQuestionId: null,
        questionForm: {
            exam_body: "JAMB",
            year: 2026,
            subject_id: "",
            question_number: 1,
            text: "",
            options: [
                { label: "A", text: "" },
                { label: "B", text: "" },
                { label: "C", text: "" },
                { label: "D", text: "" }
            ],
            correct_label: "A",
            explanation: "",
        },
        showDeleteQuestionConfirmModal: false,
        questionToDelete: null,

        // =========================================================
        // DATABASE / SELECTION STATE & MULTI-EXAM BODY
        // =========================================================

        selectedExamBody: "JAMB", // 'JAMB' | 'WAEC' | 'NECO' | 'NABTEB' | 'BECE' | 'SCHOOL'
        examBodies: [
            { id: "JAMB", name: "JAMB (UTME)", desc: "Unified Tertiary Matriculation Mock", badge: "JAMB", color: "blue" },
            { id: "WAEC", name: "WAEC (SSCE)", desc: "West African Senior School Certificate Mock", badge: "WAEC", color: "emerald" },
            { id: "NECO", name: "NECO (SSCE)", desc: "National Examinations Council Mock", badge: "NECO", color: "indigo" },
            { id: "NABTEB", name: "NABTEB", desc: "National Business & Technical Exams Mock", badge: "NABTEB", color: "amber" },
            { id: "BECE", name: "BECE / Junior WAEC", desc: "Basic Education Certificate Mock", badge: "BECE", color: "rose" },
            { id: "SCHOOL", name: "School Proprietary", desc: "Internal school continuous assessment & terminal exams", badge: "SCHOOL", color: "purple" }
        ],
        years: [],
        subjects: [],
        selectedYear: null,
        selectedSubjectIds: [],
        studentName: "",
        durationMinutes: 120,
        subjectsLoading: false,
        creatingExam: false,

        // =========================================================
        // AI TUTOR         
        // =========================================================

        showTutor: false,
        tutorLoading: false,
        tutorError: "",
        tutorAnswer: "",
        tutorProvider: "",
        tutorGreeting: "",
        tutorExplanation: "",
        tutorSteps: [],
        tutorHint: "",
        tutorEncouragement: "",
        tutorFollowUp: "",
        tutorQuestion: null,
        tutorResponse: null,

        tutorSpeaking: false,
        tutorPaused: false,
        tutorAvatarState: "idle",

        tutorSpeechSupported: false,
        tutorSpeechUtterance: null,
        tutorVoices: [],
        tutorSelectedVoice: null,

       
        // =========================================================
        // AI TUTOR SPEECH ANALYZERNODE.
        //  
        // i followed this pipeline since window.speechSynthesis does not expose its 
        // generated audio stream to JavaScript, so an AnalyserNode cannot
        //  actually listen to that speech. 
        // 
        // AI response → local TTS audio → <audio> → Web Audio AnalyserNode
        //   → spectral analysis → viseme/mouth state → avatar ... (Idrees note. It matters when revisited)
        // =========================================================

        tutorAudio: null,
        tutorAudioContext: null,
        tutorAnalyser: null,
        tutorAudioSource: null,
        tutorAudioData: null,

        tutorLipSyncFrame: null,
        tutorAudioURL: null,

        tutorViseme: "closed",
        tutorMouthOpen: 0,

        tutorAudioReady: false,
      
        // =========================================================
        // HELPER FUNCTIONS
        // =========================================================

        escapeHtml(text) {
            if (!text) return "";
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        checkStudentUsername(onValidCallback) {
            if (!this.studentUsername || !this.studentUsername.trim()) {
                this.studentFullName = "";
                this.currentUserStudent = null;
                return;
            }

            if (!window.examBridge || typeof window.examBridge.check_username !== "function") {
                return;
            }

            this.checkingUsername = true;
            window.examBridge.check_username(
                this.studentUsername.trim(),
                (response) => {
                    this.checkingUsername = false;
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success && data.exists) {
                            if (data.is_admin) {
                                showToast("Admin accounts cannot take examinations. Please register or use a student account.", "error");
                                this.studentUsername = "";
                                this.studentFullName = "";
                                this.currentUserStudent = null;
                                return;
                            }

                            this.currentUserStudent = data.user;
                            this.studentFullName = data.user.full_name;
                            this.studentName = data.user.full_name; // Keep compatible
                            this.welcomeMessage = `Welcome back, ${data.user.full_name}!`;
                            this.showWelcome = true;
                            setTimeout(() => { this.showWelcome = false; }, 3000);
                            showToast(`Welcome back, ${data.user.full_name}!`, "success");

                            if (typeof onValidCallback === "function") {
                                onValidCallback();
                            }
                        } else if (data.success && !data.exists) {
                            this.studentFullName = "";
                            this.currentUserStudent = null;
                            this.openStudentRegisterModal(this.studentUsername.trim());
                            showToast("Username not found. Please register to proceed.", "info");
                        } else if (data.error) {
                            showToast(data.error, "error");
                        }
                    } catch (err) {
                        console.error("checkStudentUsername error:", err);
                    }
                }
            );
        },

        openStudentRegisterModal(usernamePrefill) {
            const yr = this.selectedYear || new Date().getFullYear();
            this.showStudentRegisterPassword = false;
            this.studentRegisterForm = {
                role: "student",
                username: (usernamePrefill || this.studentUsername || "").trim(),
                password: "",
                full_name: "",
                student_class: "",
                admission_year: yr
            };
            this.showStudentRegisterModal = true;
        },

        registerStudent() {
            const form = this.studentRegisterForm;
            if (!form.username || !form.username.trim()) {
                showToast("Username is required.", "error");
                return;
            }
            if (!form.full_name || !form.full_name.trim()) {
                showToast("Full Name is required.", "error");
                return;
            }

            if (!window.examBridge || typeof window.examBridge.register_student !== "function") {
                showToast("Registration service unavailable.", "error");
                return;
            }

            window.examBridge.register_student(
                form.username.trim(),
                form.password ? form.password.trim() : "password123",
                form.full_name.trim(),
                form.role || "student",
                form.student_class ? form.student_class.trim() : "",
                form.admission_year ? String(form.admission_year).trim() : "",
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            this.currentUserStudent = data.user;
                            this.studentUsername = data.user.username;
                            this.studentFullName = data.user.full_name;
                            this.studentName = data.user.full_name;
                            this.showStudentRegisterModal = false;
                            showToast(`Registered successfully! Welcome, ${data.user.full_name}`, "success");
                        } else {
                            showToast(data.error || "Registration failed.", "error");
                        }
                    } catch (err) {
                        console.error("registerStudent error:", err);
                        showToast("An error occurred during registration.", "error");
                    }
                }
            );
        },

        checkStudentRegistration() {
            if (!this.studentUsername || !this.studentUsername.trim()) {
                return;
            }
            this.checkStudentUsername();
        },

        checkStudentName() {
            this.checkStudentUsername();
        },

        checkAdminNameMatch() {
            if (!this.studentUsername || !this.studentUsername.trim()) {
                return;
            }

            if (!window.examBridge || typeof window.examBridge.check_admin_identity !== "function") {
                return;
            }

            window.examBridge.check_admin_identity(
                this.studentUsername.trim(),
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success && data.is_admin) {
                            showToast("Admin accounts cannot take exams. Please use a student account.", "error");
                            this.studentUsername = "";
                            this.studentFullName = "";
                        }
                    } catch (error) {
                        console.error("Admin identity check error:", error);
                    }
                }
            );
        },


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
        // FINISH
        // =========================================================

        showFinishModal: false,

        finishingExam: false,


        // =========================================================
        // TIMEOUT
        // =========================================================

        showTimeoutOverlay: false,

        timeoutCompleting: false,

        timeoutComplete: false,


        // =========================================================
        // RESULT
        // =========================================================

        result: null,

        resultChart: null,

        resultReviewFilter: 'all',
        resultReviewSubjectFilter: 'all',


        // =========================================================
        // INIT
        // =========================================================

        init() {
            // Apply saved theme immediately on init
            try {
                const savedTheme = localStorage.getItem('cbt_theme') || 'light';
                this.applyTheme(savedTheme);
            } catch (e) {}

            this.loading = true;
            this.loadingMessage = "Initializing...";

            this.setupExamSecurity();
            this.checkAuthStatus();

            this.waitForBridge();

            // Load users, students, subjects, and questions when admin screen is accessed
            this.$watch('screen', (value) => {
                // Scroll to top when screen changes
                window.scrollTo(0, 0);
                
                if (value === 'admin' && this.isAdmin) {
                    this.loadUsers();
                    this.loadAllStudents();
                    this.loadAllSubjects();
                    this.loadQuestionBank();
                }
            });

        },


        get isNavLocked() {
            return this.screen === 'exam' || this.screen === 'result';
        },

        get filteredReviewQuestions() {
            if (!this.result || !this.result.review) return [];
            
            let questions = this.result.review;
            
            // Filter by correctness
            if (this.resultReviewFilter === 'correct') {
                questions = questions.filter(q => q.is_correct);
            } else if (this.resultReviewFilter === 'wrong') {
                questions = questions.filter(q => q.is_answered && !q.is_correct);
            } else if (this.resultReviewFilter === 'unanswered') {
                questions = questions.filter(q => !q.is_answered);
            }
            
            // Filter by subject
            if (this.resultReviewSubjectFilter !== 'all') {
                questions = questions.filter(q => q.subject_id === this.resultReviewSubjectFilter);
            }
            
            return questions;
        },

        // =========================================================
        // EXAM SECURITY
        // =========================================================

        setupExamSecurity() {
            // Prevent page reload during active exam or result review
            window.addEventListener('beforeunload', (e) => {
                if (this.screen === 'exam' || this.screen === 'result') {
                    e.preventDefault();
                    e.returnValue = '';
                    return 'You cannot reload or leave the exam/result page. Please restart the program to start fresh.';
                }
            });

            // Detect tab switching
            document.addEventListener('visibilitychange', () => {
                if (this.screen === 'exam' && document.hidden) {
                    console.warn('Tab switched during exam');
                    showToast('Warning: Tab switching detected during exam!', 'warning');
                }
            });

            // Prevent keyboard shortcuts that could exit or reload
            document.addEventListener('keydown', (e) => {
                if (this.screen === 'exam' || this.screen === 'result') {
                    // Prevent common exit / reload shortcuts
                    if (e.ctrlKey && (e.key === 'w' || e.key === 'f' || e.key === 'r' || e.key === 'R')) {
                        e.preventDefault();
                        showToast('Navigation and reload are disabled', 'warning');
                    }
                    if (e.key === 'F5' || e.key === 'Escape') {
                        e.preventDefault();
                        showToast('Page reload is disabled', 'warning');
                    }
                }
            });

            // Watch screen changes to lock/unlock navbar
            this.$watch('screen', (newScreen) => {
                const navButtons = document.querySelectorAll('nav button');
                const isLocked = newScreen === 'exam' || newScreen === 'result';
                navButtons.forEach(btn => {
                    if (isLocked) {
                        btn.disabled = true;
                        btn.style.opacity = '0.5';
                        btn.style.pointerEvents = 'none';
                        btn.style.cursor = 'not-allowed';
                    } else {
                        btn.disabled = false;
                        btn.style.opacity = '';
                        btn.style.pointerEvents = '';
                        btn.style.cursor = '';
                    }
                });
            });
        },

        // =========================================================
        // AUTHENTICATION
        // =========================================================

        checkAuthStatus() {
            if (!window.examBridge || typeof window.examBridge.get_current_user !== "function") {
                return;
            }

            window.examBridge.get_current_user((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success && data.user) {
                        this.currentUser = data.user;
                        this.isLoggedIn = true;
                    } else {
                        this.currentUser = null;
                        this.isLoggedIn = false;
                    }
                } catch (error) {
                    console.error("Auth check error:", error);
                }
            });
        },

        login(username, password) {
            if (!window.examBridge || typeof window.examBridge.login !== "function") {
                showToast("Authentication not available", "error");
                return;
            }

            const wasOnImportScreen = this.screen === 'import';
            console.log('Login attempt - wasOnImportScreen:', wasOnImportScreen, 'screen:', this.screen);

            window.examBridge.login(username, password, (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    console.log('Login response:', data);
                    if (data.success) {
                        this.currentUser = data.user;
                        this.isLoggedIn = true;
                        this.showLoginModal = false;
                        this.loginUsername = "";
                        this.loginPassword = "";
                        showToast(`Welcome, ${data.user.full_name}!`, "success");
                        
                        console.log('After login - isAdmin:', this.isAdmin, 'wasOnImportScreen:', wasOnImportScreen);
                        
                        // If user was trying to access import screen or admin, navigate appropriately
                        if (this.isAdmin) {
                            if (wasOnImportScreen) {
                                this.screen = 'import';
                            } else {
                                this.screen = 'admin';
                            }
                        }
                    } else {
                        this.loginPassword = "";
                        showToast(data.error || "Login failed", "error");
                    }
                } catch (error) {
                    this.loginPassword = "";
                    console.error("Login error:", error);
                    showToast("Login failed", "error");
                }
            });
        },

        logout() {
            this.loginUsername = "";
            this.loginPassword = "";
            if (!window.examBridge || typeof window.examBridge.logout !== "function") {
                return;
            }

            window.examBridge.logout((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.currentUser = null;
                        this.isLoggedIn = false;
                        this.screen = "selection";
                        this.loginUsername = "";
                        this.loginPassword = "";
                        showToast("Logged out successfully", "success");
                    }
                } catch (error) {
                    console.error("Logout error:", error);
                }
            });
        },

        get isAdmin() {
            return this.currentUser && this.currentUser.role === "admin";
        },

        get isLastQuestion() {
            if (!this.currentSubject || !this.exam) return false;
            const isLastInSubject = this.questionIndex >= this.currentSubject.questions.length - 1;
            const isLastSubject = this.subjectIndex >= this.exam.subjects.length - 1;
            return isLastInSubject && isLastSubject;
        },

        // =========================================================
        // SUBJECT MANAGEMENT
        // =========================================================

        loadAllSubjects() {
            if (!window.examBridge || typeof window.examBridge.get_all_subjects !== "function") return;
            window.examBridge.get_all_subjects((res) => {
                try {
                    const data = this.parseBridgeResponse(res);
                    if (data.success) {
                        this.allSubjects = data.subjects || [];
                    }
                } catch (err) {
                    console.error("loadAllSubjects error:", err);
                }
            });
        },

        openSubjectModal() {
            this.subjectModalMode = "create";
            this.editingSubjectId = null;
            this.subjectForm = { name: "", code: "" };
            this.showSubjectModal = true;
            this.loadAllSubjects();
        },

        editSubject(s) {
            this.subjectModalMode = "edit";
            this.editingSubjectId = s.id;
            this.subjectForm = { name: s.name, code: s.code || "" };
        },

        resetSubjectForm() {
            this.subjectModalMode = "create";
            this.editingSubjectId = null;
            this.subjectForm = { name: "", code: "" };
        },

        saveSubject() {
            if (!this.subjectForm.name || !this.subjectForm.name.trim()) {
                showToast("Subject name is required.", "error");
                return;
            }
            if (!window.examBridge) return;

            if (this.subjectModalMode === "create") {
                window.examBridge.create_subject(
                    this.subjectForm.name.trim(),
                    this.subjectForm.code ? this.subjectForm.code.trim() : "",
                    (res) => {
                        try {
                            const data = this.parseBridgeResponse(res);
                            if (data.success) {
                                showToast(`Subject '${data.subject.name}' added successfully.`, "success");
                                this.resetSubjectForm();
                                this.loadAllSubjects();
                                this.loadYears();
                            } else {
                                showToast(data.error || "Failed to create subject.", "error");
                            }
                        } catch (err) {
                            console.error(err);
                        }
                    }
                );
            } else {
                window.examBridge.update_subject(
                    this.editingSubjectId,
                    this.subjectForm.name.trim(),
                    this.subjectForm.code ? this.subjectForm.code.trim() : "",
                    "true",
                    (res) => {
                        try {
                            const data = this.parseBridgeResponse(res);
                            if (data.success) {
                                showToast("Subject updated successfully.", "success");
                                this.resetSubjectForm();
                                this.loadAllSubjects();
                                this.loadYears();
                            } else {
                                showToast(data.error || "Failed to update subject.", "error");
                            }
                        } catch (err) {
                            console.error(err);
                        }
                    }
                );
            }
        },

        deleteSubject(subjectId) {
            if (!window.examBridge || typeof window.examBridge.delete_subject !== "function") return;
            window.examBridge.delete_subject(subjectId, (res) => {
                try {
                    const data = this.parseBridgeResponse(res);
                    if (data.success) {
                        showToast("Subject deleted.", "success");
                        this.loadAllSubjects();
                        this.loadYears();
                    } else {
                        showToast(data.error || "Failed to delete subject.", "error");
                    }
                } catch (err) {
                    console.error(err);
                }
            });
        },

        // =========================================================
        // QUESTION BANK & MANUAL ENTRY
        // =========================================================

        loadQuestionBank(page) {
            if (!window.examBridge || typeof window.examBridge.get_questions_by_filter !== "function") return;
            if (page) this.qbPage = page;
            this.qbLoading = true;
            window.examBridge.get_questions_by_filter(
                this.qbYearFilter === "all" ? "" : String(this.qbYearFilter),
                this.qbSubjectFilter === "all" ? "" : String(this.qbSubjectFilter),
                this.qbSearchQuery ? this.qbSearchQuery.trim() : "",
                this.qbPage,
                this.qbPageSize,
                this.qbExamBodyFilter === "all" ? "" : String(this.qbExamBodyFilter),
                (res) => {
                    this.qbLoading = false;
                    try {
                        const data = this.parseBridgeResponse(res);
                        if (data.success) {
                            this.qbQuestions = data.questions || [];
                            this.qbTotalQuestions = data.total || 0;
                            this.qbTotalPages = data.total_pages || 1;
                            this.qbPage = data.page || 1;
                        } else {
                            showToast(data.error || "Failed to load questions.", "error");
                        }
                    } catch (err) {
                        console.error("loadQuestionBank error:", err);
                    }
                }
            );
        },

        openAddQuestionModal() {
            if (!this.allSubjects.length) {
                this.loadAllSubjects();
            }
            const defaultYear = this.qbYearFilter !== "all" ? Number(this.qbYearFilter) : (this.selectedYear || new Date().getFullYear());
            const defaultSubject = this.qbSubjectFilter !== "all" ? Number(this.qbSubjectFilter) : (this.allSubjects.length ? this.allSubjects[0].id : "");
            const defaultBody = this.qbExamBodyFilter !== "all" ? this.qbExamBodyFilter : (this.selectedExamBody || "JAMB");

            this.questionModalMode = "create";
            this.editingQuestionId = null;
            this.questionForm = {
                exam_body: defaultBody,
                year: defaultYear,
                subject_id: defaultSubject,
                question_number: 1,
                text: "",
                options: [
                    { label: "A", text: "" },
                    { label: "B", text: "" },
                    { label: "C", text: "" },
                    { label: "D", text: "" }
                ],
                correct_label: "A",
                explanation: ""
            };
            this.showQuestionModal = true;
            if (defaultSubject && defaultYear) {
                this.fetchNextQuestionNumber();
            }
        },

        onQuestionYearOrSubjectChange() {
            if (this.questionModalMode === "create" && this.questionForm.year && this.questionForm.subject_id) {
                this.fetchNextQuestionNumber();
            }
        },

        fetchNextQuestionNumber() {
            if (!this.questionForm.year || !this.questionForm.subject_id) return;
            if (!window.examBridge || typeof window.examBridge.get_next_question_number !== "function") return;
            window.examBridge.get_next_question_number(
                Number(this.questionForm.year),
                Number(this.questionForm.subject_id),
                this.questionForm.exam_body || "JAMB",
                (res) => {
                    try {
                        const data = this.parseBridgeResponse(res);
                        if (data.success && data.next_number) {
                            this.questionForm.question_number = data.next_number;
                        }
                    } catch (err) {
                        console.error("fetchNextQuestionNumber error:", err);
                    }
                }
            );
        },

        addQuestionOption() {
            if (this.questionForm.options.length < 6) {
                const nextLabel = String.fromCharCode(65 + this.questionForm.options.length);
                this.questionForm.options.push({ label: nextLabel, text: "" });
            }
        },

        removeQuestionOption(idx) {
            if (this.questionForm.options.length > 2) {
                this.questionForm.options.splice(idx, 1);
                this.questionForm.options.forEach((opt, i) => {
                    opt.label = String.fromCharCode(65 + i);
                });
                const labels = this.questionForm.options.map(o => o.label);
                if (!labels.includes(this.questionForm.correct_label)) {
                    this.questionForm.correct_label = labels[0];
                }
            }
        },

        openEditQuestionModal(q) {
            this.questionModalMode = "edit";
            this.editingQuestionId = q.id;
            this.questionForm = {
                exam_body: q.exam_body || "JAMB",
                year: q.year,
                subject_id: q.subject_id,
                question_number: q.question_number,
                text: q.text,
                options: q.options && q.options.length ? JSON.parse(JSON.stringify(q.options)) : [
                    { label: "A", text: "" },
                    { label: "B", text: "" },
                    { label: "C", text: "" },
                    { label: "D", text: "" }
                ],
                correct_label: q.correct_label || "A",
                explanation: q.explanation || ""
            };
            this.showQuestionModal = true;
        },

        saveQuestionManual(addAnother = false) {
            const f = this.questionForm;
            if (!f.year || !f.subject_id || !f.question_number) {
                showToast("Please fill in Exam Year, Subject, and Question Number.", "error");
                return;
            }
            if (!f.text || !f.text.trim()) {
                showToast("Question text is required.", "error");
                return;
            }
            for (const opt of f.options) {
                if (!opt.text || !opt.text.trim()) {
                    showToast(`Please enter text for Option ${opt.label}.`, "error");
                    return;
                }
            }
            if (!f.correct_label) {
                showToast("Please select which option is the correct answer.", "error");
                return;
            }

            const optionsJson = JSON.stringify(f.options);
            const examBody = f.exam_body || "JAMB";

            if (this.questionModalMode === "create") {
                window.examBridge.create_question_manual(
                    Number(f.year),
                    Number(f.subject_id),
                    Number(f.question_number),
                    f.text.trim(),
                    optionsJson,
                    f.correct_label,
                    f.explanation ? f.explanation.trim() : "",
                    examBody,
                    (res) => {
                        try {
                            const data = this.parseBridgeResponse(res);
                            if (data.success) {
                                showToast(`Question ${f.question_number} (${examBody}) saved successfully!`, "success");
                                this.loadQuestionBank();
                                this.loadYears();
                                if (addAnother) {
                                    f.question_number = Number(f.question_number) + 1;
                                    f.text = "";
                                    f.options.forEach(o => o.text = "");
                                    f.explanation = "";
                                } else {
                                    this.showQuestionModal = false;
                                }
                            } else {
                                showToast(data.error || "Failed to create question.", "error");
                            }
                        } catch (err) {
                            console.error("create_question_manual error:", err);
                        }
                    }
                );
            } else {
                window.examBridge.update_question_manual(
                    this.editingQuestionId,
                    Number(f.year),
                    Number(f.subject_id),
                    Number(f.question_number),
                    f.text.trim(),
                    optionsJson,
                    f.correct_label,
                    f.explanation ? f.explanation.trim() : "",
                    examBody,
                    (res) => {
                        try {
                            const data = this.parseBridgeResponse(res);
                            if (data.success) {
                                showToast(`Question ${f.question_number} updated successfully!`, "success");
                                this.loadQuestionBank();
                                this.loadYears();
                                this.showQuestionModal = false;
                            } else {
                                showToast(data.error || "Failed to update question.", "error");
                            }
                        } catch (err) {
                            console.error("update_question_manual error:", err);
                        }
                    }
                );
            }
        },

        confirmDeleteQuestion(q) {
            this.questionToDelete = q;
            this.showDeleteQuestionConfirmModal = true;
        },

        deleteQuestionManual() {
            if (!this.questionToDelete || !window.examBridge) return;
            window.examBridge.delete_question_manual(
                this.questionToDelete.id,
                (res) => {
                    try {
                        const data = this.parseBridgeResponse(res);
                        if (data.success) {
                            showToast("Question deleted.", "success");
                            this.showDeleteQuestionConfirmModal = false;
                            this.questionToDelete = null;
                            this.loadQuestionBank();
                            this.loadYears();
                        } else {
                            showToast(data.error || "Failed to delete question.", "error");
                        }
                    } catch (err) {
                        console.error("delete_question_manual error:", err);
                    }
                }
            );
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
                this.loadAllSubjects();
                this.loadAppSettings();
                return;
            }

            console.log("Waiting for examBridge...");
            setTimeout(() => {
                this.waitForBridge();
            }, 100);
        },

        // =========================================================
        // SELECT EXAM BODY
        // =========================================================

        selectExamBody(body) {
            if (!body) return;
            const b = String(body).toUpperCase().trim();
            if (this.selectedExamBody === b && this.years.length > 0) return;
            this.selectedExamBody = b;
            this.selectedYear = null;
            this.selectedSubjectIds = [];
            this.subjects = [];

            // Preset recommended default duration based on exam body
            if (b === "JAMB") {
                this.durationMinutes = 120;
            } else if (b === "BECE") {
                this.durationMinutes = 60;
            } else if (b === "WAEC" || b === "NECO" || b === "NABTEB") {
                this.durationMinutes = 90;
            }

            this.loadYears();
        },

        // =========================================================
        // LOAD YEARS
        // =========================================================

        loadYears() {

            this.loading = true;

            const bodyName = this.selectedExamBody || "examination";
            this.loadingMessage =
                `Loading ${bodyName} examination years...`;

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
                this.selectedExamBody || "JAMB",
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
                            "Available years for",
                            this.selectedExamBody,
                            ":",
                            this.years
                        );

                        // Auto-select latest year if available and none selected
                        if (this.years.length > 0 && !this.selectedYear) {
                            this.selectYear(this.years[0]);
                        }

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


            this.selectedYear = Number(year);

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
                this.selectedExamBody || "JAMB",
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
                            this.selectedExamBody,
                            year,
                            this.subjects
                        );

                    }
                    catch (error) {

                        console.error(
                            "Subject response error:",
                            error
                        );
                    }

                }
            );

        },


        // =========================================================
        // SUBJECT SELECTION
        // =========================================================

        toggleSubject(subjectId) {

            const id = Number(subjectId);

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
        // SUBJECT SELECTED?
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

            if (!this.studentUsername || !this.studentUsername.trim()) {
                this.setError("Please enter your registered username to start the examination.");
                showToast("Please enter your username", "warning");
                return;
            }

            if (!this.studentFullName) {
                this.checkStudentUsername(() => {
                    this.createExam();
                });
                return;
            }

            if (!this.selectedYear) {
                this.setError("Please select an examination year.");
                return;
            }

            if (!this.selectedSubjectIds.length) {
                this.setError("Please select at least one subject.");
                return;
            }

            if (
                !Number.isInteger(Number(this.durationMinutes)) ||
                Number(this.durationMinutes) <= 0
            ) {
                this.setError("Exam duration must be greater than zero.");
                return;
            }

            if (
                !window.examBridge ||
                typeof window.examBridge.create_exam !== "function"
            ) {
                this.setError("The Python bridge does not currently expose create_exam().");
                return;
            }

            this.creatingExam = true;
            this.error = null;

            const year = Number(this.selectedYear);
            const subjectIds = this.selectedSubjectIds.map(id => Number(id));
            const duration = Number(this.durationMinutes);
            const candidateName = (this.studentFullName || this.studentUsername).trim();

            this._doCreateExam(year, subjectIds, duration, candidateName);
        },

        _doCreateExam(year, subjectIds, duration, name) {
            const chosenBody = this.selectedExamBody || "JAMB";
            window.examBridge.create_exam(
                year,
                subjectIds,
                duration,
                name,
                chosenBody,
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


                        this.creatingExam = false;
                        this.screen = "session_summary";

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

            this.result = null;

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


            this.loading = true;

            this.loadingMessage =
                "Starting examination...";


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


                        this.screen = "exam";

                        this.loading = false;

                        this.creatingExam = false;

                        this.timeExpiredHandled = false;


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


            /*
            * A newly-created exam has every subject at position 0.
            *
            * Therefore we cannot interpret position 0 alone as
            * "this subject was previously visited".
            *
            * For a fresh exam, start at the first subject.
            *
            * If an existing exam has a saved position greater than
            * zero, restore that subject/question.
            */

            for (
                let i = 0;
                i < this.exam.subjects.length;
                i++
            ) {

                const subject =
                    this.exam.subjects[i];


                if (
                    !Array.isArray(subject.questions) ||
                    !subject.questions.length
                ) {

                    continue;
                }


                const position =
                    Number(
                        subject.current_question_position ?? 0
                    );


                if (
                    Number.isInteger(position) &&
                    position > 0 &&
                    position < subject.questions.length
                ) {

                    this.subjectIndex = i;

                    this.questionIndex = position;

                    return;

                }

            }


            /*
            * No previously advanced position was found.
            *
            * This is a fresh exam, so always begin with
            * the first subject and first question.
            */

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
        // QUESTION NUMBER
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
                        (subject.questions?.length || 1) - 1,
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
                            (nextSubject.questions?.length || 1) - 1,
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
                        (previousSubject.questions?.length || 1) - 1,
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
                this.exam?.is_completed ||
                this.timeExpiredHandled
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


            question.answered = true;


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


                        question.answered = true;

                        // Auto-advance to next question after saving
                        this.nextQuestion();

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
        // MASTER TIMER
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
        // CLOCK SYNC
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

                            console.error(
                                "Clock synchronization failed:",
                                data.error
                            );

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


            this.timeExpiredHandled = true;

            this.remainingSeconds = 0;

            this.stopTimers();


            this.showTimeoutOverlay = true;

            this.timeoutCompleting = true;

            this.timeoutComplete = false;


            this.completeExamAfterTimeout();

        },


        // =========================================================
        // AUTOMATIC TIMEOUT COMPLETION
        // =========================================================

        completeExamAfterTimeout() {

            if (!this.examId) {

                this.timeoutCompleting = false;

                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.complete_exam !== "function"
            ) {

                this.timeoutCompleting = false;

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

                            console.error(
                                "Automatic completion failed:",
                                data.error
                            );

                            this.timeoutCompleting = false;

                            return;
                        }


                        this.result =
                            data.result || null;

                        this.exam.is_completed = true;

                        this.finishingExam = false;

                        this.screen = "result";

                        this.prepareResultChart();


                        this.timeoutCompleting = false;

                        this.timeoutComplete = true;


                        if (this.exam) {

                            this.exam.is_completed = true;

                        }


                        this.prepareResultChart();

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
                this.timeoutCompleting ||
                !this.result
            ) {

                return;
            }


            this.showTimeoutOverlay = false;

            this.screen = "result";


            this.prepareResultChart();

        },


        // =========================================================
        // STOP TIMERS
        // =========================================================

        stopTimers() {

            if (this.timerInterval) {

                clearInterval(
                    this.timerInterval
                );

                this.timerInterval = null;

            }


            if (this.clockSyncInterval) {

                clearInterval(
                    this.clockSyncInterval
                );

                this.clockSyncInterval = null;

            }

        },


        // =========================================================
        // FORMAT CLOCK
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
        // ANSWERED COUNT
        // =========================================================

        get answeredCount() {

            if (!this.exam) {
                return 0;
            }

            return this.exam.subjects.reduce(
                (total, subject) => {

                    return (
                        total +
                        this.subjectAnsweredCount(subject)
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
                        this.subjectTotalCount(subject)
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
        // OVERALL PROGRESS PERCENTAGE
        // =========================================================

        get overallProgressPercent() {

            const total =
                this.totalQuestionCount;

            if (!total) {
                return 0;
            }

            return Math.round(
                (
                    this.answeredCount /
                    total
                ) * 100
            );

        },


        // =========================================================
        // SUBJECT TOTAL COUNT
        // =========================================================

        subjectTotalCount(subject) {

            if (!subject) {
                return 0;
            }

            /*
            * During the actual exam, the authoritative count
            * comes from the questions loaded by get_exam_payload().
            */

            if (
                Array.isArray(subject.questions)
            ) {

                return subject.questions.length;

            }

            return Number(
                subject.question_count || 0
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
        // SUBJECT PROGRESS PERCENTAGE
        // =========================================================

        subjectProgressPercent(subject) {

            const total =
                this.subjectTotalCount(subject);

            if (!total) {
                return 0;
            }

            return Math.round(
                (
                    this.subjectAnsweredCount(subject) /
                    total
                ) * 100
            );

        },


        // =========================================================
        // SUBJECT PROGRESS TEXT
        // =========================================================

        subjectProgressText(subject) {

            if (!subject) {
                return "0 / 0";
            }

            const answered =
                this.subjectAnsweredCount(subject);

            const total =
                this.subjectTotalCount(subject);

            return `${answered} / ${total}`;

        },

        // =========================================================
        // PREVIOUS BUTTON
        // =========================================================

        get canGoPrevious() {

            return (
                this.subjectIndex > 0 ||
                this.questionIndex > 0
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


            this.showFinishModal = true;

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


            this.finishingExam = true;

            this.showFinishModal = false;


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
                         * IMPORTANT:
                         *
                         * The result comes directly from
                         * complete_exam().
                         */

                        this.result =
                            data.result || null;


                        this.exam =
                            this.exam || {};


                        this.exam.is_completed = true;


                        this.finishingExam = false;


                        this.screen = "result";


                        this.prepareResultChart();

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
        // RESULT
        // =========================================================

        loadResult() {

            if (!this.examId) {
                return;
            }


            if (
                !window.examBridge ||
                typeof window.examBridge.get_result !== "function"
            ) {

                return;
            }


            window.examBridge.get_result(
                Number(this.examId),
                (response) => {

                    try {

                        const data =
                            this.parseBridgeResponse(response);


                        if (!data.success) {

                            this.setError(
                                data.error ||
                                "Unable to load result."
                            );

                            return;
                        }


                        this.result =
                            data.result || null;


                        this.screen = "result";


                        this.prepareResultChart();

                    }
                    catch (error) {

                        console.error(
                            "Result response error:",
                            error
                        );

                        this.setError(
                            "Invalid result response."
                        );

                    }

                }
            );

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


            return (
                Number.isInteger(number)
                    ? `${number}%`
                    : `${number.toFixed(2)}%`
            );

        },


        // =========================================================
        // RESULT SUBJECTS
        // =========================================================

        get resultSubjects() {

            if (
                !this.result ||
                !Array.isArray(this.result.subjects)
            ) {

                return [];
            }


            return this.result.subjects;

        },


        // =========================================================
        // RESULT REVIEW
        // =========================================================

        get resultReview() {

            if (
                !this.result ||
                !Array.isArray(this.result.review)
            ) {

                return [];
            }


            return this.result.review;

        },


        // =========================================================
        // RESULT QUESTION HELPERS
        // =========================================================

        getReviewOption(question, optionId) {

            if (
                !question ||
                !Array.isArray(question.options) ||
                optionId === null ||
                optionId === undefined
            ) {
                return null;
            }

            return (
                question.options.find(
                    option =>
                        Number(option.id) === Number(optionId)
                ) || null
            );

        },


        // =========================================================
        // CORRECT OPTION
        // =========================================================

        getCorrectOption(question) {

            if (!question) {
                return null;
            }

            return this.getReviewOption(
                question,
                question.correct_option_id
            );

        },


        // =========================================================
        // STUDENT OPTION
        // =========================================================

        getStudentOption(question) {

            if (!question) {
                return null;
            }

            if (
                question.selected_option_id === null ||
                question.selected_option_id === undefined
            ) {
                return null;
            }

            return this.getReviewOption(
                question,
                question.selected_option_id
            );

        },


        // =========================================================
        // IS CORRECT
        // =========================================================

        questionIsCorrect(question) {

            if (!question) {
                return false;
            }

            const selected =
                question.selected_option_id;

            const correct =
                question.correct_option_id;

            if (
                selected === null ||
                selected === undefined ||
                correct === null ||
                correct === undefined
            ) {
                return false;
            }

            return (
                Number(selected) ===
                Number(correct)
            );

        },


        // =========================================================
        // IS UNANSWERED
        // =========================================================

        questionIsUnanswered(question) {

            if (!question) {
                return true;
            }

            return (
                question.selected_option_id === null ||
                question.selected_option_id === undefined
            );

        },


        // =========================================================
        // IS WRONG
        // =========================================================

        questionIsWrong(question) {

            if (
                !question ||
                this.questionIsUnanswered(question)
            ) {
                return false;
            }

            return !this.questionIsCorrect(question);

        },


        // =========================================================
        // STATUS TEXT
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
        // STATUS CLASS
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
                return "text-amber-800";
            }

            if (
                this.questionIsCorrect(question)
            ) {
                return "text-green-800";
            }

            return "text-red-800";

        },

        // =========================================================
        // REVIEW OPTION CLASS
        // =========================================================
        //
        // ONLY:
        // - correct answer => green
        // - student's wrong answer => red
        // - everything else => neutral
        //
        // =========================================================

        reviewOptionClass(question, option) {

            if (!question || !option) {
                return "border-gray-200 bg-white text-gray-700";
            }

            const optionId =
                Number(option.id);

            const correctId =
                question.correct_option_id === null ||
                question.correct_option_id === undefined
                    ? null
                    : Number(question.correct_option_id);

            const studentId =
                question.selected_option_id === null ||
                question.selected_option_id === undefined
                    ? null
                    : Number(question.selected_option_id);


            // Correct answer is always green.
            if (
                correctId !== null &&
                Number.isFinite(correctId) &&
                optionId === correctId
            ) {
                return "border-green-400 bg-green-50 text-green-900 ring-1 ring-green-300";
            }


            // Student selected the wrong answer.
            if (
                studentId !== null &&
                optionId === studentId &&
                optionId !== correctId
            ) {
                return "border-red-400 bg-red-50 text-red-900 ring-1 ring-red-300";
            }


            // All other options remain neutral.
            return "border-gray-200 bg-white text-gray-700";

        },


        // =========================================================
        // REVIEW OPTION LABEL CLASS
        // =========================================================

        reviewOptionLabelClass(question, option) {

            return this.reviewOptionClass(
                question,
                option
            );

        },

        // =========================================================
        // IS CORRECT OPTION
        // =========================================================

        isCorrectOption(option) {

            if (!this.activeReviewQuestion || !option) {
                return false;
            }

            return (
                this.activeReviewQuestion.correct_option_id !== null &&
                this.activeReviewQuestion.correct_option_id !== undefined &&
                Number(option.id) ===
                Number(
                    this.activeReviewQuestion.correct_option_id
                )
            );

        },


        // =========================================================
        // IS STUDENT OPTION
        // =========================================================

        isStudentOption(question, option) {

            if (!question || !option) {
                return false;
            }

            if (
                question.selected_option_id === null ||
                question.selected_option_id === undefined
            ) {
                return false;
            }

            return (
                Number(option.id) ===
                Number(question.selected_option_id)
            );

        },


        // =========================================================
        // STUDENT ANSWER TEXT
        // =========================================================

        studentAnswerText(question) {

            const option =
                this.getStudentOption(question);

            if (!option) {
                return "No answer selected.";
            }

            return `${option.label}. ${option.text}`;

        },


        // =========================================================
        // CORRECT ANSWER TEXT
        // =========================================================

        correctAnswerText(question) {

            const option =
                this.getCorrectOption(question);

            if (!option) {
                return "Correct answer not supplied.";
            }

            return `${option.label}. ${option.text}`;

        },

        // =========================================================
        // ACTIVE REVIEW QUESTION
        //
        // Used only defensively by isCorrectOption().
        // =========================================================

        activeReviewQuestion: null,
        

        // =========================================================
        // PREPARE CHART
        // =========================================================

        prepareResultChart() {

            this.$nextTick(() => {

                this.renderResultChart();

            });

        },

        // =========================================================
        // RENDER SUBJECT CHART
        // =========================================================

        renderResultChart() {

            const canvas =
                document.getElementById("resultSubjectChart") ||
                document.getElementById("resultBreakdownChart");

            if (!canvas) {
                return;
            }

            if (typeof window.Chart === "undefined") {

                console.warn(
                    "Chart.js is not available."
                );

                return;
            }


            // ---------------------------------------------------------
            // Destroy previous chart
            // ---------------------------------------------------------

            if (this.resultChart) {

                try {

                    this.resultChart.destroy();

                } catch (error) {

                    console.warn(
                        "Unable to destroy previous chart:",
                        error
                    );

                }

                this.resultChart = null;

            }


            // ---------------------------------------------------------
            // Result counts
            // ---------------------------------------------------------

            const correct =
                Number(this.result?.correct || 0);

            const wrong =
                Number(this.result?.wrong || 0);

            const unanswered =
                Number(this.result?.unanswered || 0);


            // ---------------------------------------------------------
            // Create chart
            // ---------------------------------------------------------

            this.resultChart = new Chart(
                canvas.getContext("2d"),
                {
                    type: "doughnut",

                    data: {

                        labels: [
                            "Correct",
                            "Wrong",
                            "Unanswered"
                        ],

                        datasets: [
                            {
                                data: [
                                    correct,
                                    wrong,
                                    unanswered
                                ],

                                backgroundColor: [
                                    "#16a34a",
                                    "#dc2626",
                                    "#9ca3af"
                                ],

                                borderWidth: 2,

                                borderColor: "#ffffff",
                            },
                        ],

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        plugins: {

                            legend: {

                                position: "bottom",

                                labels: {

                                    boxWidth: 12,

                                    padding: 14,

                                },

                            },

                        },

                    },

                }
            );

        },


        // =========================================================
        // PRINT HELPER (NATIVE & BROWSER IFRAME)
        // =========================================================

        printHtmlContent(html, title = "Mock CBT") {
            // First attempt: Qt WebChannel bridge native print dialog
            if (window.examBridge && typeof window.examBridge.print_html === "function") {
                showToast("Opening print dialog...", "info");
                try {
                    window.examBridge.print_html(html, title, (response) => {
                        try {
                            const data = this.parseBridgeResponse(response);
                            if (data && data.printed) {
                                showToast("Document sent to printer", "success");
                            }
                        } catch (e) {
                            console.error("Bridge print response parse error:", e);
                        }
                    });
                    return;
                } catch (bridgeErr) {
                    console.warn("Bridge print_html error, falling back to browser print:", bridgeErr);
                }
            }

            // Second attempt: Seamless hidden iframe printing (zero popup blocks)
            showToast("Preparing document for printing...", "info");
            let printIframe = document.getElementById('cbt-app-print-frame');
            if (!printIframe) {
                printIframe = document.createElement('iframe');
                printIframe.id = 'cbt-app-print-frame';
                printIframe.style.position = 'fixed';
                printIframe.style.right = '0';
                printIframe.style.bottom = '0';
                printIframe.style.width = '0';
                printIframe.style.height = '0';
                printIframe.style.border = '0';
                printIframe.style.visibility = 'hidden';
                document.body.appendChild(printIframe);
            }

            try {
                const iframeDoc = printIframe.contentDocument || (printIframe.contentWindow ? printIframe.contentWindow.document : null);
                if (iframeDoc) {
                    iframeDoc.open();
                    iframeDoc.write(html);
                    iframeDoc.close();

                    setTimeout(() => {
                        try {
                            if (printIframe.contentWindow) {
                                printIframe.contentWindow.focus();
                                printIframe.contentWindow.print();
                            }
                        } catch (err) {
                            console.warn("Iframe print invocation fallback to window.print():", err);
                            window.print();
                        }
                    }, 400);
                } else {
                    window.print();
                }
            } catch (err) {
                console.error("Iframe write error:", err);
                window.print();
            }
        },

        // =========================================================
        // PRINT RESULT
        // =========================================================

        printResult() {
            if (!this.result) return;
            showToast("Opening native print dialog...", "info");
            if (window.examBridge && typeof window.examBridge.print_current_page === "function") {
                window.examBridge.print_current_page((response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data && data.success) {
                            showToast("Document sent to printer successfully!", "success");
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
            if (!this.result) {
                showToast("No exam result available to download", "error");
                return;
            }

            if (!window.examBridge || typeof window.examBridge.generate_result_pdf_reportlab !== "function") {
                showToast("PDF generator bridge not available", "error");
                return;
            }

            const fullStudentName = this.result.student_full_name || this.result.student_name || "Student";
            const safeName = fullStudentName.replace(/[^a-zA-Z0-9 _-]/g, "").trim().replace(/\s+/g, "_") || "student";
            const year = this.result.year || "";
            const suggestedName = year ? `exam_result_${safeName}_${year}.pdf` : `exam_result_${safeName}.pdf`;

            const resultData = JSON.parse(JSON.stringify(this.result));
            resultData.student_name = fullStudentName;
            resultData.student_full_name = fullStudentName;

            showToast("Generating PDF report...", "info");

            window.examBridge.generate_result_pdf_reportlab(
                JSON.stringify(resultData),
                suggestedName,
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (!data.success) {
                            if (data.cancelled) return;
                            showToast(data.error || "Unable to download result PDF.", "error");
                        } else {
                            showToast(`Result PDF saved to ${data.name}`, "success");
                        }
                    } catch (error) {
                        console.error("Result PDF download error:", error);
                        showToast("Failed to download result PDF: " + error.message, "error");
                    }
                }
            );
        },

        // =========================================================
        // RETURN TO APP
        // =========================================================

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


        // =========================================================
        // RESTART APPLICATION
        // =========================================================

        restartApplication() {
            if (!window.examBridge || typeof window.examBridge.restart_application !== "function") {
                showToast("The Python bridge does not expose restart_application().", "error");
                return;
            }

            showToast("Restarting application...", "info");

            window.examBridge.restart_application(
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (!data.success) {
                            console.error("Restart failed:", data.error);
                            showToast(data.error || "Unable to restart application.", "error");
                        }
                    } catch (error) {
                        console.error("Restart response error:", error);
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

                this.screen = "selection";

                this.loadYears();

                return;
            }


            this.screen = "exam";

        },


        // =========================================================
        // BRIDGE RESPONSE PARSER
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
        // ADMIN FUNCTIONS
        // =========================================================

        searchStudents() {
            if (!window.examBridge || typeof window.examBridge.search_students !== "function") {
                this.setError("Student search is not available.");
                return;
            }

            window.examBridge.search_students(
                this.adminSearchName.trim(),
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            this.adminStudents = data.students || [];
                        } else {
                            this.setError(data.error || "Unable to search students.");
                        }
                    } catch (error) {
                        console.error("Student search error:", error);
                        this.setError("Failed to search students.");
                    }
                }
            );
        },

        loadAllStudents() {
            this.adminSearchName = "";
            this.adminCurrentPage = 1;
            this.searchStudents();
        },

        // Pagination computed properties
        get paginatedStudents() {
            const start = (this.adminCurrentPage - 1) * this.adminItemsPerPage;
            const end = start + this.adminItemsPerPage;
            return this.adminStudents.slice(start, end);
        },

        get totalPages() {
            return Math.max(
                1,
                Math.ceil(
                    this.adminStudents.length /
                    this.adminItemsPerPage
                )
            );
        },

        nextPage() {
            if (this.adminCurrentPage < this.totalPages) {
                this.adminCurrentPage++;
            }
        },

        prevPage() {
            if (this.adminCurrentPage > 1) {
                this.adminCurrentPage--;
            }
        },

        goToPage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.adminCurrentPage = page;
            }
        },

        viewStudentHistory(studentName) {
            // Student Exam Records tab history button - loads exam history using student's full name
            showToast(`Loading history for ${studentName}...`, "info");
            this.selectedStudentName = studentName;
            
            if (!window.examBridge || typeof window.examBridge.get_student_history !== "function") {
                showToast("Bridge not available for student history", "error");
                this.setError("Student history is not available.");
                return;
            }

            window.examBridge.get_student_history(
                studentName,
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            this.studentHistory = data.history || [];
                            this.showStudentHistory = true;
                            showToast(`Loaded ${this.studentHistory.length} history records`, "success");
                        } else {
                            showToast(data.error || "Unable to load student history", "error");
                            this.setError(data.error || "Unable to load student history.");
                        }
                    } catch (error) {
                        showToast("Failed to load student history", "error");
                        this.setError("Failed to load student history.");
                    }
                }
            );
        },

        viewUserHistory(fullName) {
            // User Accounts tab history button - delegates to same function as Student Exam Records
            // Both now use full_name to ensure consistent data loading
            this.viewStudentHistory(fullName);
        },

        deleteStudent(studentName) {
            this.studentToDelete = studentName;
            this.showDeleteStudentConfirmModal = true;
        },

        confirmDeleteStudent() {
            if (!this.studentToDelete) return;
            
            const studentName = this.studentToDelete;
            this.showDeleteStudentConfirmModal = false;
            this.studentToDelete = null;

            if (!window.examBridge || typeof window.examBridge.delete_student !== "function") {
                this.setError("Student deletion is not available.");
                return;
            }

            window.examBridge.delete_student(
                studentName,
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            this.adminStudents = this.adminStudents.filter(s => s.name !== studentName);
                            showToast(`Student ${studentName} deleted successfully.`, "success");
                        } else {
                            showToast(data.error || "Failed to delete student", "error");
                        }
                    } catch (error) {
                        console.error("Delete student error:", error);
                        showToast("Failed to delete student", "error");
                    }
                }
            );
        },
        formatDate(dateString) {
            if (!dateString) return "N/A";
            let date = new Date(dateString);
            if (isNaN(date.getTime())) {
                const m = String(dateString).match(/^(\d{1,2})-(\d{1,2})-(\d{4})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?/);
                if (m) {
                    date = new Date(
                        parseInt(m[3], 10),
                        parseInt(m[2], 10) - 1,
                        parseInt(m[1], 10),
                        parseInt(m[4], 10),
                        parseInt(m[5], 10),
                        m[6] ? parseInt(m[6], 10) : 0
                    );
                }
            }
            if (isNaN(date.getTime())) return String(dateString);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${day}/${month}/${year} ${hours}:${minutes}`;
        },

        printStudentHistory() {
            const historyTable = document.getElementById('student-history-table');
            if (!historyTable) {
                showToast("History table not found", "error");
                return;
            }
            if (!this.studentHistory || this.studentHistory.length === 0) {
                showToast("No history to print", "error");
                return;
            }

            const rows = this.studentHistory.map(h => {
                const subjects = (h.subjects || []).map(s =>
                    `<div style="display:flex;justify-content:space-between;font-size:13px;padding:2px 0;">
                        <span>${this.escapeHtml(s.name || '')}</span>
                        <span>${this.escapeHtml(s.correct + '/' + s.total)} (${this.escapeHtml(this.formatPercentage(s.percentage))})</span>
                    </div>`
                ).join('');
                return `<tr style="border-bottom:1px solid #ddd;">
                    <td style="padding:10px 8px;text-align:left;">${this.escapeHtml(this.formatDate(h.completed_at))}</td>
                    <td style="padding:10px 8px;text-align:center;">${this.escapeHtml(h.year || '-')}</td>
                    <td style="padding:10px 8px;text-align:left;">${subjects || '-'}</td>
                    <td style="padding:10px 8px;text-align:center;">${this.escapeHtml(h.correct + '/' + h.total)}</td>
                    <td style="padding:10px 8px;text-align:center;font-weight:600;">${this.escapeHtml(this.formatPercentage(h.percentage))}</td>
                </tr>`;
            }).join('');

            const logoUrl = this.getSchoolLogoUrl();
            const schoolName = this.appSettings.school_name || 'Mock CBT Examination';
            const schoolAddress = this.appSettings.school_address || '';

            const html = `
                <html>
                <head>
                    <title>Student History - ${this.escapeHtml(this.selectedStudentName || 'Student')}</title>
                    <style>
                        * { box-sizing: border-box; }
                        body { font-family: Arial, sans-serif; padding: 30px; margin: 0; color: #1f2937; }
                        .header-wrap { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 14px; }
                        .logo-img { height: 60px; width: 60px; object-fit: contain; }
                        .school-title { font-size: 20px; font-weight: 800; color: #1e3a8a; text-transform: uppercase; margin: 0; }
                        .school-addr { font-size: 11px; color: #64748b; margin-top: 2px; }
                        .doc-type { font-size: 13px; font-weight: 700; color: #2563eb; text-transform: uppercase; margin-top: 4px; }
                        h1 { margin: 15px 0 10px 0; font-size: 18px; color: #0f172a; }
                        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }
                        th, td { border: 1px solid #e5e7eb; padding: 9px 8px; vertical-align: top; }
                        th { background-color: #1e3a8a; color: white; text-align: left; font-weight: 600; }
                        th:nth-child(2), th:nth-child(4), th:nth-child(5) { text-align: center; }
                        @media print {
                            body { padding: 10px; }
                            th { background-color: #1e3a8a !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                        }
                    </style>
                </head>
                <body>
                    <div class="header-wrap">
                        <img src="${logoUrl}" class="logo-img" alt="School Logo" onerror="this.style.display='none'">
                        <div>
                            <div class="school-title">${this.escapeHtml(schoolName)}</div>
                            ${schoolAddress ? `<div class="school-addr">${this.escapeHtml(schoolAddress)}</div>` : ''}
                            <div class="doc-type">Official Candidate Examination Transcript</div>
                        </div>
                    </div>
                    <h1>Candidate: <strong>${this.escapeHtml(this.selectedStudentName || 'Student')}</strong></h1>
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th style="text-align:center;">Year</th>
                                <th>Subject Breakdown</th>
                                <th style="text-align:center;">Total Score</th>
                                <th style="text-align:center;">Overall %</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                </body>
                </html>
            `;

            this.printHtmlContent(html, `Student History - ${this.selectedStudentName || 'Student'}`);
        },

        downloadStudentHistoryPDF() {
            if (!this.studentHistory || this.studentHistory.length === 0) {
                showToast("No history available to download", "error");
                return;
            }
            if (!this.selectedStudentName) {
                showToast("Student name not available", "error");
                return;
            }

            if (!window.examBridge || typeof window.examBridge.generate_student_history_pdf_reportlab !== "function") {
                showToast("History PDF download is not available. Bridge not connected.", "error");
                return;
            }

            const safeName = this.selectedStudentName.replace(/[^a-zA-Z0-9 _-]/g, "").trim() || "student";
            const defaultName = `${safeName}_history.pdf`;

            window.examBridge.generate_student_history_pdf_reportlab(
                this.selectedStudentName,
                JSON.stringify(this.studentHistory),
                defaultName,
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (!data.success) {
                            if (data.cancelled) return;
                            showToast(data.error || "Unable to download history PDF.", "error");
                        } else {
                            showToast(`History PDF saved to ${data.name}`, "success");
                        }
                    } catch (error) {
                        console.error("History PDF download error:", error);
                        showToast("Failed to download history PDF: " + error.message, "error");
                    }
                }
            );
        },

        // =========================================================
        // USER MANAGEMENT
        // =========================================================

        loadUsers() {
            if (!window.examBridge || typeof window.examBridge.get_all_users !== "function") {
                showToast("User management not available", "error");
                return;
            }

            window.examBridge.get_all_users((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.users = data.users || [];
                    } else {
                        showToast(data.error || "Unable to load users", "error");
                    }
                } catch (error) {
                    console.error("Load users error:", error);
                    showToast("Failed to load users", "error");
                }
            });
        },

        saveUser() {
            if (!window.examBridge) {
                showToast("User management not available", "error");
                return;
            }

            const method = this.userModalMode === 'create' ? 'create_user' : 'update_user';
            const args = this.userModalMode === 'create'
                ? [
                    this.userForm.username,
                    this.userForm.password,
                    this.userForm.full_name,
                    this.userForm.role,
                    this.userForm.student_class,
                    this.userForm.admission_year,
                  ]
                : [
                    this.editingUserId,
                    this.userForm.full_name,
                    this.userForm.role,
                    this.userForm.student_class,
                    this.userForm.admission_year,
                    String(this.userForm.is_active),
                    this.userForm.password,
                  ];

            window.examBridge[method](...args, (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        showToast(`User ${this.userModalMode === 'create' ? 'created' : 'updated'} successfully`, "success");
                        this.showUserModal = false;
                        this.resetUserForm();
                        this.loadUsers();
                    } else {
                        showToast(data.error || "Operation failed", "error");
                    }
                } catch (error) {
                    console.error("Save user error:", error);
                    showToast("Failed to save user", "error");
                }
            });
        },

        editUser(user) {
            this.userModalMode = 'edit';
            this.editingUserId = user.id;
            this.showUserPassword = false;
            this.userForm = {
                username: user.username,
                password: "",
                full_name: user.full_name,
                role: user.role,
                student_class: user.student_class || "",
                admission_year: user.admission_year || "",
                is_active: user.is_active,
                logo_path: user.logo_path || "",
            };
            this.showUserModal = true;
        },

        deleteUser(userId) {
            this.userToDelete = userId;
            this.showDeleteConfirmModal = true;
        },

        confirmDeleteUser() {
            if (!this.userToDelete) return;
            
            const userId = this.userToDelete;
            this.showDeleteConfirmModal = false;
            this.userToDelete = null;

            if (!window.examBridge || typeof window.examBridge.delete_user !== "function") {
                showToast("User management not available", "error");
                return;
            }

            window.examBridge.delete_user(String(userId), (response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        showToast("User deleted successfully", "success");
                        this.loadUsers();
                    } else {
                        showToast(data.error || "Failed to delete user", "error");
                    }
                } catch (error) {
                    console.error("Delete user error:", error);
                    showToast("Failed to delete user", "error");
                }
            });
        },

        resetUserForm() {
            this.showUserPassword = false;
            this.userForm = {
                username: "",
                password: "",
                full_name: "",
                role: "student",
                student_class: "",
                admission_year: "",
                is_active: true,
            };
            this.editingUserId = null;
        },

        // =========================================================
        // APP SETTINGS
        // =========================================================

        getSchoolLogoUrl() {
            if (this.appSettings && this.appSettings.school_logo_path) {
                const path = this.appSettings.school_logo_path;
                if (path.startsWith("data:image")) return path;
                return path.includes("?") ? path : `${path}?v=${this.logoVersion}`;
            }
            return "images/school_logo.png";
        },

        loadAppSettings() {
            if (!window.examBridge || typeof window.examBridge.get_app_settings !== "function") {
                console.warn("App settings bridge not available");
                return;
            }

            window.examBridge.get_app_settings((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        this.appSettings = data.settings;
                        this.settingsForm = { ...data.settings };
                        this.logoVersion = Date.now();
                        this.applyTheme(data.settings.theme);
                    }
                } catch (error) {
                    console.error("Failed to load app settings:", error);
                }
            });
        },

        openSettingsModal() {
            this.settingsForm = { ...this.appSettings };
            this.showSettingsModal = true;
        },

        saveSettings() {
            if (!window.examBridge || typeof window.examBridge.update_app_settings !== "function") {
                showToast("Settings not available", "error");
                return;
            }

            window.examBridge.update_app_settings(
                this.settingsForm.school_name,
                this.settingsForm.school_address,
                this.settingsForm.school_logo_path,
                this.settingsForm.theme,
                (response) => {
                    try {
                        const data = this.parseBridgeResponse(response);
                        if (data.success) {
                            this.appSettings = data.settings;
                            this.logoVersion = Date.now();
                            this.showSettingsModal = false;
                            this.applyTheme(data.settings.theme);
                            showToast("Settings saved successfully", "success");
                        } else {
                            showToast(data.error || "Failed to save settings", "error");
                        }
                    } catch (error) {
                        console.error("Save settings error:", error);
                        showToast("Failed to save settings", "error");
                    }
                }
            );
        },

        handleSettingsLogoUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Check file size (max 2MB)
            if (file.size > 2 * 1024 * 1024) {
                showToast("Logo file must be less than 2MB", "error");
                event.target.value = "";
                return;
            }

            // Check file type
            if (!file.type.startsWith("image/")) {
                showToast("Logo must be an image file", "error");
                event.target.value = "";
                return;
            }

            // Read file and convert to base64 for preview
            const reader = new FileReader();
            reader.onload = (e) => {
                this.settingsForm.school_logo_path = e.target.result;
                this.logoVersion = Date.now();
            };
            reader.readAsDataURL(file);
        },

        applyTheme(theme) {
            const currentTheme = theme || 'light';
            document.documentElement.setAttribute('data-theme', currentTheme);
            if (this.appSettings) {
                this.appSettings.theme = currentTheme;
            }
            try {
                localStorage.setItem('cbt_theme', currentTheme);
            } catch (e) {}
        },

        toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme') || (this.appSettings && this.appSettings.theme) || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            this.applyTheme(next);
            if (this.settingsForm) {
                this.settingsForm.theme = next;
            }
            if (this.currentUser && this.currentUser.role === 'admin' && window.examBridge && typeof window.examBridge.update_app_settings === 'function') {
                window.examBridge.update_app_settings(
                    this.appSettings.school_name,
                    this.appSettings.school_address,
                    this.appSettings.school_logo_path,
                    next,
                    () => {}
                );
            }
            showToast(`Switched to ${next === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
        },

        backupDatabase() {
            if (!window.examBridge || typeof window.examBridge.backup_database !== "function") {
                showToast("Backup not available", "error");
                return;
            }

            if (!confirm("Are you sure you want to create a database backup?")) {
                return;
            }

            window.examBridge.backup_database((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        showToast(`Database backed up to ${data.backup_path}`, "success");
                    } else {
                        showToast(data.error || "Backup failed", "error");
                    }
                } catch (error) {
                    console.error("Backup error:", error);
                    showToast("Backup failed", "error");
                }
            });
        },

        // =========================================================
        // USER FILTERING & PAGINATION
        // =========================================================

        get availableUserClasses() {
            const classes = new Set();
            (this.users || []).forEach(u => {
                if (u.student_class && String(u.student_class).trim()) {
                    classes.add(String(u.student_class).trim());
                }
            });
            return Array.from(classes).sort();
        },

        get filteredUsers() {
            let list = this.users || [];
            const query = (this.userSearchQuery || "").trim().toLowerCase();
            const role = this.userRoleFilter || "all";
            const userClass = this.userClassFilter || "all";

            return list.filter(user => {
                if (role !== "all" && (user.role || "").toLowerCase() !== role.toLowerCase()) {
                    return false;
                }
                if (userClass !== "all" && (user.student_class || "").toLowerCase() !== userClass.toLowerCase()) {
                    return false;
                }
                if (query) {
                    const matchName = (user.full_name || "").toLowerCase().includes(query);
                    const matchUsername = (user.username || "").toLowerCase().includes(query);
                    const matchRole = (user.role || "").toLowerCase().includes(query);
                    const matchClass = (user.student_class || "").toLowerCase().includes(query);
                    const matchYear = String(user.admission_year || "").toLowerCase().includes(query);
                    if (!matchName && !matchUsername && !matchRole && !matchClass && !matchYear) {
                        return false;
                    }
                }
                return true;
            });
        },

        get paginatedUsers() {
            const start = (this.userCurrentPage - 1) * this.userItemsPerPage;
            const end = start + this.userItemsPerPage;
            return this.filteredUsers.slice(start, end);
        },

        get userTotalPages() {
            return Math.max(1, Math.ceil(this.filteredUsers.length / this.userItemsPerPage));
        },

        resetUserFilters() {
            this.userSearchQuery = "";
            this.userRoleFilter = "all";
            this.userClassFilter = "all";
            this.userCurrentPage = 1;
        },

        // =========================================================
        // QUESTION IMPORT
        // =========================================================

        handleImportClick() {
            if (this.screen === 'exam' && !this.result) {
                showToast("Navigation is disabled during exam", "warning");
                return;
            }
            if (!this.isAdmin) {
                showToast("Please login as admin to access Question Import", "warning");
                this.showLoginModal = true;
                return;
            }
            this.screen = 'import';
        },

        launchQuestionImport() {
            if (!window.examBridge || typeof window.examBridge.launch_question_import !== "function") {
                showToast("Question import not available", "error");
                return;
            }

            window.examBridge.launch_question_import((response) => {
                try {
                    const data = this.parseBridgeResponse(response);
                    if (data.success) {
                        showToast("Question import window launched", "success");
                    } else {
                        showToast(data.error || "Failed to launch question import", "error");
                    }
                } catch (error) {
                    console.error("Launch question import error:", error);
                    showToast("Failed to launch question import", "error");
                }
            });
        },

        // =========================================================
        // GENERAL KNOWLEDGE CHAT
        // =========================================================

        showChat: false,
        chatMessages: [],
        chatInput: "",
        chatLoading: false,
        chatError: "",
        chatProvider: "",

        openGeneralKnowledge() {
            this.showChat = true;
            this.chatError = "";
            if (!this.chatMessages.length) {
                this.chatMessages = [{
                    role: "assistant",
                    content: "Hello! I'm your AI companion. Ask me anything — education, history, technology, religion, lifestyle, career, or just life in general. I'm here to help you grow! 🌟"
                }];
            }
            this.$nextTick(() => {
                const el = document.getElementById("chat-messages");
                if (el) el.scrollTop = el.scrollHeight;
                const input = document.getElementById("chat-input");
                if (input) input.focus();
            });
        },

        closeChat() {
            this.showChat = false;
        },

        refreshChat() {
            this.chatMessages = [{
                role: "assistant",
                content: "Hello! I'm your AI companion. Ask me anything — education, history, technology, religion, lifestyle, career, or just life in general. I'm here to help you grow! 🌟"
            }];
            this.chatError = "";
            this.chatProvider = "";
            this.$nextTick(() => {
                const el = document.getElementById("chat-messages");
                if (el) el.scrollTop = el.scrollHeight;
                const input = document.getElementById("chat-input");
                if (input) input.focus();
            });
        },

        _scrollChatToBottom() {
            this.$nextTick(() => {
                const el = document.getElementById("chat-messages");
                if (el) el.scrollTop = el.scrollHeight;
            });
        },

        async sendChatMessage() {
            const text = (this.chatInput || "").trim();
            if (!text || this.chatLoading) return;

            this.chatInput = "";
            this.chatError = "";
            this.chatMessages.push({ role: "user", content: text });
            this.chatLoading = true;
            this._scrollChatToBottom();

            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 45000);

            try {
                const response = await fetch("http://127.0.0.1:8000/api/v1/tutor/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    signal: controller.signal,
                    body: JSON.stringify({
                        message: text,
                        history: this.chatMessages.slice(-20).map(m => ({
                            role: m.role,
                            content: m.content,
                        })),
                    }),
                });

                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.detail || `Request failed (${response.status})`);
                }

                const data = await response.json();
                this.chatProvider = data.provider || "";
                this.chatMessages.push({ role: "assistant", content: data.reply || "" });

            } catch (err) {
                if (err.name === "AbortError") {
                    this.chatError = "Request timed out. The AI service may be unavailable. Please try again.";
                } else {
                    this.chatError = err.message || "Unable to reach the AI. Please try again.";
                }
            } finally {
                clearTimeout(timeout);
                this.chatLoading = false;
                this._scrollChatToBottom();
                this.$nextTick(() => {
                    const input = document.getElementById("chat-input");
                    if (input) input.focus();
                });
            }
        },

        chatInputKeydown(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                this.sendChatMessage();
            }
        },

        async askAITutor(question) {

                if (!question) {
                    return;
                }

                // Prevent duplicate requests while one is already running
                if (this.tutorLoading) {
                    return;
                }

                this.tutorLoading = true;

                // Open the existing tutor modal immediately
                this.showTutor = true;

                // Store question for retry
                this.tutorQuestion = question;

                // Clear previous response while the new request is loading
                this.tutorResponse = null;

                try {

                    const response = await fetch(
                        "http://127.0.0.1:8000/api/v1/tutor/ask",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type": "application/json",
                            },

                            body: JSON.stringify({
                                subject: question.subject_name || "",

                                question: question.text || "",

                                options: Array.isArray(question.options)
                                    ? question.options.map(option => ({
                                        label: option.label || "",
                                        text: option.text || "",
                                    }))
                                    : [],

                                correct_answer: this.getCorrectOption(question)?.text || "",

                                student_answer: this.getStudentOption(question)?.text || "",

                                explanation: question.explanation || "",
                            }),
                        }
                    );

                    if (!response.ok) {

                        let errorMessage =
                            `AI Tutor request failed (${response.status})`;

                        try {
                            const errorData = await response.json();

                            if (errorData?.detail) {
                                errorMessage = errorData.detail;
                            }
                        } catch (_) {
                            // Ignore invalid error JSON
                        }

                        throw new Error(errorMessage);
                    }

                    const data = await response.json();

                    if (!data || data.success !== true) {
                        throw new Error(
                            data?.detail ||
                            "AI Tutor returned an invalid response."
                        );
                    }

                    // Store the complete structured response
                    this.tutorResponse = data;

                } catch (error) {

                    console.error("AI Tutor error:", error);

                    this.tutorResponse = {
                        success: false,
                        answer: "",
                        greeting: "",
                        explanation: "",
                        steps: [],
                        hint: "",
                        encouragement: "",
                        follow_up_question: "",
                        error:
                            error?.message ||
                            "Unable to connect to the AI Tutor.",
                    };

                } finally {

                    // IMPORTANT:
                    // This always runs whether Gemini succeeds,
                    // Ollama succeeds, or all providers fail.
                    this.tutorLoading = false;
                }
        },

        // =========================================================
        // AI TUTOR AVATAR
        // =========================================================

        setTutorAvatarState(state) {
            this.tutorAvatarState = state;
        },

        startTutorSpeaking() {
            this.tutorSpeaking = true;
            this.tutorAvatarState = "speaking";
        },

        stopTutorSpeaking() {
            this.tutorSpeaking = false;
            this.tutorAvatarState = "idle";
        },

        // =========================================================
        // CLOSE AI TUTOR
        // =========================================================

        closeAITutor() {
            this.stopTutorSpeech();
            this.showTutor = false;
            document.body.classList.remove("overflow-hidden");
        },

        // ===========Newly adopted pipeline========================
        // AI TUTOR SPEECH
        // =========================================================

        async speakTutorResponse() {

            if (!this.tutorResponse) {
                return;
            }

            const text =
                this.getTutorSpeechText();

            if (!text.trim()) {
                return;
            }

            this.tutorError = "";

            const loaded =
                await this.loadTutorAudio(
                    text
                );

            if (!loaded) {
                return;
            }

            try {

                if (
                    this.tutorAudioContext &&
                    this.tutorAudioContext.state === "suspended"
                ) {
                    await this.tutorAudioContext.resume();
                }

                this.tutorSpeaking = true;
                this.tutorPaused = false;
                this.tutorAvatarState = "speaking";

                this.tutorAudio.onplay = () => {

                    this.tutorSpeaking = true;
                    this.tutorPaused = false;
                    this.tutorAvatarState =
                        "speaking";

                    // Small delay to ensure audio is actually playing before starting lip sync
                    setTimeout(() => {
                        if (this.tutorSpeaking && !this.tutorAudio.paused) {
                            this.startTutorLipSync();
                        }
                    }, 100);
                };

                this.tutorAudio.onpause = () => {

                    if (
                        this.tutorAudio &&
                        !this.tutorAudio.ended
                    ) {

                        this.tutorPaused = true;
                        this.tutorSpeaking = false;
                        this.tutorAvatarState =
                            "idle";

                        this.stopTutorLipSync();
                    }
                };

                this.tutorAudio.onended = () => {

                    this.tutorSpeaking = false;
                    this.tutorPaused = false;
                    this.tutorAvatarState =
                        "idle";

                    this.stopTutorLipSync();
                };

                this.tutorAudio.onerror = (event) => {

                    console.error(
                        "Tutor audio playback error:",
                        event
                    );

                    this.tutorSpeaking = false;
                    this.tutorPaused = false;
                    this.tutorAvatarState =
                        "idle";

                    this.stopTutorLipSync();

                    this.tutorError =
                        "The tutor speech could not be played.";
                };

                await this.tutorAudio.play();

            } catch (error) {

                console.error(
                    "Tutor speech playback error:",
                    error
                );

                this.tutorSpeaking = false;
                this.tutorPaused = false;
                this.tutorAvatarState =
                    "idle";

                this.stopTutorLipSync();

                this.tutorError =
                    "Unable to play tutor speech.";
            }
        },

        // =========================================================
        // RETRY AI TUTOR
        // =========================================================

        retryAITutor() {

            if (!this.tutorQuestion) {
                return;
            }

            this.askAITutor(
                this.tutorQuestion
            );
        },


        // =========================================================
        // AI TUTOR — TEXT TO SPEECH
        // =========================================================

        initTutorSpeech() {
            if (
                typeof window === "undefined" ||
                !("speechSynthesis" in window) ||
                !("SpeechSynthesisUtterance" in window)
            ) {
                this.tutorSpeechSupported = false;
                return;
            }

            this.tutorSpeechSupported = true;

            const loadVoices = () => {
                this.tutorVoices = window.speechSynthesis.getVoices();

                if (!this.tutorSelectedVoice && this.tutorVoices.length) {
                    this.tutorSelectedVoice =
                        this.getPreferredTutorVoice(this.tutorVoices);
                }
            };

            loadVoices();

            if ("onvoiceschanged" in window.speechSynthesis) {
                window.speechSynthesis.onvoiceschanged = loadVoices;
            }
        },


        getPreferredTutorVoice(voices) {
            if (!Array.isArray(voices) || !voices.length) {
                return null;
            }

            // Prefer an English voice.
            const englishVoice = voices.find(
                voice =>
                    typeof voice.lang === "string" &&
                    voice.lang.toLowerCase().startsWith("en")
            );

            return englishVoice || voices[0];
        },


        getTutorSpeechText() {
            if (!this.tutorResponse) {
                return "";
            }

            const parts = [];

            if (this.tutorResponse.greeting) {
                parts.push(this.tutorResponse.greeting);
            }

            if (this.tutorResponse.explanation) {
                parts.push(this.tutorResponse.explanation);
            }

            if (Array.isArray(this.tutorResponse.steps)) {
                this.tutorResponse.steps.forEach(
                    (step, index) => {
                        if (step) {
                            parts.push(
                                `Step ${index + 1}. ${step}`
                            );
                        }
                    }
                );
            }

            if (this.tutorResponse.hint) {
                parts.push(
                    `Hint. ${this.tutorResponse.hint}`
                );
            }

            if (this.tutorResponse.encouragement) {
                parts.push(
                    this.tutorResponse.encouragement
                );
            }

            if (this.tutorResponse.follow_up_question) {
                parts.push(
                    `Think about this. ${this.tutorResponse.follow_up_question}`
                );
            }

            return parts
                .filter(Boolean)
                .join(". ");
        },


        // =========================================================
        // AI TUTOR — AUDIO LIP SYNC
        // =========================================================

        initTutorLipSync() {

            if (this.tutorAudioContext) {
                return;
            }

            try {

                const AudioContext =
                    window.AudioContext ||
                    window.webkitAudioContext;

                if (!AudioContext) {
                    console.warn(
                        "Web Audio API is not available."
                    );
                    return;
                }

                this.tutorAudioContext =
                    new AudioContext();

                this.tutorAnalyser =
                    this.tutorAudioContext.createAnalyser();

                this.tutorAnalyser.fftSize = 2048;

                this.tutorAnalyser.smoothingTimeConstant = 0.55;

                this.tutorAudioData =
                    new Uint8Array(
                        this.tutorAnalyser.frequencyBinCount
                    );

            } catch (error) {

                console.error(
                    "Tutor lip-sync initialization failed:",
                    error
                );

            }
        },

        // =================================
        // Load Tutor Audio
        // =================================

        async loadTutorAudio(text) {

            if (!text || !text.trim()) {
                return false;
            }

            this.stopTutorSpeech();

            this.initTutorLipSync();

            try {

                if (
                    this.tutorAudioContext &&
                    this.tutorAudioContext.state === "suspended"
                ) {
                    await this.tutorAudioContext.resume();
                }

                const response = await fetch(
                    "http://127.0.0.1:8000/api/v1/tutor/speak",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            text: text,
                        }),
                    }
                );
                
                if (!response.ok) {

                    throw new Error(
                        `TTS request failed: HTTP ${response.status}`
                    );

                }

                const audioBlob =
                    await response.blob();

                if (this.tutorAudioURL) {

                    URL.revokeObjectURL(
                        this.tutorAudioURL
                    );

                    this.tutorAudioURL = null;
                }

                this.tutorAudioURL =
                    URL.createObjectURL(
                        audioBlob
                    );

                this.tutorAudio =
                    new Audio();

                this.tutorAudio.preload = "auto";

                this.tutorAudio.src =
                    this.tutorAudioURL;

                this.tutorAudio.volume = 1;

                await new Promise(
                    (resolve, reject) => {

                        this.tutorAudio.oncanplaythrough =
                            resolve;

                        this.tutorAudio.onerror =
                            () => reject(
                                new Error(
                                    "Tutor audio could not be loaded."
                                )
                            );

                        this.tutorAudio.load();

                    }
                );

                this.connectTutorAudio();

                return true;

            } catch (error) {

                console.error(
                    "Tutor audio loading error:",
                    error
                );

                this.tutorError =
                    "The tutor speech could not be generated.";

                return false;
            }
        },


        // ====================================
        // Connect the audio to the analyser
        // ====================================

        connectTutorAudio() {

            if (
                !this.tutorAudio ||
                !this.tutorAudioContext ||
                !this.tutorAnalyser
            ) {
                return;
            }

            try {

                // Disconnect previous source if it exists
                if (this.tutorAudioSource) {
                    try { this.tutorAudioSource.disconnect(); } catch (_) {}
                    this.tutorAudioSource = null;
                }

                // Each new Audio() element needs its own MediaElementSource
                this.tutorAudioSource =
                    this.tutorAudioContext.createMediaElementSource(
                        this.tutorAudio
                    );

                this.tutorAudioSource.connect(this.tutorAnalyser);
                this.tutorAnalyser.connect(this.tutorAudioContext.destination);

                this.tutorAudioReady = true;

            } catch (error) {
                console.error("Tutor audio analyser connection failed:", error);
                // Still mark ready so audio plays even without lip sync
                this.tutorAudioReady = true;
            }
        },


        // ========================================
        // Frequency-band analysis
        // =========================================

        analyseTutorAudio() {

            if (
                !this.tutorAnalyser ||
                !this.tutorAudioData
            ) {
                return;
            }

            this.tutorAnalyser.getByteFrequencyData(
                this.tutorAudioData
            );

            const sampleRate =
                this.tutorAudioContext.sampleRate;

            const fftSize =
                this.tutorAnalyser.fftSize;

            const binWidth =
                sampleRate / fftSize;

            const energy = (
                minHz,
                maxHz
            ) => {

                const start =
                    Math.max(
                        0,
                        Math.floor(minHz / binWidth)
                    );

                const end =
                    Math.min(
                        this.tutorAudioData.length - 1,
                        Math.ceil(maxHz / binWidth)
                    );

                if (end <= start) {
                    return 0;
                }

                let total = 0;

                for (
                    let i = start;
                    i <= end;
                    i++
                ) {

                    total +=
                        this.tutorAudioData[i];
                }

                return (
                    total /
                    ((end - start + 1) * 255)
                );
            };

            const low =
                energy(80, 300);

            const mid =
                energy(300, 1200);

            const high =
                energy(1200, 4000);

            const veryHigh =
                energy(4000, 8000);

            const overall =
                (low * 0.25) +
                (mid * 0.40) +
                (high * 0.25) +
                (veryHigh * 0.10);

            this.updateTutorViseme({
                low,
                mid,
                high,
                veryHigh,
                overall,
            });
        },


        // =========================================================
        // VISEMO ESTIMATOR
        // =========================================================

        updateTutorViseme({
            low,
            mid,
            high,
            veryHigh,
            overall,
        }) {

            if (!this.tutorSpeaking) {
                this.setTutorViseme(
                    "closed",
                    0
                );

                return;
            }

            const mouthOpen =
                Math.min(
                    1,
                    Math.max(
                        0,
                        (overall - 0.015) * 3.5
                    )
                );

            this.tutorMouthOpen =
                this.smoothTutorValue(
                    this.tutorMouthOpen,
                    mouthOpen,
                    0.45
                );

            let viseme;

            /*
            * Approximate acoustic mouth categories.
            *
            * This is not pretending to recover exact
            * phonemes from the waveform.
            *
            * It identifies useful speech shapes:
            *
            * closed
            * narrow
            * open
            * wide
            * rounded
            */

            if (overall < 0.015) {

                viseme = "closed";

            } else if (
                mouthOpen < 0.15
            ) {

                viseme = "narrow";

            } else if (
                low > mid * 1.15 &&
                low > high * 1.25
            ) {

                viseme = "rounded";

            } else if (
                high > mid * 1.10 &&
                high > low * 1.05
            ) {

                viseme = "wide";

            } else if (
                mouthOpen > 0.65
            ) {

                viseme = "open";

            } else {

                viseme = "mid";
            }

            this.setTutorViseme(
                viseme,
                this.tutorMouthOpen
            );
        },


        // ========================================================
        // SMOOTHING THE MOUTH
        // =========================================================
        
        smoothTutorValue(
            current,
            target,
            amount = 0.35
        ) {

            return (
                current +
                ((target - current) * amount)
            );
        },


        // ===========================================
        // DECLARING VISEME
        // ==================finally==================

        setTutorViseme(
            viseme,
            amount = 0
        ) {

            this.tutorViseme = viseme;

            this.tutorMouthOpen =
                Math.max(
                    0,
                    Math.min(
                        1,
                        amount
                    )
                );
        },


        // ================================================
        // START THE ANALYSIS LOOP
        // ===============speech in action==================

        startTutorLipSync() {

            this.stopTutorLipSync();

            const tick = () => {

                if (
                    !this.tutorAudio ||
                    this.tutorAudio.paused ||
                    this.tutorAudio.ended
                ) {

                    this.setTutorViseme(
                        "closed",
                        0
                    );

                    return;
                }

                this.analyseTutorAudio();

                this.tutorLipSyncFrame =
                    requestAnimationFrame(
                        tick
                    );
            };

            this.tutorLipSyncFrame =
                requestAnimationFrame(
                    tick
                );
        },

        // ================================================
        // STOP THE ANALYSIS LOOP
        // ===============speech OVER==================

        stopTutorLipSync() {

            if (this.tutorLipSyncFrame) {

                cancelAnimationFrame(
                    this.tutorLipSyncFrame
                );

                this.tutorLipSyncFrame =
                    null;
            }

            this.setTutorViseme(
                "closed",
                0
            );
        },

        // =========================================
        // PAUSE TUTOR SPEECH
        // =======================================

        pauseTutorSpeech() {

            if (
                !this.tutorAudio ||
                this.tutorAudio.paused
            ) {
                return;
            }

            this.tutorAudio.pause();

            this.tutorSpeaking = false;
            this.tutorPaused = true;
            this.tutorAvatarState = "idle";

            this.stopTutorLipSync();
        },

        // ==============================================
        // RESUME TUTOR SPEECH
        // ==============================================

        async resumeTutorSpeech() {

            if (
                !this.tutorAudio ||
                !this.tutorAudio.paused ||
                this.tutorAudio.ended
            ) {
                return;
            }

            try {

                if (
                    this.tutorAudioContext &&
                    this.tutorAudioContext.state === "suspended"
                ) {
                    await this.tutorAudioContext.resume();
                }

                await this.tutorAudio.play();

                this.tutorSpeaking = true;
                this.tutorPaused = false;
                this.tutorAvatarState =
                    "speaking";

                this.startTutorLipSync();

            } catch (error) {

                console.error(
                    "Tutor resume error:",
                    error
                );
            }
        },


        // =============================================
        // STOP TUTOR SPEECH
        // =============================================

        stopTutorSpeech() {

            if (this.tutorAudio) {

                try {
                    this.tutorAudio.pause();
                } catch (_) {}

                try {
                    this.tutorAudio.currentTime = 0;
                } catch (_) {}
            }

            this.stopTutorLipSync();

            this.tutorSpeaking = false;
            this.tutorPaused = false;
            this.tutorAvatarState = "idle";

            if (this.tutorAudioURL) {

                URL.revokeObjectURL(
                    this.tutorAudioURL
                );

                this.tutorAudioURL = null;
            }

            this.tutorAudio = null;
        },

        // ================================
        // CLOSE TUTOR SPEECH NEWLY ADOPTED
        // ================================

        closeTutor() {
            this.stopTutorSpeech();

            this.showTutor = false;

            document.body.classList.remove(
                "overflow-hidden"
            );
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

                    console.warn(error);

                }

                this.resultChart = null;

            }

        },

        // =========================================================
        // AI TUTOR ESCAPE KEY
        // =========================================================

        handleTutorEscape(event) {

            if (
                event.key === "Escape" &&
                this.showTutorModal
            ) {
                this.closeAITutor();
            }
        },

    }));

});




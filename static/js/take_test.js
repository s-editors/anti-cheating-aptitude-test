// Take Test JavaScript - Simplified and Debugged Version
console.log('Take Test JavaScript loaded');

document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM Content Loaded - Take Test JavaScript starting...');

    // ================================
    // Initialize variables
    // ================================
    let warningCount = 0;
    let testFinished = false;
    const warningContainer = document.getElementById('warningContainer');
    const warningCountInput = document.getElementById('warning_count');
    const testForm = document.getElementById('test-form');
    const currentQuestionInput = document.getElementById('current_question');
    let currentQuestion = 1;
    
    // Warning sound setup (plays for 5 seconds then stops)
    // Ensure you have a file at: static/sounds/warning.mp3
    let warningSoundTimeout = null;
    const warningSound = (function createWarningAudio() {
        try {
            const audio = new Audio('/static/sounds/alarm-301729.mp3');
            audio.preload = 'auto';
            return audio;
        } catch (e) {
            console.warn('Audio initialization failed:', e);
            return null;
        }
    })();
    
    // Get data from form attributes
    const totalQuestions = testForm ? (parseInt(testForm.dataset.totalQuestions) || 0) : 0;
    const testId = testForm ? testForm.dataset.testId : null;
    const duration = testForm ? (parseInt(testForm.dataset.duration) || 15) : 15; // 15 minutes default
    const maxWarnings = testForm ? (parseInt(testForm.dataset.maxWarnings) || 3) : 3;

    console.log('Test initialization:', {
        totalQuestions: totalQuestions,
        testId: testId,
        duration: duration,
        testForm: testForm,
        testFormDataset: testForm ? testForm.dataset : 'No form found'
    });

    // ================================
    // Navigation buttons
    // ================================
    const prevBtns = document.querySelectorAll('.prev-btn');
    const nextBtns = document.querySelectorAll('.next-btn');
    const submitBtn = document.getElementById('submit-btn-trigger'); // Updated ID
    const questionNumbers = document.querySelectorAll('.question-number');

    console.log('Navigation elements:', {
        prevBtnsCount: prevBtns.length,
        nextBtnsCount: nextBtns.length,
        submitBtn: submitBtn,
        questionNumbers: questionNumbers.length
    });

    // ================================
    // Timer functionality
    // ================================
    let totalSeconds = duration * 60;
    let initialTotalSeconds = totalSeconds;
    let timer = null;
    const timerStatus = document.getElementById('timer-status');
    const timerDisplay = document.getElementById('timer-display');
    const minutesElement = document.getElementById('minutes');
    const secondsElement = document.getElementById('seconds');
    const progressBar = document.getElementById('timer-progress-bar');

    console.log('Timer elements:', {
        timerStatus: timerStatus,
        timerDisplay: timerDisplay,
        minutesElement: minutesElement,
        secondsElement: secondsElement,
        progressBar: progressBar,
        totalSeconds: totalSeconds,
        duration: duration
    });

    function updateTimer() {
        totalSeconds--;

        if (totalSeconds <= 0) {
            clearInterval(timer);
            alert('Time is up! Your test will be submitted automatically.');
            submitTest();
            return;
        }

        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;

        if (minutesElement) {
            minutesElement.textContent = minutes.toString().padStart(2, '0');
        }
        if (secondsElement) {
            secondsElement.textContent = seconds.toString().padStart(2, '0');
        }

        if (progressBar) {
            const progressPercentage = (totalSeconds / initialTotalSeconds) * 100;
            progressBar.style.width = progressPercentage + '%';
        }

        if (totalSeconds < 300 && totalSeconds >= 60) {
            const timerElement = document.getElementById('timer');
            if (timerElement) timerElement.classList.add('timer-warning');
            if (progressBar) {
                progressBar.classList.remove('bg-success');
                progressBar.classList.add('bg-warning');
            }
            if (timerStatus) timerStatus.textContent = "Time is running low!";
        }

        if (totalSeconds < 60) {
            const timerElement = document.getElementById('timer');
            if (timerElement) timerElement.classList.add('timer-danger');
            if (progressBar) {
                progressBar.classList.remove('bg-warning');
                progressBar.classList.add('bg-danger');
            }
            if (timerStatus) timerStatus.textContent = "Hurry up! Almost out of time!";
            if (timerDisplay) timerDisplay.classList.add('pulse');
        } else {
            if (timerDisplay) timerDisplay.classList.remove('pulse');
            if (totalSeconds >= 300 && timerStatus) {
                timerStatus.textContent = "Plenty of time remaining";
            }
        }
    }

    // Start timer
    if (duration > 0) {
        console.log('Starting timer with duration:', duration);
        timer = setInterval(updateTimer, 1000);
        // Initialize timer display immediately
        updateTimer();
    } else {
        console.error('Invalid duration:', duration);
    }

    // ================================
    // Question navigation functions
    // ================================
    function showQuestion(questionNumber) {
        console.log('Showing question:', questionNumber);
        
        // Hide all questions
        document.querySelectorAll('.question-section').forEach(question => {
            question.style.display = 'none';
            question.setAttribute('aria-hidden', 'true');
        });

        // Show current question
        const currentQuestionElement = document.getElementById(`question-${questionNumber}`);
        if (currentQuestionElement) {
            currentQuestionElement.style.display = 'block';
            currentQuestionElement.setAttribute('aria-hidden', 'false');

            // Focus on question text for accessibility
            const questionText = currentQuestionElement.querySelector('.question-text');
            if (questionText) {
                questionText.setAttribute('tabindex', '-1');
                questionText.focus();
            }
        }

        currentQuestion = questionNumber;
        if (currentQuestionInput) {
            currentQuestionInput.value = currentQuestion;
        }

        updateNavigationButtons();
        updateQuestionNumbers();
    }

    function updateNavigationButtons() {
        prevBtns.forEach(btn => {
            btn.disabled = currentQuestion === 1;
        });
        
        nextBtns.forEach(btn => {
            btn.disabled = currentQuestion === totalQuestions;
        });
    }

    function updateQuestionNumbers() {
        questionNumbers.forEach(qNum => qNum.classList.remove('active'));
        const currentQuestionNumber = document.querySelector(`.question-number[data-question="${currentQuestion}"]`);
        if (currentQuestionNumber) {
            currentQuestionNumber.classList.add('active');
            if (currentQuestionNumber.classList.contains('not-visited')) {
                currentQuestionNumber.classList.remove('not-visited');
                currentQuestionNumber.classList.add('not-answered');
            }
        }
    }

    function updateQuestionStatus(questionNumber) {
        const questionElement = document.querySelector(`.question-number[data-question="${questionNumber}"]`);
        if (!questionElement) return;

        // Find the question ID from the form
        const questionSection = document.getElementById(`question-${questionNumber}`);
        if (!questionSection) return;

        const radioInputs = questionSection.querySelectorAll('input[type="radio"]');
        const isAnswered = Array.from(radioInputs).some(input => input.checked);
        const bookmarkCheckbox = questionSection.querySelector('.bookmark-checkbox');
        const isBookmarked = bookmarkCheckbox ? bookmarkCheckbox.checked : false;

        questionElement.classList.remove('not-visited', 'not-answered', 'answered', 'bookmarked');

        if (isAnswered) {
            questionElement.classList.add('answered');
        } else {
            questionElement.classList.add('not-answered');
        }

        if (isBookmarked) {
            questionElement.classList.add('bookmarked');
        }

        updateLegendCounts();
    }

    // ================================
    // Function: Update legend counts
    // ================================
    function updateLegendCounts() {
        const currentCount = document.querySelectorAll('.question-number.active').length;
        const answeredCount = document.querySelectorAll('.question-number.answered:not(.bookmarked)').length;
        const notAnsweredCount = document.querySelectorAll('.question-number.not-answered:not(.bookmarked)').length;
        const notVisitedCount = document.querySelectorAll('.question-number.not-visited').length;
        const bookmarkedCount = document.querySelectorAll('.question-number.bookmarked:not(.answered)').length;
        const bookmarkedAnsweredCount = document.querySelectorAll('.question-number.bookmarked.answered').length;

        console.log('Legend counts:', {
            current: currentCount,
            answered: answeredCount,
            notAnswered: notAnsweredCount,
            notVisited: notVisitedCount,
            bookmarked: bookmarkedCount,
            bookmarkedAnswered: bookmarkedAnsweredCount
        });

        const legendItems = document.querySelectorAll('.legend-item span');
        if (legendItems.length >= 6) {
            legendItems[0].textContent = `Current Question (${currentCount})`;
            legendItems[1].textContent = `Answered (${answeredCount})`;
            legendItems[2].textContent = `Not Answered (${notAnsweredCount})`;
            legendItems[3].textContent = `Not Visited (${notVisitedCount})`;
            legendItems[4].textContent = `Bookmarked (${bookmarkedCount})`;
            legendItems[5].textContent = `Bookmarked & Answered (${bookmarkedAnsweredCount})`;
        }
    }

    // ================================
    // Event listeners
    // ================================
    if (prevBtns.length > 0) {
        console.log('Adding event listeners to prev buttons');
        prevBtns.forEach(btn => {
            btn.addEventListener('click', function (e) {
                console.log('Prev button clicked, current question:', currentQuestion);
                e.preventDefault();
                if (currentQuestion > 1) {
                    updateQuestionStatus(currentQuestion);
                    showQuestion(currentQuestion - 1);
                }
            });
        });
    } else {
        console.error('Prev buttons not found!');
    }

    if (nextBtns.length > 0) {
        console.log('Adding event listeners to next buttons');
        nextBtns.forEach(btn => {
            btn.addEventListener('click', function (e) {
                console.log('Next button clicked. Current:', currentQuestion, 'Total:', totalQuestions);
                e.preventDefault();
                
                if (currentQuestion < totalQuestions) {
                    const nextQ = currentQuestion + 1;
                    const nextEl = document.getElementById(`question-${nextQ}`);
                    
                    if (!nextEl) {
                        console.error(`Target question element #question-${nextQ} not found!`);
                        alert('Error: Next question not found. Please verify your internet connection or refresh the page.');
                        return;
                    }

                    updateQuestionStatus(currentQuestion);
                    showQuestion(nextQ);
                } else {
                    console.log('Already at last question');
                    // Optional: Shake the button or show a tooltip?
                }
            });
        });
    } else {
        console.error('Next buttons not found!');
    }

    questionNumbers.forEach(qNum => {
        qNum.addEventListener('click', function (e) {
            console.log('Question number clicked:', this.getAttribute('data-question'));
            e.preventDefault();
            const questionNumber = parseInt(this.getAttribute('data-question'));
            updateQuestionStatus(currentQuestion);
            showQuestion(questionNumber);
        });

        qNum.setAttribute('tabindex', '0');
        qNum.setAttribute('role', 'button');
        qNum.setAttribute('aria-label', 'Go to question ' + qNum.getAttribute('data-question'));

        qNum.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const questionNumber = parseInt(this.getAttribute('data-question'));
                updateQuestionStatus(currentQuestion);
                showQuestion(questionNumber);
            }
        });
    });

    // Submit button logic is handled by Bootstrap Modal in HTML
    // We don't need a separate event listener here for the trigger button
    /* 
    if (submitBtn) {
        console.log('Adding event listener to submit button');
        submitBtn.addEventListener('click', function (e) {
            // ... logic removed to avoid conflict with Bootstrap Modal ...
        });
    } 
    */

    function submitTest() {
        if (testFinished) {
            return;
        }
        testFinished = true;
        console.log('Submitting test...');
        // Update final question status before submission
        updateQuestionStatus(currentQuestion);
        
        // Update warning count
        if (warningCountInput) {
            warningCountInput.value = warningCount;
        }
        
        if (timer) {
            clearInterval(timer);
        }
        
        // Submit the form
        if (testForm) {
            console.log('Submitting form...');
            testForm.submit();
        } else {
            console.error('Test form not found!');
        }
    }

    // Add event listeners for radio buttons
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const questionSection = this.closest('.question-section');
            if (questionSection) {
                const questionNumber = parseInt(questionSection.id.split('-')[1]);
                updateQuestionStatus(questionNumber);
            }
        });
    });

    // Add event listeners for bookmark checkboxes
    document.querySelectorAll('.bookmark-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const questionSection = this.closest('.question-section');
            if (questionSection) {
                const questionNumber = parseInt(questionSection.id.split('-')[1]);
                updateQuestionStatus(questionNumber);
            }
        });
    });

    // ================================
    // Anti-cheating features
    // ================================
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'hidden') {
            recordWarning('Tab/Application switching detected');
        }
    });

    // Detect focus loss (window blur) - captures Alt+Tab, Win+Shift+S (Snipping Tool), clicking outside
    window.addEventListener('blur', function () {
        recordWarning('Window focus lost. Please stay on the test screen.');
    });

    document.addEventListener('keydown', function (e) {
        // Prevent standard copy/paste/cut
        if ((e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'x')) || 
            (e.metaKey && (e.key === 'c' || e.key === 'v' || e.key === 'x'))) {
            e.preventDefault();
            recordWarning('Copy/Paste/Cut shortcuts are disabled');
        }
        
        // Prevent Alt+Tab (though blur/visibilitychange usually catches this too)
        if (e.altKey && e.key === 'Tab') {
            e.preventDefault();
            recordWarning('Alt+Tab is disabled');
        }

        // Prevent PrintScreen (some browsers catch it on keydown)
        if (e.key === 'PrintScreen') {
            e.preventDefault();
            recordWarning('Screenshot attempt detected (PrintScreen)');
        }

        // Prevent Windows/Command key (often used for screenshots like Win+Shift+S)
        if (e.key === 'Meta' || e.key === 'OS') {
            e.preventDefault();
            recordWarning('System key detected (Windows/Command key)');
        }
    });

    // Backup for PrintScreen (some browsers only fire keyup for it)
    document.addEventListener('keyup', function (e) {
        if (e.key === 'PrintScreen') {
            e.preventDefault();
            recordWarning('Screenshot attempt detected (PrintScreen)');
        }
    });

    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
        recordWarning('Right-click menu is disabled');
    });

    function recordWarning(message) {
        if (testFinished) {
            return;
        }
        warningCount++;
        if (warningCountInput) {
            warningCountInput.value = warningCount;
        }

        // Play warning sound for 5 seconds
        if (warningSound) {
            try {
                // If already playing, reset and replay
                warningSound.pause();
                warningSound.currentTime = 0;
                const playPromise = warningSound.play();
                if (playPromise && typeof playPromise.then === 'function') {
                    playPromise.catch(() => {/* autoplay may be blocked; ignore */});
                }
                if (warningSoundTimeout) clearTimeout(warningSoundTimeout);
                warningSoundTimeout = setTimeout(() => {
                    try {
                        warningSound.pause();
                        warningSound.currentTime = 0;
                    } catch (_) {}
                }, 5000);
            } catch (_) {
                // Ignore audio errors
            }
        }

        // Show warning in container
        if (warningContainer) {
            warningContainer.style.display = 'block';
            const warningElement = document.createElement('div');
            warningElement.className = 'alert alert-danger alert-dismissible fade show';
            warningElement.innerHTML =
                `<strong>Warning ${warningCount}/${maxWarnings}:</strong> ${message} 
                 <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
            warningContainer.appendChild(warningElement);

            // Auto-remove warning after 5 seconds
            setTimeout(() => {
                if (warningElement.parentNode) {
                    warningElement.remove();
                }
            }, 5000);
        }

        if (warningCount >= maxWarnings) {
            if (timer) clearInterval(timer);
            alert(`Maximum warnings (${maxWarnings}) reached. Your test will be terminated.`);
            submitTest();
        }
    }

    window.manualSubmitTest = submitTest;

    // No page-unload handler: user can leave/close without browser warning dialog

    // ================================
    // Initialize on load
    // ================================
    updateNavigationButtons();
    updateLegendCounts();
    
    // Show first question by default
    showQuestion(1);
    
    console.log('Test interface initialized successfully');
});

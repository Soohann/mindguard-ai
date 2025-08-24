// MindGuard Professional Interface - Enhanced JavaScript
class MindGuardApp {
    constructor() {
        this.emojis = {};
        this.isDragging = false;
        this.currentSlider = null;
        this.sliderValues = {
            mood: 3, stress: 3, focus: 3, sleep: 3,
            motivation: 3, anxiety: 3, appetite: 3,
            food_security: 3
        };
        
        // Animation and interaction settings
        this.animationDuration = 250;
        this.debounceTimeout = null;
        
        this.init();
    }

    async init() {
        try {
            // Show loading state
            this.showInitialLoading();
            
            // Load emoji mappings from backend
            await this.loadEmojis();
            
            // Initialize sliders with enhanced interactions
            this.initializeSliders();
            
            // Initialize form handling
            this.initializeForm();
            
            // Set initial state with animations
            await this.updateAllSliders();
            
            // Hide loading and show interface
            this.hideInitialLoading();
            
            console.log('🧠 MindGuard Professional Interface initialized successfully!');
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showError('Failed to initialize the application. Please refresh the page.');
        }
    }

    showInitialLoading() {
        // Add a subtle loading indicator
        document.body.style.cursor = 'wait';
    }

    hideInitialLoading() {
        document.body.style.cursor = 'default';
        // Fade in the main container
        const container = document.querySelector('.block-container');
        if (container) {
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';
            
            requestAnimationFrame(() => {
                container.style.transition = 'all 0.5s ease-out';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            });
        }
    }

    async loadEmojis() {
        try {
            const response = await fetch('/api/emojis');
            if (response.ok) {
                this.emojis = await response.json();
            } else {
                // Enhanced fallback emoji mappings
                this.emojis = {
                    "mood": {1: "😞", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"},
                    "stress": {1: "😌", 2: "😕", 3: "😟", 4: "😣", 5: "😫"},
                    "focus": {1: "😵", 2: "😕", 3: "😐", 4: "🙂", 5: "😎"},
                    "sleep": {1: "😴", 2: "🥱", 3: "😐", 4: "🙂", 5: "😌"},
                    "motivation": {1: "🥀", 2: "😕", 3: "😐", 4: "🙂", 5: "🚀"},
                    "anxiety": {1: "😌", 2: "😯", 3: "😬", 4: "😰", 5: "😱"},
                    "appetite": {1: "🥄", 2: "🍽️", 3: "😐", 4: "🥗", 5: "🍱"},
                    "food_security": {1: "🍞", 2: "🍽️", 3: "🙂", 4: "🛒", 5: "🧺"}
                };
            }
        } catch (error) {
            console.error('Error loading emojis:', error);
        }
    }

    initializeSliders() {
        const customSliders = document.querySelectorAll('.custom-slider');
        
        customSliders.forEach(slider => {
            const sliderName = slider.getAttribute('data-slider');
            
            // Enhanced mouse events with better feedback
            slider.addEventListener('mousedown', (e) => this.startDrag(e, sliderName));
            slider.addEventListener('click', (e) => this.handleClick(e, sliderName));
            slider.addEventListener('mouseenter', () => this.handleSliderHover(sliderName, true));
            slider.addEventListener('mouseleave', () => this.handleSliderHover(sliderName, false));
            
            // Enhanced touch events for mobile
            slider.addEventListener('touchstart', (e) => this.startDrag(e, sliderName), { passive: false });
            
            // Add keyboard support
            slider.setAttribute('tabindex', '0');
            slider.setAttribute('role', 'slider');
            slider.setAttribute('aria-valuemin', '1');
            slider.setAttribute('aria-valuemax', '5');
            slider.setAttribute('aria-valuenow', '3');
            slider.addEventListener('keydown', (e) => this.handleKeyboard(e, sliderName));
        });
        
        // Global event listeners with improved performance
        document.addEventListener('mousemove', (e) => this.handleDrag(e), { passive: true });
        document.addEventListener('mouseup', () => this.stopDrag());
        document.addEventListener('touchmove', (e) => this.handleDrag(e), { passive: false });
        document.addEventListener('touchend', () => this.stopDrag());
    }

    handleSliderHover(sliderName, isHovering) {
        const container = document.querySelector(`[data-slider="${sliderName}"]`).closest('.slider-container');
        if (isHovering) {
            container.style.transform = 'translateY(-2px)';
            container.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1)';
        } else {
            container.style.transform = 'translateY(0)';
            container.style.boxShadow = '';
        }
    }

    handleKeyboard(e, sliderName) {
        const currentValue = this.sliderValues[sliderName];
        let newValue = currentValue;
        
        switch(e.key) {
            case 'ArrowLeft':
            case 'ArrowDown':
                newValue = Math.max(1, currentValue - 1);
                break;
            case 'ArrowRight':
            case 'ArrowUp':
                newValue = Math.min(5, currentValue + 1);
                break;
            case 'Home':
                newValue = 1;
                break;
            case 'End':
                newValue = 5;
                break;
            default:
                return;
        }
        
        e.preventDefault();
        this.updateSlider(sliderName, newValue);
        this.provideFeedback(sliderName, newValue);
    }

    provideFeedback(sliderName, value) {
        // Subtle haptic feedback for mobile devices
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
        
        // Audio feedback (optional)
        if (window.AudioContext) {
            // Could add subtle audio cues here
        }
    }

    initializeForm() {
        const form = document.getElementById('wellness-form');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Add real-time validation
        const textarea = document.getElementById('journal');
        textarea.addEventListener('input', (e) => this.handleJournalInput(e));
    }

    handleJournalInput(e) {
        const textarea = e.target;
        const charCount = textarea.value.length;
        const maxChars = 1000; // Set a reasonable limit
        
        // Add character counter (if not exists)
        let counter = textarea.parentNode.querySelector('.char-counter');
        if (!counter) {
            counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.style.cssText = 'font-size: 0.75rem; color: var(--gray-500); text-align: right; margin-top: 0.5rem;';
            textarea.parentNode.appendChild(counter);
        }
        
        counter.textContent = `${charCount}/${maxChars} characters`;
        
        // Change color if approaching limit
        if (charCount > maxChars * 0.9) {
            counter.style.color = 'var(--warning-600)';
        } else if (charCount > maxChars) {
            counter.style.color = 'var(--error-600)';
            textarea.value = textarea.value.substring(0, maxChars);
        } else {
            counter.style.color = 'var(--gray-500)';
        }
    }

    startDrag(e, sliderName) {
        e.preventDefault();
        this.isDragging = true;
        this.currentSlider = sliderName;
        
        // Add visual feedback
        const slider = document.querySelector(`[data-slider="${sliderName}"]`);
        slider.style.cursor = 'grabbing';
        
        this.handleClick(e, sliderName);
    }

    handleClick(e, sliderName) {
        const slider = document.querySelector(`[data-slider="${sliderName}"]`);
        const rect = slider.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const percentage = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        
        // Calculate discrete value (snaps to 1, 2, 3, 4, 5)
        const value = Math.round(percentage * 4) + 1;
        
        // Update slider with smooth animation to discrete position
        this.updateSlider(sliderName, value);
        this.provideFeedback(sliderName, value);
    }

    handleDrag(e) {
        if (!this.isDragging || !this.currentSlider) return;
        
        e.preventDefault();
        this.handleClick(e, this.currentSlider);
    }

    stopDrag() {
        if (this.currentSlider) {
            const slider = document.querySelector(`[data-slider="${this.currentSlider}"]`);
            slider.style.cursor = 'grab';
        }
        
        this.isDragging = false;
        this.currentSlider = null;
    }

    updateSlider(sliderName, value) {
        // Update internal state
        this.sliderValues[sliderName] = value;
        
        // Update hidden input
        const hiddenInput = document.getElementById(sliderName);
        if (hiddenInput) {
            hiddenInput.value = value;
        }
        
        // Update visual elements with animation
        this.updateSliderVisuals(sliderName, value);
        
        // Update emoji, label, and value display
        this.updateSliderLabel(sliderName, value);
        this.updateValueDisplay(sliderName, value);
        
        // Update accessibility attributes
        const slider = document.querySelector(`[data-slider="${sliderName}"]`);
        slider.setAttribute('aria-valuenow', value);
    }

    updateSliderVisuals(sliderName, value) {
        const slider = document.querySelector(`[data-slider="${sliderName}"]`);
        const fill = slider.querySelector('.slider-fill');
        const thumb = slider.querySelector('.slider-thumb');

        // Use the ORIGINAL logic from the previous version
        const negativeSliders = ['stress', 'anxiety'];
        const isNegative = negativeSliders.includes(sliderName);

        // ✅ Calculate position for discrete values (1, 2, 3, 4, 5)
        const percentage = ((value - 1) / 4) * 100;
        
        // ✅ Always use smooth transitions (this makes it smooth)
        thumb.style.transition = 'left 0.3s ease-out, border-color 0.2s ease-out';
        fill.style.transition = 'width 0.3s ease-out, background-color 0.2s ease-out';
        
        thumb.style.left = `${percentage}%`;
        fill.style.width = `${percentage}%`;

        // ✅ ORIGINAL color logic - reverse for positive sliders (5 = best = green)
        const colorValue = isNegative ? value : (6 - value);

        // ✅ Update colors using the original class names
        fill.className = `slider-fill fill-color-${colorValue}`;
        thumb.className = `slider-thumb thumb-color-${colorValue}`;

        // ✅ Update thumb value display
        let numberSpan = thumb.querySelector('.thumb-value');
        if (!numberSpan) {
            numberSpan = document.createElement('div');
            numberSpan.className = 'thumb-value';
            thumb.appendChild(numberSpan);
        }
        numberSpan.textContent = value;

        // Add subtle animation to the container
        const container = slider.closest('.slider-container');
        container.style.transform = 'scale(1.02)';
        setTimeout(() => {
            container.style.transform = 'scale(1)';
        }, 150);
    }

    updateSliderLabel(sliderName, value) {
        const emojiElement = document.getElementById(`${sliderName}-emoji`);
        
        if (this.emojis[sliderName] && this.emojis[sliderName][value]) {
            const emoji = this.emojis[sliderName][value];
            emojiElement.textContent = emoji;
            
            // Add emoji animation
            emojiElement.style.transform = 'scale(1.2)';
            setTimeout(() => {
                emojiElement.style.transform = 'scale(1)';
            }, 200);
        }
    }

    updateValueDisplay(sliderName, value) {
        const valueDisplay = document.getElementById(`${sliderName}-value`);
        if (valueDisplay) {
            valueDisplay.textContent = value;
            
            // Add pulse animation
            valueDisplay.style.transform = 'scale(1.1)';
            setTimeout(() => {
                valueDisplay.style.transform = 'scale(1)';
            }, 150);
        }
    }

    getDisplayName(sliderName) {
        const displayNames = {
            'mood': 'Mood',
            'stress': 'Stress',
            'focus': 'Focus',
            'sleep': 'Sleep',
            'motivation': 'Motivation',
            'anxiety': 'Anxiety',
            'appetite': 'Appetite',
            'food_security': 'Food Security'
        };
        return displayNames[sliderName] || sliderName;
    }

    async updateAllSliders() {
        const promises = Object.keys(this.sliderValues).map((sliderName, index) => {
            return new Promise(resolve => {
                setTimeout(() => {
                    this.updateSlider(sliderName, this.sliderValues[sliderName]);
                    resolve();
                }, index * 50); // Staggered animation
            });
        });
        
        await Promise.all(promises);
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const submitBtn = document.getElementById('submit-btn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        try {
            // Show enhanced loading state
            this.showLoading(submitBtn, btnText, btnLoading);
            
            // Prepare form data
            const formData = this.getFormData();
            
            // Enhanced validation
            const validationResult = this.validateFormData(formData);
            if (!validationResult.isValid) {
                throw new Error(validationResult.message);
            }
            
            // Submit to backend with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'An error occurred while processing your request.');
            }
            
            // Display results with enhanced animations
            await this.displayResults(result);
            
        } catch (error) {
            if (error.name === 'AbortError') {
                this.showError('Request timed out. Please check your connection and try again.');
            } else {
                this.showError(error.message);
            }
        } finally {
            // Hide loading state
            this.hideLoading(submitBtn, btnText, btnLoading);
        }
    }

    getFormData() {
        const journal = document.getElementById('journal').value;
        
        return {
            ...this.sliderValues,
            journal: journal.trim()
        };
    }

    validateFormData(formData) {
        const sliderFields = ['mood', 'stress', 'focus', 'sleep', 'motivation', 'anxiety', 'appetite', 'food_security'];
        
        // Check if all sliders are at default value
        if (sliderFields.every(field => formData[field] === 3)) {
            return {
                isValid: false,
                message: 'Please adjust at least one slider to reflect your current state. The sliders help us provide personalized recommendations.'
            };
        }
        
        // Check for valid range
        for (const field of sliderFields) {
            if (formData[field] < 1 || formData[field] > 5) {
                return {
                    isValid: false,
                    message: `Invalid value for ${field}. Please ensure all values are between 1 and 5.`
                };
            }
        }
        
        return { isValid: true };
    }

    showLoading(submitBtn, btnText, btnLoading) {
        submitBtn.disabled = true;
        submitBtn.style.cursor = 'not-allowed';
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-flex';
        
        // Add loading class for additional styling
        submitBtn.classList.add('loading');
    }

    hideLoading(submitBtn, btnText, btnLoading) {
        submitBtn.disabled = false;
        submitBtn.style.cursor = 'pointer';
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        
        // Remove loading class
        submitBtn.classList.remove('loading');
    }

    showError(message) {
        // Create a professional error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'stAlert stAlert--error';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        errorDiv.innerHTML = `
            <div class="stAlert-content">
                <strong>⚠️ Error:</strong> ${message}
                <button onclick="this.parentElement.parentElement.remove()" style="
                    float: right;
                    background: none;
                    border: none;
                    font-size: 1.2rem;
                    cursor: pointer;
                    color: var(--error-600);
                    margin-left: 10px;
                ">&times;</button>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => errorDiv.remove(), 300);
            }
        }, 5000);
    }

    async displayResults(result) {
        const resultsSection = document.getElementById('results');
        const burnoutResult = document.getElementById('burnout-result');
        const feedback = document.getElementById('feedback');
        const resources = document.getElementById('resources');
        const emotionAnalysis = document.getElementById('emotion-analysis');
        
        // Show results section with animation
        resultsSection.style.display = 'block';
        resultsSection.style.opacity = '0';
        resultsSection.style.transform = 'translateY(30px)';
        
        // Animate results appearance
        await new Promise(resolve => {
            requestAnimationFrame(() => {
                resultsSection.style.transition = 'all 0.5s ease-out';
                resultsSection.style.opacity = '1';
                resultsSection.style.transform = 'translateY(0)';
                setTimeout(resolve, 500);
            });
        });
        
        // Display burnout level with enhanced styling
        this.displayBurnoutResult(burnoutResult, result);
        
        // Display feedback
        const feedbackContent = feedback.querySelector('.stAlert-content') || feedback;
        feedbackContent.innerHTML = result.feedback;
        
        // Display resources with enhanced layout
        this.displayResources(resources, result.resources);
        
        // Display emotion analysis if available
        if (result.emotion_analysis) {
            this.displayEmotionAnalysis(emotionAnalysis, result.emotion_analysis);
        } else {
            emotionAnalysis.style.display = 'none';
        }
        
        // Smooth scroll to results
        resultsSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    displayBurnoutResult(container, result) {
        const level = result.burnout_level.toLowerCase();
        const score = result.wellness_score;
        
        const levelEmojis = {
            'low': '🟢',
            'moderate': '🟡', 
            'high': '🔴'
        };
        
        const levelMessages = {
            'low': 'Great job maintaining your wellness!',
            'moderate': 'Some areas need attention.',
            'high': 'Consider reaching out for support.'
        };
        
        container.innerHTML = `
            <div class="burnout-level ${level}">
                ${levelEmojis[level]} Burnout Risk: <strong>${result.burnout_level}</strong>
            </div>
            <div class="wellness-score">
                Wellness Score: <strong>${score}/5.0</strong>
            </div>
            <p style="margin-top: 1rem; color: var(--gray-600); font-size: 1rem;">
                ${levelMessages[level]}
            </p>
        `;
    }

    displayResources(container, resourcesData) {
        if (!resourcesData || !Array.isArray(resourcesData.items)) {
            container.innerHTML = '<p>No specific resources recommended at this time.</p>';
            return;
        }

        let html = '';
        resourcesData.items.forEach(item => {
            const name = item.name || '';
            const desc = item.description || '';
            const url = item.url;

            html += `
                <div class="resource-card">
                    ${url ? 
                        `<h5><a href="${url}" target="_blank" rel="noopener noreferrer">${name}</a></h5>` :
                        `<h5>${name}</h5>`
                    }
                    ${desc ? `<p>${desc}</p>` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
    }

    displayEmotionAnalysis(container, emotionData) {
        const confidencePercent = Math.round(emotionData.confidence * 100);
        
        container.innerHTML = `
            <div class="emotion-result">
                <p><strong>Detected Emotion:</strong> ${emotionData.emotion}</p>
                <p><strong>Confidence:</strong> ${confidencePercent}%</p>
                <div style="
                    width: 100%;
                    height: 8px;
                    background: var(--gray-200);
                    border-radius: 4px;
                    overflow: hidden;
                    margin-top: 0.5rem;
                ">
                    <div style="
                        width: ${confidencePercent}%;
                        height: 100%;
                        background: var(--primary-600);
                        transition: width 1s ease-out;
                    "></div>
                </div>
            </div>
        `;
        container.style.display = 'block';
    }

    // Utility methods
    resetForm() {
        // Reset slider values to default with animation
        Object.keys(this.sliderValues).forEach((key, index) => {
            setTimeout(() => {
                this.sliderValues[key] = 3;
                this.updateSlider(key, 3);
            }, index * 50);
        });
        
        // Clear journal
        document.getElementById('journal').value = '';
        
        // Hide results with animation
        const resultsSection = document.getElementById('results');
        resultsSection.style.transition = 'all 0.3s ease-in';
        resultsSection.style.opacity = '0';
        resultsSection.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            resultsSection.style.display = 'none';
        }, 300);
    }

    getWellnessSummary() {
        const values = { ...this.sliderValues };
        const total = Object.values(values).reduce((a, b) => a + b, 0);
        const average = total / 8;
        
        return {
            values,
            total,
            average: Math.round(average * 100) / 100,
            timestamp: new Date().toISOString()
        };
    }

    // Export functionality for analytics
    exportData() {
        const summary = this.getWellnessSummary();
        const journal = document.getElementById('journal').value;
        
        const exportData = {
            ...summary,
            journal: journal.trim(),
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
        
        // Create downloadable JSON
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mindguard-data-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mindGuardApp = new MindGuardApp();
    
    // Console branding
    console.log(`
🧠 MindGuard Professional Interface
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ AI-Powered Student Wellness Monitoring
🎯 Built for University of Idaho Students  
🔒 Privacy-First Design
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `);
});

// Enhanced keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Reset form with Ctrl+R (prevent default page refresh)
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (window.mindGuardApp) {
            window.mindGuardApp.resetForm();
            console.log('✨ Form reset via keyboard shortcut');
        }
    }
    
    // Quick submit with Ctrl+Enter
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.click();
            console.log('🚀 Quick submit via keyboard shortcut');
        }
    }
    
    // Export data with Ctrl+E
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        if (window.mindGuardApp) {
            window.mindGuardApp.exportData();
            console.log('📊 Data exported via keyboard shortcut');
        }
    }
});

// Performance monitoring and analytics
if (window.performance && window.performance.mark) {
    window.performance.mark('mindguard-start');
    
    window.addEventListener('load', () => {
        window.performance.mark('mindguard-loaded');
        window.performance.measure('mindguard-load-time', 'mindguard-start', 'mindguard-loaded');
        
        const measure = window.performance.getEntriesByName('mindguard-load-time')[0];
        console.log(`⚡ MindGuard loaded in ${Math.round(measure.duration)}ms`);
        
        // Track key metrics
        if (measure.duration > 3000) {
            console.warn('⚠️ Slow load time detected. Consider optimizing.');
        }
    });
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .stButton.loading {
        background: linear-gradient(135deg, var(--gray-400), var(--gray-500)) !important;
        cursor: not-allowed !important;
    }
    
    .stButton.loading::before {
        display: none;
    }
`;
document.head.appendChild(style);

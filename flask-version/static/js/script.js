// MindGuard Flask App - JavaScript (Exact Streamlit Match)
class MindGuardApp {
    constructor() {
        this.emojis = {};
        this.isDragging = false;
        this.currentSlider = null;
        this.sliderValues = {
            mood: 3, stress: 3, focus: 3, sleep: 3,
            energy: 3, motivation: 3, anxiety: 3, appetite: 3
        };
        
        this.init();
    }

    async init() {
        try {
            // Load emoji mappings from backend
            await this.loadEmojis();
            
            // Initialize sliders
            this.initializeSliders();
            
            // Initialize form handling
            this.initializeForm();
            
            // Set initial state
            this.updateAllSliders();
            
            console.log('MindGuard app initialized successfully!');
        } catch (error) {
            console.error('Error initializing app:', error);
        }
    }

    async loadEmojis() {
        try {
            const response = await fetch('/api/emojis');
            if (response.ok) {
                this.emojis = await response.json();
            } else {
                // Fallback emoji mappings - exact Streamlit emojis
                this.emojis = {
                    "mood": {1: "😞", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"},
                    "stress": {1: "😌", 2: "😕", 3: "😟", 4: "😣", 5: "😫"},
                    "focus": {1: "😵", 2: "😕", 3: "😐", 4: "🙂", 5: "😎"},
                    "sleep": {1: "😴", 2: "🥱", 3: "😐", 4: "🙂", 5: "😌"},
                    "energy": {1: "🥱", 2: "😪", 3: "😐", 4: "😊", 5: "🤩"},
                    "motivation": {1: "🥀", 2: "😕", 3: "😐", 4: "🙂", 5: "🚀"},
                    "anxiety": {1: "😌", 2: "😯", 3: "😬", 4: "😰", 5: "😱"},
                    "appetite": {1: "🥄", 2: "🍽️", 3: "😐", 4: "🥗", 5: "🍱"}
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
            
            // Mouse events
            slider.addEventListener('mousedown', (e) => this.startDrag(e, sliderName));
            slider.addEventListener('click', (e) => this.handleClick(e, sliderName));
            
            // Touch events for mobile
            slider.addEventListener('touchstart', (e) => this.startDrag(e, sliderName), { passive: false });
        });
        
        // Global event listeners
        document.addEventListener('mousemove', (e) => this.handleDrag(e));
        document.addEventListener('mouseup', () => this.stopDrag());
        document.addEventListener('touchmove', (e) => this.handleDrag(e), { passive: false });
        document.addEventListener('touchend', () => this.stopDrag());
    }

    initializeForm() {
        const form = document.getElementById('wellness-form');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    startDrag(e, sliderName) {
        e.preventDefault();
        this.isDragging = true;
        this.currentSlider = sliderName;
        this.handleClick(e, sliderName);
    }

    handleClick(e, sliderName) {
        const slider = document.querySelector(`[data-slider="${sliderName}"]`);
        const rect = slider.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const percentage = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        const value = Math.round(percentage * 4) + 1;
        
        this.updateSlider(sliderName, value);
    }

    handleDrag(e) {
        if (!this.isDragging || !this.currentSlider) return;
        
        e.preventDefault();
        this.handleClick(e, this.currentSlider);
    }

    stopDrag() {
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
        
        // Update visual elements
        this.updateSliderVisuals(sliderName, value);
        
        // Update emoji and label - Streamlit style
        this.updateSliderLabel(sliderName, value);
    }

    updateSliderVisuals(sliderName, value) {
    const slider = document.querySelector(`[data-slider="${sliderName}"]`);
    const fill = slider.querySelector('.slider-fill');
    const thumb = slider.querySelector('.slider-thumb');

    const negativeSliders = ['stress', 'anxiety'];
    const isNegative = negativeSliders.includes(sliderName);

    // ✅ Reverse color for positive sliders (5 = best)
    const colorValue = isNegative ? value : (6 - value);

    // ✅ Update thumb position
    const percentage = ((value - 1) / 4) * 100;
    thumb.style.left = `${percentage}%`;
    fill.style.width = `${percentage}%`;

    // ✅ Color update
    fill.className = `slider-fill fill-color-${colorValue}`;
    thumb.className = `slider-thumb thumb-color-${colorValue}`;

    // ✅ Create or update the number display
    let numberSpan = thumb.querySelector('.thumb-value');
    if (!numberSpan) {
        numberSpan = document.createElement('span');
        numberSpan.className = 'thumb-value';
        thumb.appendChild(numberSpan);
    }
    numberSpan.textContent = value;
}





    updateSliderLabel(sliderName, value) {
        const label = document.getElementById(`${sliderName}-label`);
    
        // Add label styling
        label.classList.add('slider-label');
    
        // Update emoji and text
        if (this.emojis[sliderName] && this.emojis[sliderName][value]) {
            const emoji = this.emojis[sliderName][value];
            const displayName = this.getDisplayName(sliderName);
            label.textContent = `${emoji} ${displayName}`;
        }
    }


    getDisplayName(sliderName) {
        const displayNames = {
            'mood': 'Mood',
            'stress': 'Stress', 
            'focus': 'Focus',
            'sleep': 'Sleep Quality',
            'energy': 'Energy Level',
            'motivation': 'Motivation',
            'anxiety': 'Anxiety',
            'appetite': 'Appetite'
        };
        return displayNames[sliderName] || sliderName;
    }

    updateAllSliders() {
        Object.keys(this.sliderValues).forEach(sliderName => {
            this.updateSlider(sliderName, this.sliderValues[sliderName]);
        });
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const submitBtn = document.getElementById('submit-btn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        try {
            // Show loading state
            this.showLoading(submitBtn, btnText, btnLoading);
            
            // Prepare form data
            const formData = this.getFormData();
            
            // Validate form data
            if (this.isAllDefault(formData)) {
                throw new Error('It looks like you haven\'t updated any inputs. Please adjust them to reflect your current state.');
            }
            
            // Submit to backend
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'An error occurred while processing your request.');
            }
            
            // Display results - Streamlit style
            this.displayResults(result);
            
        } catch (error) {
            this.showError(error.message);
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

    isAllDefault(formData) {
        const sliderFields = ['mood', 'stress', 'focus', 'sleep', 'energy', 'motivation', 'anxiety', 'appetite'];
        return sliderFields.every(field => formData[field] === 3);
    }

    showLoading(submitBtn, btnText, btnLoading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    }

    hideLoading(submitBtn, btnText, btnLoading) {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }

    showError(message) {
        // Show Streamlit-style warning (simple alert)
        alert(message);
    }

    displayResults(result) {
        const resultsSection = document.getElementById('results');
        const burnoutResult = document.getElementById('burnout-result');
        const feedback = document.getElementById('feedback');
        const resources = document.getElementById('resources');
        const emotionAnalysis = document.getElementById('emotion-analysis');
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Display burnout level - Exact Streamlit style
        burnoutResult.innerHTML = `<h3>🔥 Burnout Risk Level: <strong>${result.burnout_level}</strong></h3>`;
        
        // Display feedback in info alert
        const feedbackContent = feedback.querySelector('.stAlert-content') || feedback;
        feedbackContent.innerHTML = result.feedback;
        
        // Display resources - Streamlit style
        this.displayResources(resources, result.resources);
        
        // Display emotion analysis if available
        if (result.emotion_analysis) {
            this.displayEmotionAnalysis(emotionAnalysis, result.emotion_analysis);
        } else {
            emotionAnalysis.style.display = 'none';
        }
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    displayResources(container, resourcesData) {
        let html = '';
        
        if (resourcesData.items && resourcesData.items.length > 0) {
            if (resourcesData.items.length >= 3 && resourcesData.items[0].url) {
                // High burnout - show full resources with links
                resourcesData.items.forEach(item => {
                    html += `<p><strong><a href="${item.url}" target="_blank" rel="noopener noreferrer">${item.name}</a></strong><br>${item.description}</p>`;
                });
            } else {
                // Moderate/Low burnout - simple list
                resourcesData.items.forEach(item => {
                    html += `<p>- ${item.name}</p>`;
                });
            }
        }
        
        container.innerHTML = html;
    }

    displayEmotionAnalysis(container, emotionData) {
        const confidencePercent = Math.round(emotionData.confidence * 100);
        
        container.innerHTML = `
            <div class="emotion-result">
                <p><strong>Detected Emotion:</strong> ${emotionData.emotion} (confidence: ${confidencePercent}%)</p>
            </div>
        `;
        container.style.display = 'block';
    }

    // Utility methods
    resetForm() {
        // Reset slider values to default
        Object.keys(this.sliderValues).forEach(key => {
            this.sliderValues[key] = 3;
        });
        
        // Update all sliders visually
        this.updateAllSliders();
        
        // Clear journal
        document.getElementById('journal').value = '';
        
        // Hide results
        document.getElementById('results').style.display = 'none';
    }

    getWellnessSummary() {
        const summary = {
            values: { ...this.sliderValues },
            total: Object.values(this.sliderValues).reduce((a, b) => a + b, 0),
            average: Object.values(this.sliderValues).reduce((a, b) => a + b, 0) / 8
        };
        
        return summary;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mindGuardApp = new MindGuardApp();
    
    // Console info for developers
    console.log('🧠 MindGuard - AI-Powered Student Wellness Monitor');
    console.log('Built for University of Idaho students');
    console.log('Exact Streamlit interface with working colored sliders!');
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Reset form with Ctrl+R (prevent default page refresh)
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (window.mindGuardApp) {
            window.mindGuardApp.resetForm();
            console.log('Form reset via keyboard shortcut');
        }
    }
    
    // Quick submit with Ctrl+Enter
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.click();
        }
    }
});

// Performance monitoring
if (window.performance && window.performance.mark) {
    window.performance.mark('mindguard-app-start');
    
    window.addEventListener('load', () => {
        window.performance.mark('mindguard-app-loaded');
        window.performance.measure('mindguard-load-time', 'mindguard-app-start', 'mindguard-app-loaded');
        
        const measure = window.performance.getEntriesByName('mindguard-load-time')[0];
        console.log(`MindGuard loaded in ${Math.round(measure.duration)}ms`);
    });
}
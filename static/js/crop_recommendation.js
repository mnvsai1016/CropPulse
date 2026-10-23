// Crop Recommendation Page JavaScript
// Handles form submission, API calls, and result display

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cropForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    const placeholderContainer = document.getElementById('placeholderContainer');
    const predictYieldBtn = document.getElementById('predictYieldBtn');
    const getSoilHealthBtn = document.getElementById('getSoilHealthBtn');
    const askChatbotBtn = document.getElementById('askChatbotBtn');

    let currentCropName = null;
    let currentFormData = null;

    // Crop name to emoji/icon mapping
    const cropIcons = {
        'rice': '🌾',
        'wheat': '🌾',
        'maize': '🌽',
        'cotton': '🌿',
        'sugarcane': '🎋',
        'potato': '🥔',
        'onion': '🧅',
        'tomato': '🍅',
        'groundnut': '🥜',
        'soybean': '🫘',
        'sunflower': '🌻',
        'mustard': '🌿',
        'jute': '🌾',
        'bajra': '🌾',
        'jowar': '🌾',
        'mungbean': '🫘',
        'lentil': '🫘',
        'chickpea': '🫘',
        'pigeonpea': '🫘',
        'blackgram': '🫘',
        'mothbeans': '🫘',
        'kidneybeans': '🫘',
        'mango': '🥭',
        'banana': '🍌',
        'grapes': '🍇',
        'watermelon': '🍉',
        'muskmelon': '🍈',
        'apple': '🍎',
        'orange': '🍊',
        'papaya': '🥭',
        'coconut': '🥥',
        'coffee': '☕',
        'tea': '🍵'
    };

    // Helper to safely parse input values
    function getNumericValue(id, fallback = 0) {
        const el = document.getElementById(id);
        if (!el) return fallback;
        const val = parseFloat(el.value);
        return isNaN(val) ? fallback : val;
    }

    // Real-time pH validation
    const phInput = document.getElementById('ph');
    if (phInput) {
        phInput.addEventListener('input', function() {
            const phValue = parseFloat(this.value);
            if (!isNaN(phValue) && (phValue > 14 || phValue < 0)) {
                this.classList.add('error');
                this.setCustomValidity('pH must be between 0 and 14');
            } else {
                this.classList.remove('error');
                this.setCustomValidity('');
            }
        });
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validate form
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            // Get form data safely
            const formData = {
                n: getNumericValue('n'),
                p: getNumericValue('p'),
                k: getNumericValue('k'),
                temperature: getNumericValue('temperature'),
                humidity: getNumericValue('humidity'),
                ph: getNumericValue('ph', 7),
                rainfall: getNumericValue('rainfall')
            };

            // Store form data for soil health button
            currentFormData = formData;

            // Show loading state
            if (analyzeBtn) {
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
            }
            
            // Hide placeholder, show results container
            if (placeholderContainer) placeholderContainer.style.display = 'none';
            if (resultsContainer) {
                resultsContainer.classList.remove('hidden');
                resultsContainer.style.display = 'block';
            }

            // Show loading in results
            showLoadingState();

            try {
                // Make API call
                const response = await fetch('/api/predict-crop', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data && data.success) {
                    displayResults(data.result);
                } else {
                    showError(data ? (data.error || 'An error occurred during prediction') : 'Prediction failed');
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Failed to connect to the server. Please try again.');
            } finally {
                // Reset button
                if (analyzeBtn) {
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze & Recommend';
                }
            }
        });
    }

    function showLoadingState() {
        const cropNameEl = document.getElementById('cropName');
        if (cropNameEl) cropNameEl.textContent = 'Analyzing...';
        const badgeEl = document.getElementById('topRecommendationBadge');
        if (badgeEl) badgeEl.style.display = 'none';
        const adviceSec = document.getElementById('cropAdviceSection');
        if (adviceSec) adviceSec.style.display = 'none';
        const altSec = document.getElementById('alternativesSection');
        if (altSec) altSec.style.display = 'none';
        if (predictYieldBtn) predictYieldBtn.disabled = true;
        if (getSoilHealthBtn) getSoilHealthBtn.disabled = true;
        if (askChatbotBtn) askChatbotBtn.disabled = true;
    }

    function displayResults(result) {
        if (!result) return;
        const cropName = result.crop ? String(result.crop) : 'Unknown';
        const confidence = typeof result.confidence === 'number' ? result.confidence : parseFloat(result.confidence) || 0;
        const alternatives = Array.isArray(result.alternatives) ? result.alternatives : [];
        const advice = result.advice ? String(result.advice) : '';

        currentCropName = cropName;

        // Top Recommendation Badge & Confidence
        const badgeEl = document.getElementById('topRecommendationBadge');
        const confValEl = document.getElementById('confidenceValue');
        if (badgeEl && confValEl) {
            confValEl.textContent = confidence.toFixed(1);
            badgeEl.style.display = 'inline-block';
        }

        // Update crop name
        const cropNameEl = document.getElementById('cropName');
        if (cropNameEl) {
            cropNameEl.textContent = cropName.charAt(0).toUpperCase() + cropName.slice(1);
        }

        // Update crop image/icon
        const cropImage = document.getElementById('cropImage');
        if (cropImage) {
            const cropLower = cropName.toLowerCase();
            const icon = cropIcons[cropLower] || '🌱';
            cropImage.innerHTML = `<span style="font-size: 4rem;">${icon}</span>`;
        }

        // Update agronomic advice
        const adviceSec = document.getElementById('cropAdviceSection');
        const adviceText = document.getElementById('cropAdviceText');
        if (adviceSec && adviceText) {
            if (advice && advice.trim()) {
                adviceText.textContent = advice;
                adviceSec.style.display = 'block';
            } else {
                adviceSec.style.display = 'none';
            }
        }

        // Update secondary alternatives
        const altSec = document.getElementById('alternativesSection');
        const altList = document.getElementById('alternativesList');
        if (altSec && altList) {
            if (alternatives && alternatives.length > 0) {
                altList.innerHTML = '';
                alternatives.forEach(alt => {
                    const altCropName = alt.crop ? String(alt.crop) : '';
                    const altConf = typeof alt.confidence === 'number' ? alt.confidence.toFixed(1) : alt.confidence;
                    const altLower = altCropName.toLowerCase();
                    const altIcon = cropIcons[altLower] || '🌱';
                    const capName = altCropName.charAt(0).toUpperCase() + altCropName.slice(1);

                    const card = document.createElement('div');
                    card.className = 'alternative-card';
                    card.innerHTML = `
                        <div class="alternative-info">
                            <span class="alternative-icon">${altIcon}</span>
                            <div>
                                <span class="alternative-name">${capName}</span>
                                <span class="alternative-conf">${altConf}% match</span>
                            </div>
                        </div>
                        <div class="alternative-actions">
                            <a href="/yield-prediction?crop=${encodeURIComponent(altCropName)}" class="btn-alt-action" title="Predict yield for ${capName}">
                                <i class="fas fa-chart-line"></i> Yield
                            </a>
                            <a href="/soil-health?crop=${encodeURIComponent(altCropName)}" class="btn-alt-action" title="Soil health for ${capName}">
                                <i class="fas fa-microscope"></i> Soil
                            </a>
                        </div>
                    `;
                    altList.appendChild(card);
                });
                altSec.style.display = 'block';
            } else {
                altSec.style.display = 'none';
            }
        }

        // Inject rich context for CropPulse Assistant
        try {
            window.chatContext = {
                feature: "crop_recommendation",
                crop: cropName,
                confidence: confidence,
                alternatives: alternatives.map(a => a.crop),
                advice: advice
            };
        } catch (e) {
            // Ignore context errors
        }

        // Animate result appearance
        if (resultsContainer) {
            resultsContainer.classList.add('fade-in');
        }

        // Enable buttons
        if (predictYieldBtn) predictYieldBtn.disabled = false;
        if (getSoilHealthBtn) getSoilHealthBtn.disabled = false;
        if (askChatbotBtn) askChatbotBtn.disabled = false;
    }

    function showError(message) {
        const cropNameEl = document.getElementById('cropName');
        if (cropNameEl) cropNameEl.textContent = 'Error: ' + (message || 'Unknown error');
        const cropImage = document.getElementById('cropImage');
        if (cropImage) cropImage.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i>';
        const badgeEl = document.getElementById('topRecommendationBadge');
        if (badgeEl) badgeEl.style.display = 'none';
        const adviceSec = document.getElementById('cropAdviceSection');
        if (adviceSec) adviceSec.style.display = 'none';
        const altSec = document.getElementById('alternativesSection');
        if (altSec) altSec.style.display = 'none';
        if (predictYieldBtn) predictYieldBtn.disabled = true;
        if (getSoilHealthBtn) getSoilHealthBtn.disabled = true;
        if (askChatbotBtn) askChatbotBtn.disabled = true;
    }

    // Predict Yield button -> redirect to yield prediction page with preselected crop
    if (predictYieldBtn) {
        predictYieldBtn.addEventListener('click', function() {
            if (!currentCropName) return;
            const cropParam = encodeURIComponent(currentCropName);
            window.location.href = `/yield-prediction?crop=${cropParam}`;
        });
    }

    // Get Soil Health button -> redirect to soil health page with form values
    if (getSoilHealthBtn) {
        getSoilHealthBtn.addEventListener('click', function() {
            if (!currentFormData) return;
            
            // Create URL with form parameters including recommended crop
            const params = new URLSearchParams({
                crop: currentCropName || '',
                nitrogen: currentFormData.n,
                phosphorous: currentFormData.p,
                potassium: currentFormData.k,
                temperature: currentFormData.temperature,
                humidity: currentFormData.humidity
            });
            
            window.location.href = `/soil-health?${params.toString()}`;
        });
    }
});



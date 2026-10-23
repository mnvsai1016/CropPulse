document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('soilHealthForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const originalBtnText = analyzeBtn ? analyzeBtn.innerHTML : '<i class="fas fa-microscope"></i> Analyze & Recommend';

    // Helper to safely populate form fields from URL params
    const setFieldValue = (id, val) => {
        if (val === null || val === undefined) return;
        const el = document.getElementById(id);
        if (el) el.value = val;
    };

    // Check for URL parameters and populate form
    const urlParams = new URLSearchParams(window.location.search);
    setFieldValue('nitrogen', urlParams.get('nitrogen'));
    const pVal = urlParams.get('phosphorous') || urlParams.get('phosphorus');
    setFieldValue('phosphorous', pVal);
    setFieldValue('potassium', urlParams.get('potassium'));
    setFieldValue('temperature', urlParams.get('temperature'));
    setFieldValue('humidity', urlParams.get('humidity'));

    // Check for crop URL parameter and auto-select crop
    const cropParam = urlParams.get('crop') || urlParams.get('cropType');
    if (cropParam) {
        selectFertilizerCrop(cropParam);
    }

    function selectFertilizerCrop(cropName) {
        const cropSelect = document.getElementById('cropType');
        if (!cropSelect || !cropName) return;

        const cropLower = cropName.toLowerCase().trim();
        const cropToFertilizerMap = {
            'rice': 'Paddy',
            'paddy': 'Paddy',
            'wheat': 'Wheat',
            'barley': 'Barley',
            'maize': 'Maize',
            'cotton': 'Cotton',
            'tobacco': 'Tobacco',
            'sugarcane': 'Sugarcane',
            'groundnut': 'Ground Nuts',
            'ground nuts': 'Ground Nuts',
            'oil seeds': 'Oil seeds',
            'oilseeds': 'Oil seeds',
            'pulses': 'Pulses',
            'chickpea': 'Pulses',
            'kidneybeans': 'Pulses',
            'pigeonpeas': 'Pulses',
            'mothbeans': 'Pulses',
            'mungbean': 'Pulses',
            'blackgram': 'Pulses',
            'lentil': 'Pulses',
            'millets': 'Millets',
            'jute': 'Cotton',
            'watermelon': 'Pulses',
            'muskmelon': 'Pulses',
            'apple': 'Pulses',
            'banana': 'Pulses',
            'grapes': 'Pulses',
            'mango': 'Pulses',
            'orange': 'Pulses',
            'papaya': 'Pulses',
            'pomegranate': 'Pulses',
            'coconut': 'Oil seeds',
            'coffee': 'Pulses'
        };

        const targetClass = cropToFertilizerMap[cropLower] || cropName;
        let matchedOption = null;

        // 1. Try exact or case-insensitive match on value or label
        for (let opt of cropSelect.options) {
            if (!opt.value) continue;
            const optVal = opt.value.toLowerCase().trim();
            const optText = opt.textContent.toLowerCase().trim();
            if (optVal === targetClass.toLowerCase().trim() || optVal === cropLower ||
                optText === targetClass.toLowerCase().trim() || optText.includes(cropLower)) {
                matchedOption = opt;
                break;
            }
        }

        if (matchedOption) {
            cropSelect.value = matchedOption.value;
        } else {
            // Add custom option with mapped target
            const displayLabel = cropName.charAt(0).toUpperCase() + cropName.slice(1);
            const newOption = new Option(displayLabel, targetClass, true, true);
            cropSelect.add(newOption);
            cropSelect.value = targetClass;
        }

        // Highlight auto-selected crop dropdown
        cropSelect.style.borderColor = 'var(--primary-color)';
        cropSelect.style.boxShadow = '0 0 0 3px rgba(46, 125, 50, 0.25)';
        setTimeout(() => {
            cropSelect.style.boxShadow = '';
        }, 1500);

        cropSelect.dispatchEvent(new Event('change'));
    }

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            if (analyzeBtn) {
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            }
            if (resultsContainer) {
                resultsContainer.classList.add('hidden');
            }

            // Get form data safely
            const formData = new FormData(form);
            const parseFormFloat = (key, fallback = 0) => {
                const val = parseFloat(formData.get(key));
                return isNaN(val) ? fallback : val;
            };

            const data = {
                temperature: parseFormFloat('temperature'),
                humidity: parseFormFloat('humidity'),
                moisture: parseFormFloat('moisture'),
                soilType: String(formData.get('soilType') || '').trim(),
                cropType: String(formData.get('cropType') || '').trim(),
                nitrogen: parseFormFloat('nitrogen'),
                potassium: parseFormFloat('potassium'),
                phosphorous: parseFormFloat('phosphorous')
            };

            try {
                // Make API call
                const response = await fetch('/api/predict-fertilizer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result && result.success && result.result) {
                    displayResults(result.result);
                } else {
                    showError(result ? (result.error || 'An error occurred during prediction') : 'Prediction failed');
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Network error. Please try again.');
            } finally {
                // Reset button state
                if (analyzeBtn) {
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerHTML = originalBtnText;
                }
            }
        });
    }

    function displayResults(result) {
        if (!result) return;
        // Hide placeholder and show results
        const placeholderContainer = document.getElementById('placeholderContainer');
        if (placeholderContainer) {
            placeholderContainer.style.display = 'none';
        }
        
        const fertName = result.fertilizer ? String(result.fertilizer) : 'Recommended Fertilizer';
        const soilAdv = result.soil_advice ? String(result.soil_advice) : 'Soil nutrients are being analyzed.';

        // Display fertilizer name
        const fnEl = document.getElementById('fertilizerName');
        if (fnEl) fnEl.textContent = fertName;
        const ftEl = document.getElementById('fertilizerType');
        if (ftEl) ftEl.textContent = fertName;
        
        // Display soil advice
        const saEl = document.getElementById('soilAdvice');
        if (saEl) saEl.innerHTML = '<p>' + soilAdv + '</p>';
        
        // Update fertilizer image icon based on fertilizer type
        const fertilizerImage = document.getElementById('fertilizerImage');
        if (fertilizerImage) {
            const fertLower = fertName.toLowerCase();
            if (fertLower.includes('urea')) {
                fertilizerImage.innerHTML = '<i class="fas fa-flask"></i>';
            } else if (fertLower.includes('dap')) {
                fertilizerImage.innerHTML = '<i class="fas fa-atom"></i>';
            } else {
                fertilizerImage.innerHTML = '<i class="fas fa-seedling"></i>';
            }
        }

        // Inject context for chatbot (soil health focus)
        try {
            window.chatContext = {
                feature: "soil_health",
                recommendation: soilAdv,
                fertilizer: fertName
            };
        } catch (e) {
            // Ignore context errors
        }

        // Show results with animation
        if (resultsContainer) {
            resultsContainer.classList.remove('hidden');
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }

    function showError(message) {
        alert('Error: ' + message);
    }

    // Form validation
    if (form) {
        const inputs = form.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                const value = parseFloat(this.value);
                const min = parseFloat(this.min);
                const max = parseFloat(this.max);
                
                if (!isNaN(value) && !isNaN(min) && value < min) {
                    this.setCustomValidity(`Value must be >= ${min}`);
                } else if (!isNaN(value) && !isNaN(max) && value > max) {
                    this.setCustomValidity(`Value must be <= ${max}`);
                } else {
                    this.setCustomValidity('');
                }
            });
        });
    }
});
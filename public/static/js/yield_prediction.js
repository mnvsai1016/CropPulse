// Yield Prediction Page JavaScript
// Handles form submission, API calls, and result display

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('yieldForm');
    const predictBtn = document.getElementById('predictBtn');
    const calculateBtn = document.getElementById('calculateBtn');
    const getYieldSoilHealthBtn = document.getElementById('getYieldSoilHealthBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    const placeholderContainer = document.getElementById('placeholderContainer');
    
    let currentYieldData = null;

    // Auto-select crop from URL parameters (e.g. redirected from Crop Recommendation)
    const urlParams = new URLSearchParams(window.location.search);
    const cropParam = urlParams.get('crop');
    if (cropParam) {
        selectYieldCrop(cropParam);
    }

    function selectYieldCrop(cropName) {
        const cropSelect = document.getElementById('crop');
        if (!cropSelect || !cropName) return;

        const cropLower = cropName.toLowerCase().trim();
        const cropToYieldMap = {
            'apple': 'Apple',
            'banana': 'Banana',
            'blackgram': 'Blackgram',
            'chickpea': 'Gram',
            'coconut': 'Coconut ',
            'coffee': 'Coffee',
            'cotton': 'Cotton(lint)',
            'grapes': 'Grapes',
            'jute': 'Jute',
            'kidneybeans': 'Rajmash Kholar',
            'lentil': 'Lentil',
            'maize': 'Maize',
            'mango': 'Mango',
            'mothbeans': 'Moth',
            'mungbean': 'Moong(Green Gram)',
            'muskmelon': 'Water Melon',
            'orange': 'Orange',
            'papaya': 'Papaya',
            'pigeonpeas': 'Arhar/Tur',
            'pomegranate': 'Pome Granet',
            'rice': 'Rice',
            'watermelon': 'Water Melon'
        };

        const targetCrop = cropToYieldMap[cropLower] || cropName;
        let matchedOption = null;

        // 1. Try exact or case-insensitive match on value or label
        for (let opt of cropSelect.options) {
            if (!opt.value) continue;
            const optVal = opt.value.toLowerCase().trim();
            const optText = opt.textContent.toLowerCase().trim();
            if (optVal === targetCrop.toLowerCase().trim() || optVal === cropLower ||
                optText === targetCrop.toLowerCase().trim() || optText === cropLower) {
                matchedOption = opt;
                break;
            }
        }

        // 2. Try substring match if no exact match
        if (!matchedOption) {
            for (let opt of cropSelect.options) {
                if (!opt.value) continue;
                const optVal = opt.value.toLowerCase().trim();
                if (optVal.includes(cropLower) || cropLower.includes(optVal)) {
                    matchedOption = opt;
                    break;
                }
            }
        }

        if (matchedOption) {
            cropSelect.value = matchedOption.value;
        } else {
            // Add custom option with mapped target
            const displayLabel = cropName.charAt(0).toUpperCase() + cropName.slice(1);
            const newOption = new Option(displayLabel, targetCrop, true, true);
            cropSelect.add(newOption);
            cropSelect.value = targetCrop;
        }

        // Visual feedback highlight
        cropSelect.style.borderColor = 'var(--primary-color)';
        cropSelect.style.boxShadow = '0 0 0 3px rgba(46, 125, 50, 0.25)';
        setTimeout(() => {
            cropSelect.style.boxShadow = '';
        }, 1500);

        cropSelect.dispatchEvent(new Event('change'));
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

            const stateEl = document.getElementById('state');
            const districtEl = document.getElementById('district');
            const seasonEl = document.getElementById('season');
            const cropEl = document.getElementById('crop');
            const areaEl = document.getElementById('area');

            const areaVal = areaEl ? parseFloat(areaEl.value) : 0;
            if (isNaN(areaVal) || areaVal <= 0) {
                if (areaEl) {
                    areaEl.setCustomValidity('Please enter a valid positive area');
                    areaEl.reportValidity();
                }
                return;
            }

            // Get form data safely
            const formData = {
                state: stateEl ? stateEl.value : '',
                district: districtEl ? districtEl.value : '',
                season: seasonEl ? seasonEl.value : '',
                crop: cropEl ? cropEl.value : '',
                area: areaVal
            };

            // Show loading state
            if (predictBtn) {
                predictBtn.disabled = true;
                predictBtn.innerHTML = '<span class="spinner"></span> Predicting...';
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
                const response = await fetch('/api/predict-yield', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data && data.success && data.result) {
                    currentYieldData = data.result;
                    displayResults(data.result);
                } else {
                    showError(data ? (data.error || 'An error occurred during prediction') : 'Prediction failed');
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Failed to connect to the server. Please try again.');
            } finally {
                // Reset button
                if (predictBtn) {
                    predictBtn.disabled = false;
                    predictBtn.innerHTML = '<i class="fas fa-chart-line"></i> Predict Yield';
                }
            }
        });
    }

    // Revenue calculator
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function() {
            if (!currentYieldData) {
                alert('Please predict yield first');
                return;
            }

            const mpEl = document.getElementById('marketPrice');
            const marketPrice = mpEl ? parseFloat(mpEl.value) : NaN;
            
            if (isNaN(marketPrice) || marketPrice <= 0) {
                alert('Please enter a valid market price greater than 0');
                if (mpEl) mpEl.focus();
                return;
            }

            const totalY = typeof currentYieldData.total_yield === 'number' ? currentYieldData.total_yield : parseFloat(currentYieldData.total_yield) || 0;
            const totalRevenue = totalY * marketPrice;
            const revenueResult = document.getElementById('revenueResult');
            const revenueAmount = document.getElementById('revenueAmount');

            if (revenueResult && revenueAmount) {
                revenueAmount.textContent = totalRevenue.toLocaleString('en-IN', {
                    maximumFractionDigits: 2
                });
                revenueResult.classList.remove('hidden');
                revenueResult.style.animation = 'fadeInUp 0.5s ease';
            }
        });
    }

    // Cross-navigation to Soil Health & Fertilizer Advisor
    if (getYieldSoilHealthBtn) {
        getYieldSoilHealthBtn.addEventListener('click', function() {
            const cropSelect = document.getElementById('crop');
            const cropVal = cropSelect ? cropSelect.value : '';
            if (cropVal) {
                window.location.href = `/soil-health?crop=${encodeURIComponent(cropVal)}`;
            }
        });
    }

    function showLoadingState() {
        const ty = document.getElementById('totalYield');
        if (ty) ty.textContent = '...';
        const yph = document.getElementById('yieldPerHectare');
        if (yph) yph.textContent = 'Calculating...';
        if (getYieldSoilHealthBtn) getYieldSoilHealthBtn.disabled = true;
    }

    function displayResults(result) {
        if (!result) return;
        const totalYield = typeof result.total_yield === 'number' ? result.total_yield : parseFloat(result.total_yield) || 0;
        const yieldPerHectare = typeof result.yield_per_hectare === 'number' ? result.yield_per_hectare : parseFloat(result.yield_per_hectare) || 0;
        const area = typeof result.area === 'number' ? result.area : parseFloat(result.area) || 0;

        // Animate total yield
        animateValue('totalYield', 0, totalYield, 1000, ' Tonnes');
        
        // Update yield per hectare
        const yphEl = document.getElementById('yieldPerHectare');
        if (yphEl) {
            yphEl.textContent = `${yieldPerHectare.toFixed(2)} Tonnes per Hectare (for ${area} hectares)`;
        }

        // Enable soil health cross-navigation button
        if (getYieldSoilHealthBtn) getYieldSoilHealthBtn.disabled = false;

        // Inject context for chatbot
        try {
            const cropSelect = document.getElementById('crop');
            const cropName = cropSelect ? (cropSelect.options[cropSelect.selectedIndex]?.text || cropSelect.value) : '';
            const stateSelect = document.getElementById('state');
            const stateName = stateSelect ? stateSelect.value : '';
            const seasonSelect = document.getElementById('season');
            const seasonName = seasonSelect ? seasonSelect.value : '';

            window.chatContext = {
                feature: "yield_prediction",
                crop: cropName,
                yield: yieldPerHectare,
                total_yield: totalYield,
                area: area,
                state: stateName,
                season: seasonName
            };
        } catch (e) {
            // Ignore context errors
        }

        // Reset revenue calculator
        const mpEl = document.getElementById('marketPrice');
        if (mpEl) mpEl.value = '';
        const revenueResult = document.getElementById('revenueResult');
        if (revenueResult) {
            revenueResult.classList.add('hidden');
        }

        // Animate result appearance
        if (resultsContainer) {
            resultsContainer.classList.add('fade-in');
        }
    }

    function animateValue(elementId, start, end, duration, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        if (isNaN(end)) {
            element.textContent = '0.00' + suffix;
            return;
        }

        const range = end - start;
        if (range === 0 || duration <= 0) {
            element.textContent = end.toFixed(2) + suffix;
            return;
        }

        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = current.toFixed(2) + suffix;
        }, 16);
    }

    function showError(message) {
        const ty = document.getElementById('totalYield');
        if (ty) ty.textContent = 'Error';
        const yph = document.getElementById('yieldPerHectare');
        if (yph) yph.textContent = message || 'Prediction failed';
    }
});



/**
 * CropPulse Disease Scanner & Leaf Diagnostics Frontend
 */

let currentLeafFile = null;
window.lastDiseaseDiagnosis = null;

document.addEventListener('DOMContentLoaded', () => {
    // Set page context for CropPulse Assistant
    if (!window.chatContext) {
        window.chatContext = { feature: "disease_detection" };
    }

    const fileInput = document.getElementById('leafFileInput');
    const customFilePicker = document.getElementById('customFilePicker');
    const btnBrowseFile = document.getElementById('btnBrowseFile');
    const fileInputDisplayName = document.getElementById('fileInputDisplayName');
    const cameraBtn = document.getElementById('useCameraBtn');
    const cameraFileInput = document.getElementById('cameraFileInput');
    const emptyPreview = document.getElementById('emptyPreview');
    const filledPreview = document.getElementById('filledPreview');
    const previewImg = document.getElementById('previewImg');
    const previewFileName = document.getElementById('previewFileName');
    const previewFileSize = document.getElementById('previewFileSize');
    const btnRemoveImg = document.getElementById('btnRemoveImg');
    const scanBtn = document.getElementById('scanBtn');
    const askDiseaseChatBtn = document.getElementById('askDiseaseChatBtn');

    // 1. Custom File Picker Click -> triggers hidden file input
    if (customFilePicker && fileInput) {
        customFilePicker.addEventListener('click', (e) => {
            // Prevent duplicate triggers if clicking the button directly
            if (e.target !== btnBrowseFile) {
                fileInput.click();
            }
        });
    }

    if (btnBrowseFile && fileInput) {
        btnBrowseFile.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    // File Input Listener
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }

    // 2. Mobile Camera Button -> Triggers native camera capture input
    if (cameraBtn && cameraFileInput) {
        cameraBtn.addEventListener('click', () => {
            cameraFileInput.click();
        });

        cameraFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }

    // 3. Remove Selected Image
    if (btnRemoveImg) {
        btnRemoveImg.addEventListener('click', (e) => {
            e.stopPropagation();
            resetImageSelection();
        });
    }

    // 4. Drag and Drop Support
    setupDragAndDrop();

    // Allow tapping on the empty preview box to select a leaf photo on mobile
    const previewBoxContainer = document.getElementById('previewBoxContainer');
    if (previewBoxContainer && fileInput) {
        previewBoxContainer.addEventListener('click', (e) => {
            if (!currentLeafFile && !e.target.closest('#btnRemoveImg')) {
                fileInput.click();
            }
        });
    }

    // 5. Detect Disease Button
    if (scanBtn) {
        scanBtn.addEventListener('click', performDiagnosis);
    }

    // 6. Chatbot Inquire Button
    if (askDiseaseChatBtn) {
        askDiseaseChatBtn.addEventListener('click', askAssistantAboutDisease);
    }
});

/**
 * Configure Drag-and-Drop file handling on file picker and preview container
 */
function setupDragAndDrop() {
    const dropTargets = [
        document.getElementById('customFilePicker'),
        document.getElementById('previewBoxContainer'),
        document.querySelector('.preview-box-container')
    ].filter(Boolean);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Prevent default drag behaviors across the window so dropped files don't open in browser
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        window.addEventListener(eventName, (e) => {
            if (e.dataTransfer && e.dataTransfer.types && e.dataTransfer.types.includes('Files')) {
                preventDefaults(e);
            }
        }, false);

        dropTargets.forEach(target => {
            target.addEventListener(eventName, preventDefaults, false);
        });
    });

    // Add drag-over styling
    ['dragenter', 'dragover'].forEach(eventName => {
        dropTargets.forEach(target => {
            target.addEventListener(eventName, () => {
                target.classList.add('drag-over');
            }, false);
        });
    });

    // Remove drag-over styling
    ['dragleave', 'dragend'].forEach(eventName => {
        dropTargets.forEach(target => {
            target.addEventListener(eventName, (e) => {
                if (!target.contains(e.relatedTarget)) {
                    target.classList.remove('drag-over');
                }
            }, false);
        });
    });

    // Handle dropped file
    dropTargets.forEach(target => {
        target.addEventListener('drop', (e) => {
            target.classList.remove('drag-over');
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length > 0) {
                handleFileSelection(dt.files[0]);
            }
        }, false);
    });
}

/**
 * Safely truncate extra long filenames with middle ellipsis (e.g. MyLongName...jpg)
 */
function truncateFileName(name, maxLength = 32) {
    if (!name || name.length <= maxLength) return name;
    const extIndex = name.lastIndexOf('.');
    const ext = extIndex !== -1 ? name.slice(extIndex) : '';
    const base = extIndex !== -1 ? name.slice(0, extIndex) : name;
    const keepChars = maxLength - ext.length - 3;
    if (keepChars <= 4) return name.slice(0, maxLength - 3) + '...';
    const front = Math.ceil(keepChars / 2);
    const back = Math.floor(keepChars / 2);
    return `${base.slice(0, front)}...${base.slice(-back)}${ext}`;
}

/**
 * Handle incoming file and display preview safely without layout overflow
 */
function handleFileSelection(file) {
    if (!file) return;

    if (!file.type.match('image.*')) {
        alert('Please upload a valid image file (JPG, PNG, or WEBP).');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        alert('File size exceeds 10MB limit. Please upload a smaller image.');
        return;
    }

    currentLeafFile = file;

    const fileInputDisplayName = document.getElementById('fileInputDisplayName');
    const emptyPreview = document.getElementById('emptyPreview');
    const filledPreview = document.getElementById('filledPreview');
    const previewImg = document.getElementById('previewImg');
    const previewFileName = document.getElementById('previewFileName');
    const previewFileSize = document.getElementById('previewFileSize');
    const scanBtn = document.getElementById('scanBtn');

    // Update input display name
    if (fileInputDisplayName) {
        fileInputDisplayName.textContent = truncateFileName(file.name, 30);
        fileInputDisplayName.title = file.name;
    }

    // Read and display preview
    const reader = new FileReader();
    reader.onload = (e) => {
        if (previewImg) previewImg.src = e.target.result;
        if (previewFileName) {
            previewFileName.textContent = truncateFileName(file.name, 32);
            previewFileName.title = file.name;
        }
        if (previewFileSize) previewFileSize.textContent = formatBytes(file.size);
        
        if (emptyPreview) emptyPreview.style.display = 'none';
        if (filledPreview) filledPreview.style.display = 'flex';
        if (scanBtn) scanBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

/**
 * Reset image state
 */
function resetImageSelection() {
    currentLeafFile = null;
    const fileInput = document.getElementById('leafFileInput');
    const cameraFileInput = document.getElementById('cameraFileInput');
    const fileInputDisplayName = document.getElementById('fileInputDisplayName');
    const previewImg = document.getElementById('previewImg');
    if (fileInput) fileInput.value = '';
    if (cameraFileInput) cameraFileInput.value = '';
    if (fileInputDisplayName) {
        fileInputDisplayName.textContent = 'No file chosen';
        fileInputDisplayName.removeAttribute('title');
    }
    if (previewImg) {
        previewImg.src = '';
    }

    const emptyPreview = document.getElementById('emptyPreview');
    const filledPreview = document.getElementById('filledPreview');
    if (emptyPreview) emptyPreview.style.display = 'flex';
    if (filledPreview) filledPreview.style.display = 'none';

    const scanBtn = document.getElementById('scanBtn');
    if (scanBtn) scanBtn.disabled = true;
}

/**
 * Send image to diagnosis endpoint
 */
async function performDiagnosis() {
    if (!currentLeafFile) {
        alert('Please select or upload a leaf photo first.');
        return;
    }

    const scanBtn = document.getElementById('scanBtn');
    const origText = scanBtn.innerHTML;
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing Leaf Features...';

    const formData = new FormData();
    formData.append('file', currentLeafFile);

    try {
        // Trigger /api/detect-disease endpoint with fallback to /api/predict-disease
        let response;
        try {
            response = await fetch('/api/detect-disease', {
                method: 'POST',
                body: formData
            });
            if (response.status === 404) {
                response = await fetch('/api/predict-disease', {
                    method: 'POST',
                    body: formData
                });
            }
        } catch (_) {
            response = await fetch('/api/predict-disease', {
                method: 'POST',
                body: formData
            });
        }

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Server error occurred during analysis');
        }

        renderDiagnosisResults(data.result);
    } catch (err) {
        console.error('Diagnosis failed:', err);
        alert(`Diagnosis failed: ${err.message}`);
    } finally {
        scanBtn.disabled = false;
        scanBtn.innerHTML = origText;
    }
}

/**
 * Render diagnostic results into DOM
 */
function renderDiagnosisResults(res) {
    if (!res) return;

    window.lastDiseaseDiagnosis = res;
    window.chatContext = {
        feature: "disease_detection",
        crop: res.crop,
        disease: res.disease_name,
        severity: res.severity,
        pathogen_type: res.pathogen_type,
        organic_treatment: res.organic_treatment,
        chemical_treatment: res.chemical_treatment,
        prevention: res.prevention
    };

    const placeholder = document.getElementById('placeholderContainer');
    const results = document.getElementById('resultsContainer');
    if (placeholder) placeholder.style.display = 'none';
    if (results) results.style.display = 'block';

    // Status Banner
    const statusBanner = document.getElementById('statusBanner');
    const statusIcon = document.getElementById('statusIcon');
    const diagnosisTitle = document.getElementById('diagnosisTitle');
    const cropNameText = document.getElementById('cropNameText');
    const pathogenText = document.getElementById('pathogenText');
    const severityPill = document.getElementById('severityPill');

    const isHealthy = (res.status || '').toLowerCase() === 'healthy';

    if (statusBanner && statusIcon && severityPill) {
        if (isHealthy) {
            statusBanner.className = 'status-banner healthy';
            statusIcon.className = 'fas fa-check-circle';
            severityPill.className = 'severity-pill none';
            severityPill.textContent = 'Healthy Tissue';
        } else {
            statusBanner.className = 'status-banner diseased';
            statusIcon.className = 'fas fa-exclamation-triangle';
            const sev = (res.severity || 'Moderate').toLowerCase();
            if (sev.includes('high')) {
                severityPill.className = 'severity-pill high';
            } else if (sev.includes('low')) {
                severityPill.className = 'severity-pill low';
            } else {
                severityPill.className = 'severity-pill moderate';
            }
            severityPill.textContent = `${res.severity || 'Active'} Severity`;
        }
    }

    if (diagnosisTitle) diagnosisTitle.textContent = res.disease_name || 'Diagnosed Condition';
    if (cropNameText) cropNameText.textContent = res.crop || 'Crop';
    if (pathogenText) pathogenText.textContent = res.pathogen_type || 'Biological';

    // Confidence
    const confVal = typeof res.confidence === 'number' ? res.confidence : parseFloat(res.confidence || 90.0);
    const confidenceValueText = document.getElementById('confidenceValueText');
    const confidenceBarFill = document.getElementById('confidenceBarFill');
    if (confidenceValueText) confidenceValueText.textContent = `${confVal.toFixed(1)}%`;
    if (confidenceBarFill) confidenceBarFill.style.width = `${Math.min(100, Math.max(5, confVal))}%`;

    // Overview & Actionable Treatments
    const diagnosisDesc = document.getElementById('diagnosisDescription');
    const organicTreatment = document.getElementById('organicTreatmentText');
    const chemicalTreatment = document.getElementById('chemicalTreatmentText');
    const prevention = document.getElementById('preventionText');

    if (diagnosisDesc) diagnosisDesc.textContent = res.description || 'No description provided.';
    if (organicTreatment) organicTreatment.textContent = res.organic_treatment || 'No organic remedies specified.';
    if (chemicalTreatment) chemicalTreatment.textContent = res.chemical_treatment || 'No chemical remedies specified.';
    if (prevention) prevention.textContent = res.prevention || 'No preventive guidelines available.';

    // Top ensemble candidates
    const candidatesList = document.getElementById('candidatesList');
    if (candidatesList) {
        candidatesList.innerHTML = '';
        const candidates = Array.isArray(res.top_candidates) ? res.top_candidates : [];
        if (candidates.length === 0) {
            candidatesList.innerHTML = '<div style="font-size:0.85rem;color:#777;padding:0.3rem;">No alternative candidates recorded.</div>';
        } else {
            candidates.forEach(cand => {
                const row = document.createElement('div');
                row.className = 'candidate-row';
                const cScore = typeof cand.confidence === 'number' 
                    ? cand.confidence.toFixed(1) 
                    : parseFloat(cand.confidence || 0).toFixed(1);
                row.innerHTML = `
                    <span class="candidate-name" title="${escapeHtml(cand.disease_name || 'Candidate')}">${escapeHtml(cand.disease_name || 'Candidate')}</span>
                    <span class="candidate-score">${cScore}%</span>
                `;
                candidatesList.appendChild(row);
            });
        }
    }

    // Scroll smoothly to results on mobile devices
    if (window.innerWidth < 768 && results) {
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Seamlessly open chatbot with diagnosis inquiry
 */
function askAssistantAboutDisease() {
    const res = window.lastDiseaseDiagnosis;
    if (res) {
        window.chatContext = {
            feature: "disease_detection",
            crop: res.crop,
            disease: res.disease_name,
            severity: res.severity,
            pathogen_type: res.pathogen_type,
            organic_treatment: res.organic_treatment,
            chemical_treatment: res.chemical_treatment,
            prevention: res.prevention
        };
    }
    const prompt = res 
        ? `I just scanned a ${res.crop} leaf showing signs of "${res.disease_name}". Can you explain the treatment schedule and preventive management steps?`
        : `How can I identify and treat foliar crop fungal diseases?`;

    const chatWindow = document.getElementById('chat-window');
    if (typeof toggleChat === 'function') {
        if (chatWindow && (chatWindow.style.display === 'none' || !chatWindow.style.display)) {
            toggleChat();
        }
    } else if (chatWindow) {
        chatWindow.style.display = 'flex';
    }

    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = prompt;
        // Auto-expand textarea height to fit prompt smoothly
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 80) + 'px';
        chatInput.focus();
        chatInput.dispatchEvent(new Event('input', { bubbles: true }));

        if (window.innerWidth < 768) {
            chatInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

// Make accessible to inline onclick handlers
window.askAssistantAboutDisease = askAssistantAboutDisease;

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
/**
 * CropPulse Disease Scanner & Leaf Diagnostics Frontend
 */

let currentLeafFile = null;
window.lastDiseaseDiagnosis = null;

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('leafFileInput');
    const cameraBtn = document.getElementById('useCameraBtn');
    const cameraFileInput = document.getElementById('cameraFileInput');
    const emptyPreview = document.getElementById('emptyPreview');
    const filledPreview = document.getElementById('filledPreview');
    const previewImg = document.getElementById('previewImg');
    const previewFileName = document.getElementById('previewFileName');
    const previewFileSize = document.getElementById('previewFileSize');
    const btnRemoveImg = document.getElementById('btnRemoveImg');
    const scanBtn = document.getElementById('scanBtn');
    const sampleBtns = document.querySelectorAll('.sample-pill-btn');

    // 1. File Input Listener
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

    // 3. Quick Test Sample Buttons
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const src = btn.getAttribute('data-src');
            const name = btn.getAttribute('data-name') || 'sample_leaf.jpg';

            sampleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            try {
                scanBtn.disabled = true;
                scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading Sample...';

                const response = await fetch(src);
                const blob = await response.blob();
                const file = new File([blob], name, { type: blob.type || 'image/jpeg' });
                handleFileSelection(file);
            } catch (err) {
                console.error('Failed to load sample image:', err);
                alert('Could not load sample image. Please try uploading an image directly.');
            } finally {
                scanBtn.innerHTML = '<i class="fas fa-search"></i> Detect Disease';
                scanBtn.disabled = false;
            }
        });
    });

    // 4. Remove Selected Image
    if (btnRemoveImg) {
        btnRemoveImg.addEventListener('click', (e) => {
            e.stopPropagation();
            resetImageSelection();
        });
    }

    // 5. Detect Disease Button
    if (scanBtn) {
        scanBtn.addEventListener('click', performDiagnosis);
    }
});

/**
 * Handle incoming file and display preview
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

    const emptyPreview = document.getElementById('emptyPreview');
    const filledPreview = document.getElementById('filledPreview');
    const previewImg = document.getElementById('previewImg');
    const previewFileName = document.getElementById('previewFileName');
    const previewFileSize = document.getElementById('previewFileSize');
    const scanBtn = document.getElementById('scanBtn');

    // Read and display preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewFileName.textContent = file.name;
        previewFileSize.textContent = formatBytes(file.size);
        
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
    if (fileInput) fileInput.value = '';
    if (cameraFileInput) cameraFileInput.value = '';

    const emptyPreview = document.getElementById('emptyPreview');
    const filledPreview = document.getElementById('filledPreview');
    if (emptyPreview) emptyPreview.style.display = 'flex';
    if (filledPreview) filledPreview.style.display = 'none';

    const scanBtn = document.getElementById('scanBtn');
    if (scanBtn) scanBtn.disabled = true;

    document.querySelectorAll('.sample-pill-btn').forEach(b => b.classList.remove('active'));
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
        const response = await fetch('/api/predict-disease', {
            method: 'POST',
            body: formData
        });

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
    window.lastDiseaseDiagnosis = res;

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
        } else {
            severityPill.className = 'severity-pill moderate';
        }
        severityPill.textContent = `${res.severity || 'Active'} Severity`;
    }

    diagnosisTitle.textContent = res.disease_name || 'Diagnosed Condition';
    cropNameText.textContent = res.crop || 'Crop';
    pathogenText.textContent = res.pathogen_type || 'Biological';

    // Confidence
    const confVal = res.confidence !== undefined ? res.confidence : 90.0;
    const confidenceValueText = document.getElementById('confidenceValueText');
    const confidenceBarFill = document.getElementById('confidenceBarFill');
    if (confidenceValueText) confidenceValueText.textContent = `${confVal.toFixed(1)}%`;
    if (confidenceBarFill) confidenceBarFill.style.width = `${Math.min(100, Math.max(10, confVal))}%`;

    // Overview & Treatments
    document.getElementById('diagnosisDescription').textContent = res.description || 'No description provided.';
    document.getElementById('organicTreatmentText').textContent = res.organic_treatment || 'No organic remedies specified.';
    document.getElementById('chemicalTreatmentText').textContent = res.chemical_treatment || 'No chemical remedies specified.';
    document.getElementById('preventionText').textContent = res.prevention || 'No preventive guidelines available.';

    // Top ensemble candidates
    const candidatesList = document.getElementById('candidatesList');
    if (candidatesList) {
        candidatesList.innerHTML = '';
        const candidates = res.top_candidates || [];
        candidates.forEach(cand => {
            const row = document.createElement('div');
            row.className = 'candidate-row';
            row.innerHTML = `
                <span class="candidate-name">${escapeHtml(cand.disease_name)}</span>
                <span class="candidate-score">${cand.confidence.toFixed(1)}%</span>
            `;
            candidatesList.appendChild(row);
        });
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
    const prompt = res 
        ? `I just scanned a ${res.crop} leaf showing signs of "${res.disease_name}". Can you explain the treatment schedule and preventive management steps?`
        : `How can I identify and treat foliar crop fungal diseases?`;

    if (typeof toggleChat === 'function') {
        const chatWindow = document.getElementById('chat-window');
        if (chatWindow && chatWindow.style.display !== 'flex') {
            toggleChat();
        }
    }

    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = prompt;
        chatInput.focus();
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

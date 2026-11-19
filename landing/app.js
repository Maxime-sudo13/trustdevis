/**
 * TrustDevis Landing Page - Application JavaScript
 * Handles file upload, analysis simulation, and UI interactions
 */

// ============================================
// DOM Elements
// ============================================
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const cameraInput = document.getElementById('camera-input');
const selectFileBtn = document.getElementById('select-file-btn');
const takePhotoBtn = document.getElementById('take-photo-btn');
const filePreview = document.getElementById('file-preview');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const removeFileBtn = document.getElementById('remove-file');
const rgpdConsent = document.getElementById('rgpd-consent');
const analyzeBtn = document.getElementById('analyze-btn');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultSection = document.getElementById('result-section');
const badgeCircle = document.querySelector('.badge-circle');
const badgeScore = document.getElementById('badge-score');
const badgeStatus = document.getElementById('badge-status');
const anomaliesList = document.getElementById('anomalies-list');
const userPrice = document.getElementById('user-price');
const marketPrice = document.getElementById('market-price');
const priceDiff = document.getElementById('price-diff');

// ============================================
// State
// ============================================
let currentFile = null;

// ============================================
// Event Listeners
// ============================================

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Click to select file
dropZone.addEventListener('click', (e) => {
    if (e.target !== selectFileBtn && e.target !== takePhotoBtn) {
        fileInput.click();
    }
});

selectFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Camera capture
takePhotoBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    cameraInput.click();
});

cameraInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Remove file
removeFileBtn.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    cameraInput.value = '';
    filePreview.style.display = 'none';
    updateAnalyzeButton();
});

// RGPD consent
rgpdConsent.addEventListener('change', updateAnalyzeButton);

// Analyze button
analyzeBtn.addEventListener('click', startAnalysis);

// ============================================
// Functions
// ============================================

function handleFile(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.pdf')) {
        alert('Veuillez sélectionner un fichier PDF ou une image (JPG, PNG)');
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('Le fichier est trop volumineux. Taille maximum : 10 Mo');
        return;
    }
    
    currentFile = file;
    
    // Update preview
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    filePreview.style.display = 'block';
    
    updateAnalyzeButton();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateAnalyzeButton() {
    analyzeBtn.disabled = !(currentFile && rgpdConsent.checked);
}

function startAnalysis() {
    if (!currentFile || !rgpdConsent.checked) return;
    
    // Hide upload, show progress
    dropZone.style.display = 'none';
    filePreview.style.display = 'none';
    document.querySelector('.rgpd-checkbox').style.display = 'none';
    analyzeBtn.style.display = 'none';
    progressContainer.style.display = 'block';
    
    // Simulate analysis progress
    simulateAnalysis();
}

function simulateAnalysis() {
    const steps = [
        { progress: 15, text: 'Upload du fichier...', step: 1 },
        { progress: 35, text: 'Extraction du texte (OCR)...', step: 2 },
        { progress: 60, text: 'Analyse des prix...', step: 3 },
        { progress: 85, text: 'Comparaison avec le marché...', step: 3 },
        { progress: 100, text: 'Génération du rapport...', step: 4 }
    ];
    
    let currentStep = 0;
    
    const interval = setInterval(() => {
        if (currentStep >= steps.length) {
            clearInterval(interval);
            showResults();
            return;
        }
        
        const step = steps[currentStep];
        progressFill.style.width = step.progress + '%';
        progressText.textContent = step.text;
        updateProgressSteps(step.step);
        
        currentStep++;
    }, 800);
}

function updateProgressSteps(activeStep) {
    const steps = document.querySelectorAll('.progress-steps .step');
    steps.forEach((step, index) => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');
        
        if (stepNum === activeStep) {
            step.classList.add('active');
        } else if (stepNum < activeStep) {
            step.classList.add('completed');
        }
    });
}

function showResults() {
    // Generate random score for demo (weighted towards middle)
    const random = Math.random();
    let score;
    if (random < 0.2) {
        score = Math.floor(Math.random() * 40); // 0-40 (red)
    } else if (random < 0.5) {
        score = Math.floor(Math.random() * 30) + 41; // 41-70 (orange)
    } else {
        score = Math.floor(Math.random() * 30) + 71; // 71-100 (green)
    }
    
    // Show result section
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Animate score
    animateScore(score);
    
    // Set badge color and status
    setTimeout(() => {
        updateBadge(score);
        generateAnomalies(score);
        generateMarketComparison(score);
    }, 500);
}

function animateScore(targetScore) {
    let current = 0;
    const duration = 1500;
    const increment = targetScore / (duration / 16);
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= targetScore) {
            current = targetScore;
            clearInterval(timer);
        }
        badgeScore.textContent = Math.floor(current);
    }, 16);
}

function updateBadge(score) {
    badgeCircle.classList.remove('red', 'orange', 'green');
    badgeStatus.classList.remove('red', 'orange', 'green');
    
    let statusText, statusIcon, colorClass;
    
    if (score <= 40) {
        colorClass = 'red';
        statusText = 'Risque élevé - Vérifiez les points';
        statusIcon = '⚠️';
    } else if (score <= 70) {
        colorClass = 'orange';
        statusText = 'Attention - Quelques anomalies';
        statusIcon = '⚡';
    } else {
        colorClass = 'green';
        statusText = 'Devis conforme au marché';
        statusIcon = '✅';
    }
    
    badgeCircle.classList.add(colorClass);
    badgeStatus.classList.add(colorClass);
    badgeStatus.innerHTML = `<span class="status-icon">${statusIcon}</span><span class="status-text">${statusText}</span>`;
}

function generateAnomalies(score) {
    const anomalies = [];
    
    if (score <= 40) {
        anomalies.push(
            { icon: '⚠️', title: 'Prix supérieur au marché', desc: 'Le prix global est 35% au-dessus de la médiane constatée.' },
            { icon: '💰', title: 'Ligne "Frais de déplacement"', desc: '120€ - Tarif inhabituellement élevé pour la zone.' },
            { icon: '📋', title: 'Description imprécise', desc: 'La main d\'œuvre n\'est pas détaillée par poste.' }
        );
    } else if (score <= 70) {
        anomalies.push(
            { icon: '⚡', title: 'Ligne "Matériaux"', desc: 'Prix légèrement supérieur (+12%) à la moyenne du marché.' },
            { icon: '📋', title: 'Délai non précisé', desc: 'Aucune indication sur la durée des travaux.' }
        );
    } else {
        anomalies.push(
            { icon: '✅', title: 'Prix conforme', desc: 'Les prix sont alignés avec les tarifs du marché.' },
            { icon: '📋', title: 'Devis complet', desc: 'Toutes les informations légales sont présentes.' }
        );
    }
    
    anomaliesList.innerHTML = anomalies.map(a => `
        <div class="anomaly-item fade-in">
            <span class="anomaly-icon">${a.icon}</span>
            <div class="anomaly-content">
                <h4>${a.title}</h4>
                <p>${a.desc}</p>
            </div>
        </div>
    `).join('');
}

function generateMarketComparison(score) {
    // Generate realistic prices based on score
    const basePrice = 2500 + Math.floor(Math.random() * 5000);
    let marketPriceValue;
    
    if (score <= 40) {
        marketPriceValue = Math.round(basePrice * 0.75);
    } else if (score <= 70) {
        marketPriceValue = Math.round(basePrice * 0.9);
    } else {
        marketPriceValue = Math.round(basePrice * 0.98);
    }
    
    const diff = basePrice - marketPriceValue;
    const diffPercent = Math.round((diff / marketPriceValue) * 100);
    
    userPrice.textContent = formatPrice(basePrice);
    marketPrice.textContent = formatPrice(marketPriceValue);
    
    if (diff > 0) {
        priceDiff.textContent = `+${diffPercent}% (${formatPrice(diff)})`;
        priceDiff.style.color = 'var(--color-danger)';
    } else if (diff < 0) {
        priceDiff.textContent = `${diffPercent}% (${formatPrice(Math.abs(diff))})`;
        priceDiff.style.color = 'var(--color-success)';
    } else {
        priceDiff.textContent = 'Aligné';
        priceDiff.style.color = 'var(--color-success)';
    }
}

function formatPrice(amount) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// ============================================
// Counter Animation
// ============================================
function animateCounter() {
    const counter = document.getElementById('devis-counter');
    const target = 12847;
    const duration = 2000;
    const start = 12000;
    const increment = (target - start) / (duration / 16);
    
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        counter.textContent = Math.floor(current).toLocaleString('fr-FR');
    }, 16);
}

// Start counter animation when page loads
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(animateCounter, 500);
});

// ============================================
// Smooth Scroll for Navigation Links
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// ============================================
// Mobile Menu Toggle (placeholder)
// ============================================
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
mobileMenuBtn.addEventListener('click', () => {
    // Mobile menu toggle functionality would go here
    console.log('Mobile menu clicked - implement menu toggle');
});

// ============================================
// Download PDF Button
// ============================================
document.getElementById('download-pdf').addEventListener('click', () => {
    alert('Fonctionnalité à venir : Téléchargement du rapport PDF détaillé');
});

// ============================================
// Get Detailed Analysis Button
// ============================================
document.getElementById('get-detailed-analysis').addEventListener('click', () => {
    alert('Redirection vers la page d\'inscription pour accéder à l\'analyse complète');
});

// ============================================
// Scroll Reveal Animation
// ============================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
        }
    });
}, observerOptions);

// Observe elements for reveal animation
document.querySelectorAll('.step-card, .testimonial-card, .pricing-card').forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
});
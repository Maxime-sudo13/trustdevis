// Générateur de Devis - TrustDevis

document.addEventListener('DOMContentLoaded', function() {
    // Éléments du formulaire
    const form = document.getElementById('generateur-form');
    const formSteps = document.querySelectorAll('.form-step');
    const stepItems = document.querySelectorAll('.step-item');
    const progressFill = document.getElementById('progress-fill-line');
    
    // Boutons navigation
    const btnStep1 = document.getElementById('btn-step-1');
    const btnStep2 = document.getElementById('btn-step-2');
    const btnPrev = document.querySelectorAll('.btn-prev');
    
    // Inputs étape 1
    const typeCards = document.querySelectorAll('input[name="type-travaux"]');
    const autreCheckbox = document.getElementById('autre-checkbox');
    const autreInput = document.getElementById('autre-input');
    
    // Inputs étape 2
    const surfaceInput = document.getElementById('surface');
    const descriptionInput = document.getElementById('description');
    const materiauxInputs = document.querySelectorAll('input[name="materiaux"]');
    
    // État courant
    let currentStep = 1;
    const formData = {
        typeTravaux: '',
        autreType: '',
        surface: '',
        description: '',
        materiaux: '',
        codePostal: '',
        email: '',
        telephone: '',
        urgence: 'standard'
    };
    
    // Prix de base par type de travaux (€/m²)
    const prixBase = {
        plomberie: { mo: 80, mat: 40 },
        electricite: { mo: 70, mat: 35 },
        peinture: { mo: 25, mat: 15 },
        carrelage: { mo: 45, mat: 30 },
        menuiserie: { mo: 90, mat: 120 },
        toiture: { mo: 60, mat: 80 },
        chauffage: { mo: 100, mat: 150 },
        renovation: { mo: 150, mat: 100 },
        autre: { mo: 75, mat: 50 }
    };
    
    // Multiplicateurs matériaux
    const multiplicateurs = {
        standard: { eco: 0.85, std: 1, prem: 1.3 },
        premium: { eco: 0.8, std: 1, prem: 1.4 },
        eco: { eco: 0.9, std: 1.1, prem: 1.2 }
    };
    
    // ========== ÉTAPE 1: Type de travaux ==========
    
    // Gestion sélection type de travaux
    typeCards.forEach(card => {
        card.addEventListener('change', function() {
            formData.typeTravaux = this.value;
            btnStep1.disabled = false;
            
            // Désactiver "autre" si un type est sélectionné
            if (autreCheckbox.checked) {
                autreCheckbox.checked = false;
                autreInput.disabled = true;
                autreInput.value = '';
            }
        });
    });
    
    // Gestion checkbox "autre"
    autreCheckbox.addEventListener('change', function() {
        autreInput.disabled = !this.checked;
        if (this.checked) {
            autreInput.focus();
            // Désélectionner les autres types
            typeCards.forEach(card => card.checked = false);
            btnStep1.disabled = autreInput.value.trim() === '';
        } else {
            autreInput.value = '';
            btnStep1.disabled = true;
        }
    });
    
    autreInput.addEventListener('input', function() {
        formData.autreType = this.value;
        btnStep1.disabled = this.value.trim() === '';
    });
    
    // Bouton étape 1
    btnStep1.addEventListener('click', function() {
        if (autreCheckbox.checked && autreInput.value.trim()) {
            formData.typeTravaux = 'autre';
            formData.autreType = autreInput.value.trim();
        }
        goToStep(2);
    });
    
    // ========== ÉTAPE 2: Détails ==========
    
    function checkStep2Validity() {
        const hasSurface = surfaceInput.value && parseInt(surfaceInput.value) > 0;
        const hasMateriaux = Array.from(materiauxInputs).some(input => input.checked);
        btnStep2.disabled = !(hasSurface && hasMateriaux);
    }
    
    surfaceInput.addEventListener('input', function() {
        formData.surface = this.value;
        checkStep2Validity();
    });
    
    descriptionInput.addEventListener('input', function() {
        formData.description = this.value;
    });
    
    materiauxInputs.forEach(input => {
        input.addEventListener('change', function() {
            formData.materiaux = this.value;
            checkStep2Validity();
        });
    });
    
    // Bouton étape 2
    btnStep2.addEventListener('click', function() {
        goToStep(3);
    });
    
    // ========== ÉTAPE 3: Contact ==========
    
    const codePostalInput = document.getElementById('code-postal');
    const emailInput = document.getElementById('email');
    const telephoneInput = document.getElementById('telephone');
    const urgenceInputs = document.querySelectorAll('input[name="urgence"]');
    const btnSubmit = document.getElementById('btn-submit');
    
    function checkStep3Validity() {
        const cpValid = /^[0-9]{5}$/.test(codePostalInput.value);
        const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value);
        btnSubmit.disabled = !(cpValid && emailValid);
    }
    
    codePostalInput.addEventListener('input', function() {
        formData.codePostal = this.value;
        checkStep3Validity();
    });
    
    emailInput.addEventListener('input', function() {
        formData.email = this.value;
        checkStep3Validity();
    });
    
    telephoneInput.addEventListener('input', function() {
        formData.telephone = this.value;
    });
    
    urgenceInputs.forEach(input => {
        input.addEventListener('change', function() {
            formData.urgence = this.value;
        });
    });
    
    // ========== Navigation ==========
    
    function goToStep(step) {
        // Masquer étape courante
        formSteps[currentStep - 1].classList.remove('active');
        
        // Afficher nouvelle étape
        currentStep = step;
        formSteps[currentStep - 1].classList.add('active');
        
        // Mettre à jour la progress bar
        updateProgressBar();
        
        // Scroll vers le formulaire
        document.getElementById('formulaire').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    function updateProgressBar() {
        // Mettre à jour la ligne de progression
        const progress = ((currentStep - 1) / 2) * 100;
        progressFill.style.width = progress + '%';
        
        // Mettre à jour les étapes
        stepItems.forEach((item, index) => {
            item.classList.remove('active', 'completed');
            if (index + 1 < currentStep) {
                item.classList.add('completed');
            } else if (index + 1 === currentStep) {
                item.classList.add('active');
            }
        });
    }
    
    // Boutons précédent
    btnPrev.forEach(btn => {
        btn.addEventListener('click', function() {
            goToStep(currentStep - 1);
        });
    });
    
    // ========== Soumission ==========
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Afficher le loading
        form.style.display = 'none';
        document.querySelector('.progress-steps-container').style.display = 'none';
        document.getElementById('loading-state').style.display = 'block';
        
        // Simuler le calcul
        let progress = 0;
        const loadingFill = document.querySelector('.loading-fill');
        const loadingPercent = document.querySelector('.loading-percent');
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;
            
            loadingFill.style.width = progress + '%';
            loadingPercent.textContent = Math.round(progress) + '%';
            
            if (progress === 100) {
                clearInterval(interval);
                setTimeout(() => {
                    showResults();
                }, 500);
            }
        }, 200);
    });
    
    // ========== Affichage résultats ==========
    
    function showResults() {
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('resultats-section').style.display = 'block';
        
        // Calculer les prix
        const prix = calculatePrices();
        
        // Afficher les prix
        document.getElementById('prix-economique').textContent = formatPrice(prix.economique.total);
        document.getElementById('mo-economique').textContent = formatPrice(prix.economique.mo) + ' €';
        document.getElementById('mat-economique').textContent = formatPrice(prix.economique.mat) + ' €';
        document.getElementById('duree-economique').textContent = prix.economique.duree;
        
        document.getElementById('prix-standard').textContent = formatPrice(prix.standard.total);
        document.getElementById('mo-standard').textContent = formatPrice(prix.standard.mo) + ' €';
        document.getElementById('mat-standard').textContent = formatPrice(prix.standard.mat) + ' €';
        document.getElementById('duree-standard').textContent = prix.standard.duree;
        
        document.getElementById('prix-premium').textContent = formatPrice(prix.premium.total);
        document.getElementById('mo-premium').textContent = formatPrice(prix.premium.mo) + ' €';
        document.getElementById('mat-premium').textContent = formatPrice(prix.premium.mat) + ' €';
        document.getElementById('duree-premium').textContent = prix.premium.duree;
        
        // Tableau comparatif
        document.getElementById('table-prix-eco').textContent = formatPrice(prix.economique.total) + ' €';
        document.getElementById('table-prix-std').textContent = formatPrice(prix.standard.total) + ' €';
        document.getElementById('table-prix-prem').textContent = formatPrice(prix.premium.total) + ' €';
        
        // Scroll vers les résultats
        document.getElementById('resultats-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    function calculatePrices() {
        const type = formData.typeTravaux || 'autre';
        const surface = parseInt(formData.surface) || 10;
        const materiaux = formData.materiaux || 'standard';
        
        const base = prixBase[type] || prixBase.autre;
        const mult = multiplicateurs[materiaux];
        
        // Calculer les prix
        const moEco = Math.round(base.mo * surface * mult.eco);
        const matEco = Math.round(base.mat * surface * mult.eco * 0.8);
        const totalEco = moEco + matEco;
        
        const moStd = Math.round(base.mo * surface * mult.std);
        const matStd = Math.round(base.mat * surface * mult.std);
        const totalStd = moStd + matStd;
        
        const moPrem = Math.round(base.mo * surface * mult.prem);
        const matPrem = Math.round(base.mat * surface * mult.prem * 1.3);
        const totalPrem = moPrem + matPrem;
        
        // Durées estimées (jours)
        const baseDuree = Math.max(1, Math.round(surface / 10));
        
        return {
            economique: {
                total: totalEco,
                mo: moEco,
                mat: matEco,
                duree: baseDuree + ' jour' + (baseDuree > 1 ? 's' : '')
            },
            standard: {
                total: totalStd,
                mo: moStd,
                mat: matStd,
                duree: Math.max(1, baseDuree - 1) + ' jour' + (Math.max(1, baseDuree - 1) > 1 ? 's' : '')
            },
            premium: {
                total: totalPrem,
                mo: moPrem,
                mat: matPrem,
                duree: Math.max(1, baseDuree - 2) + ' jour' + (Math.max(1, baseDuree - 2) > 1 ? 's' : '')
            }
        };
    }
    
    function formatPrice(price) {
        return price.toLocaleString('fr-FR');
    }
    
    // ========== Actions résultats ==========
    
    document.getElementById('btn-email').addEventListener('click', function() {
        alert('Les devis ont été envoyés à votre adresse email : ' + formData.email);
    });
    
    document.getElementById('btn-artisans').addEventListener('click', function() {
        alert('Votre demande a été transmise aux artisans de votre secteur. Ils vous contacteront sous 24h.');
    });
});

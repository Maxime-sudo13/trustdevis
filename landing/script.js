// TrustDevis Landing Page - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initCounter();
    initFAQ();
    initFormValidation();
    initSmoothScroll();
    initMobileMenu();
});

/**
 * Animated Counter
 * Animates the counter from 0 to target value
 */
function initCounter() {
    const counters = document.querySelectorAll('[data-target]');
    
    const animateCounter = (element) => {
        const target = parseInt(element.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const step = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current < target) {
                element.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        };
        
        updateCounter();
    };
    
    // Intersection Observer to trigger animation when visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

/**
 * FAQ Accordion
 * Toggle FAQ items open/close
 */
function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close all other items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current item
            item.classList.toggle('active');
        });
    });
}

/**
 * Form Validation
 * Validates the registration form
 */
function initFormValidation() {
    const form = document.getElementById('pilotForm');
    const formSuccess = document.getElementById('formSuccess');
    
    if (!form) return;
    
    const validators = {
        name: (value) => {
            if (!value.trim()) return 'Le nom est requis';
            if (value.trim().length < 2) return 'Le nom doit contenir au moins 2 caractères';
            return '';
        },
        email: (value) => {
            if (!value.trim()) return 'L\'email est requis';
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) return 'Veuillez entrer un email valide';
            return '';
        },
        phone: (value) => {
            if (!value.trim()) return 'Le téléphone est requis';
            const phoneRegex = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) return 'Veuillez entrer un numéro français valide';
            return '';
        },
        sector: (value) => {
            if (!value) return 'Veuillez sélectionner un secteur';
            return '';
        }
    };
    
    const showError = (input, message) => {
        const formGroup = input.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        input.classList.add('error');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('visible');
        }
    };
    
    const clearError = (input) => {
        const formGroup = input.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        input.classList.remove('error');
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.remove('visible');
        }
    };
    
    const validateField = (input) => {
        const name = input.name;
        const value = input.value;
        
        if (validators[name]) {
            const error = validators[name](value);
            if (error) {
                showError(input, error);
                return false;
            } else {
                clearError(input);
                return true;
            }
        }
        return true;
    };
    
    // Validate on blur
    form.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.classList.contains('error')) {
                validateField(input);
            }
        });
    });
    
    // Form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = true;
        const requiredFields = ['name', 'email', 'phone', 'sector'];
        
        requiredFields.forEach(fieldName => {
            const input = form.querySelector(`[name="${fieldName}"]`);
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        if (isValid) {
            // Simulate form submission
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="spinner">
                    <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2" stroke-dasharray="40" stroke-dashoffset="10">
                        <animateTransform attributeName="transform" type="rotate" from="0 10 10" to="360 10 10" dur="1s" repeatCount="indefinite"/>
                    </circle>
                </svg>
                Envoi en cours...
            `;
            
            setTimeout(() => {
                form.style.display = 'none';
                formSuccess.classList.add('visible');
                
                // Reset form for future use
                form.reset();
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 1500);
        }
    });
}

/**
 * Smooth Scroll
 * Smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Mobile Menu
 * Toggle mobile navigation
 */
function initMobileMenu() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (!menuBtn || !navLinks) return;
    
    menuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('mobile-open');
        menuBtn.classList.toggle('active');
    });
    
    // Close menu when clicking on a link
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('mobile-open');
            menuBtn.classList.remove('active');
        });
    });
}

/**
 * Scroll Reveal Animation
 * Reveal elements on scroll
 */
const initScrollReveal = () => {
    const revealElements = document.querySelectorAll('.problem-card, .solution-feature, .testimonial-card, .benefit');
    
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    revealElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = `opacity 0.5s ease ${index * 0.1}s, transform 0.5s ease ${index * 0.1}s`;
        revealObserver.observe(el);
    });
};

// Initialize scroll reveal after DOM is ready
document.addEventListener('DOMContentLoaded', initScrollReveal);

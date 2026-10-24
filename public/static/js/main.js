// Main JavaScript for Agri-Guide
// Handles navigation, mobile menu, and general UI interactions

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle & interactions
    const mobileMenu = document.getElementById('mobile-menu');
    const navMenu = document.querySelector('.nav-menu');

    function closeMobileNav() {
        if (navMenu) navMenu.classList.remove('active');
        if (mobileMenu) {
            mobileMenu.classList.remove('active');
            mobileMenu.setAttribute('aria-expanded', 'false');
        }
        document.body.classList.remove('mobile-nav-open');
    }

    if (mobileMenu) {
        mobileMenu.addEventListener('click', function(e) {
            e.stopPropagation();
            const willOpen = !navMenu.classList.contains('active');
            navMenu.classList.toggle('active', willOpen);
            mobileMenu.classList.toggle('active', willOpen);
            mobileMenu.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
            document.body.classList.toggle('mobile-nav-open', willOpen);

            // Mutual exclusion: close profile dropdown when opening hamburger
            if (willOpen && typeof window.closeProfileDropdown === 'function') {
                window.closeProfileDropdown();
            }
        });
    }

    // Close mobile menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            closeMobileNav();
        });
    });

    // Close mobile menu when clicking outside navbar
    document.addEventListener('click', function(e) {
        if (navMenu && navMenu.classList.contains('active')) {
            const navContainer = document.querySelector('.nav-container');
            if (navContainer && !navContainer.contains(e.target)) {
                closeMobileNav();
            }
        }
    });

    // Close mobile menu on Escape key press
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && navMenu && navMenu.classList.contains('active')) {
            closeMobileNav();
        }
    });

    // Clean up mobile drawer state if window is resized to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && navMenu && navMenu.classList.contains('active')) {
            closeMobileNav();
        }
    });

    // Expose close helper globally
    window.closeMobileNav = closeMobileNav;

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form input validation styling
    const inputs = document.querySelectorAll('.form-input, .form-select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('error');
            } else {
                this.classList.add('error');
            }
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('error') && this.checkValidity()) {
                this.classList.remove('error');
            }
        });
    });

    // Initialize CropPulse Plant Growing Intro Transition
    initPlantIntro();
});

// Plant Growing Transition Controller
function initPlantIntro() {
    const loader = document.getElementById('plant-intro-loader');
    if (!loader) return;

    // Check if user already saw the intro in this tab session
    const hasSeenIntro = sessionStorage.getItem('croppulse_intro_seen');
    if (hasSeenIntro) {
        loader.style.display = 'none';
        return;
    }

    // Auto transition out after plant reaches full growth (4.0s total)
    const autoDismiss = setTimeout(function() {
        dismissPlantIntro();
    }, 4000);

    window.dismissPlantIntro = function() {
        clearTimeout(autoDismiss);
        sessionStorage.setItem('croppulse_intro_seen', 'true');
        loader.classList.add('fade-out');
        setTimeout(function() {
            if (loader && loader.parentNode) {
                loader.style.display = 'none';
            }
        }, 750);
    };

    // Clicking anywhere on the screen allows the user to dismiss if desired
    loader.addEventListener('click', function() {
        dismissPlantIntro();
    });
}



document.addEventListener('DOMContentLoaded', function() {
    // Language switching functionality
    const languageSelect = document.getElementById('languageSelect');
    
    // Set initial language based on browser preference or default to English
    const userLang = navigator.language || navigator.userLanguage;
    let initialLang = 'en';
    if (userLang.startsWith('zh')) initialLang = 'zh';
    if (userLang.startsWith('ja')) initialLang = 'ja';
    
    document.documentElement.setAttribute('lang', initialLang);
    languageSelect.value = initialLang;
    updateContent(initialLang);

    languageSelect.addEventListener('change', function() {
        const lang = this.value;
        document.documentElement.setAttribute('lang', lang);
        updateContent(lang);
    });

    function updateContent(lang) {
        // Update all elements with data-en/data-zh/data-ja attributes
        document.querySelectorAll(`[data-${lang}]`).forEach(element => {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = element.getAttribute(`data-placeholder-${lang}`);
            } else {
                element.textContent = element.getAttribute(`data-${lang}`);
            }
        });

        // Update pricing display
        document.querySelectorAll('.price').forEach(price => {
            const amountElement = price.querySelector('.amount');
            if (amountElement) {
                let priceValue;
                switch(lang) {
                    case 'en':
                        priceValue = amountElement.getAttribute('data-price-usd');
                        break;
                    case 'zh':
                        priceValue = amountElement.getAttribute('data-price-cny');
                        break;
                    case 'ja':
                        priceValue = amountElement.getAttribute('data-price-jpy');
                        break;
                }
                amountElement.textContent = priceValue;
            }
        });

        // Show/hide currency symbols
        document.querySelectorAll('.currency-en, .currency-zh, .currency-ja').forEach(currency => {
            currency.style.display = 'none';
        });
        document.querySelectorAll(`.currency-${lang}`).forEach(currency => {
            currency.style.display = 'inline';
        });
    }

    // Pricing plan selection handling
    const planRadios = document.querySelectorAll('.plan-radio');
    const continueButton = document.querySelector('.continue-button');

    planRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Enable continue button when a plan is selected
            continueButton.disabled = false;
            
            // Update the continue button text based on selected plan
            const selectedCard = this.closest('.pricing-card');
            const packageName = selectedCard.querySelector('h3').textContent;
            const lang = document.documentElement.getAttribute('lang');
            
            const buttonTexts = {
                en: `Continue with ${packageName}`,
                zh: `继续${packageName}`,
                ja: `${packageName}で続ける`
            };
            
            continueButton.setAttribute('data-en', buttonTexts.en);
            continueButton.setAttribute('data-zh', buttonTexts.zh);
            continueButton.setAttribute('data-ja', buttonTexts.ja);
            continueButton.textContent = buttonTexts[lang];
        });
    });

    // Continue button click handler
    continueButton.addEventListener('click', function() {
        if (!this.disabled) {
            const selectedPlan = document.querySelector('.plan-radio:checked').value;
            // Scroll to contact form
            document.querySelector('#contact').scrollIntoView({ behavior: 'smooth' });
            // Pre-select the service in the contact form
            const serviceSelect = document.querySelector('#service');
            if (serviceSelect) {
                serviceSelect.value = selectedPlan;
            }
        }
    });

    // Form submission
    document.getElementById('contact-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get the selected package
        const selectedPackage = document.querySelector('input[name="pricing-plan"]:checked');
        if (!selectedPackage) {
            alert('Please select a package first');
            return;
        }

        // Get form data
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            selected_package: selectedPackage.value,
            message: document.getElementById('message').value
        };

        try {
            // Show loading state
            const submitButton = document.querySelector('.submit-button');
            submitButton.classList.add('loading');
            submitButton.disabled = true;

            // Send data to backend using Cloudflare Worker URL
            const response = await fetch('https://adcadd24-resumehub-api.xiuxiu-luo.workers.dev/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                // Success
                alert('Thank you for your submission! We will contact you soon.');
                this.reset();
                // Uncheck radio buttons
                document.querySelectorAll('input[name="pricing-plan"]').forEach(radio => radio.checked = false);
            } else {
                // Error
                alert(result.error || 'Failed to submit form. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to submit form. Please try again later.');
        } finally {
            // Remove loading state
            const submitButton = document.querySelector('.submit-button');
            submitButton.classList.remove('loading');
            submitButton.disabled = false;
        }
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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

    // Sticky header
    const header = document.querySelector('header');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll <= 0) {
            header.classList.remove('scroll-up');
            return;
        }

        if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
            header.classList.remove('scroll-up');
            header.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
            header.classList.remove('scroll-down');
            header.classList.add('scroll-up');
        }
        lastScroll = currentScroll;
    });

    // Add animation on scroll for service cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.service-card').forEach(card => {
        observer.observe(card);
    });
});

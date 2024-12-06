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

    // Form submission handling
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                service: document.getElementById('service').value,
                message: document.getElementById('message').value
            };

            // Basic form validation
            if (!formData.name || !formData.email || !formData.service || !formData.message) {
                const messages = {
                    en: 'Please fill in all required fields',
                    zh: '请填写所有必填字段',
                    ja: '必須項目をすべて入力してください'
                };
                alert(messages[document.documentElement.getAttribute('lang')]);
                return;
            }

            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(formData.email)) {
                const messages = {
                    en: 'Please enter a valid email address',
                    zh: '请输入有效的邮箱地址',
                    ja: '有効なメールアドレスを入力してください'
                };
                alert(messages[document.documentElement.getAttribute('lang')]);
                return;
            }

            // Simulate form submission
            console.log('Sending form data to info@eliteresumeau.com');
            const successMessages = {
                en: 'Thank you for your interest! We will contact you shortly.',
                zh: '感谢您的关注！我们会尽快与您联系。',
                ja: 'お問い合わせありがとうございます！近日中にご連絡させていただきます。'
            };
            alert(successMessages[document.documentElement.getAttribute('lang')]);
            contactForm.reset();

            console.log('Form submitted:', formData);
        });
    }

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

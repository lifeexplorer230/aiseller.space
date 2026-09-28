/**
 * Fade-in анимации при скролле
 * Использует Intersection Observer API
 */

class ScrollAnimations {
    constructor() {
        this.animatedElements = document.querySelectorAll('[data-animate]');
        this.observerOptions = {
            threshold: 0.15, // Триггер когда 15% элемента видимо
            rootMargin: '0px 0px -50px 0px' // Небольшой отступ снизу
        };

        this.init();
    }

    init() {
        // Fallback для старых браузеров
        if (!('IntersectionObserver' in window)) {
            this.animatedElements.forEach(el => {
                el.classList.add('is-visible');
            });
            return;
        }

        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            this.observerOptions
        );

        this.animatedElements.forEach(el => {
            this.observer.observe(el);
        });
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Опционально: перестать наблюдать после анимации
                // this.observer.unobserve(entry.target);
            }
        });
    }
}

/**
 * Smooth scroll для якорных ссылок
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');

            if (targetId === '#' || targetId === '#!') return;

            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    new ScrollAnimations();
    initSmoothScroll();
});

/**
 * FAQ Accordion
 * Управляет раскрытием/закрытием ответов в FAQ секции
 */

class FAQAccordion {
    constructor() {
        this.faqItems = document.querySelectorAll('.faq-item');
        this.init();
    }

    init() {
        if (!this.faqItems.length) return;

        this.faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            if (question) {
                question.addEventListener('click', () => this.toggle(item));
            }
        });
    }

    toggle(item) {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = item.querySelector('.faq-icon');
        const isOpen = item.classList.contains('is-open');

        if (isOpen) {
            // Закрываем
            item.classList.remove('is-open');
            question.setAttribute('aria-expanded', 'false');
            answer.style.maxHeight = '0';
            icon.textContent = '+';
        } else {
            // Открываем
            item.classList.add('is-open');
            question.setAttribute('aria-expanded', 'true');
            answer.style.maxHeight = answer.scrollHeight + 'px';
            icon.textContent = '−';
        }
    }

    closeAll() {
        this.faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');
            const icon = item.querySelector('.faq-icon');

            item.classList.remove('is-open');
            question.setAttribute('aria-expanded', 'false');
            answer.style.maxHeight = '0';
            icon.textContent = '+';
        });
    }

    openAll() {
        this.faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');
            const icon = item.querySelector('.faq-icon');

            item.classList.add('is-open');
            question.setAttribute('aria-expanded', 'true');
            answer.style.maxHeight = answer.scrollHeight + 'px';
            icon.textContent = '−';
        });
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    new FAQAccordion();
});

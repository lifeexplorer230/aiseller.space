/**
 * Mobile Menu
 * Управление открытием/закрытием мобильного меню
 */

class MobileMenu {
    constructor() {
        this.menuToggle = document.querySelector('.menu-burger');
        this.nav = document.querySelector('.nav');
        this.navLinks = document.querySelectorAll('.nav__link');
        this.isOpen = false;

        this.init();
    }

    init() {
        if (!this.menuToggle || !this.nav) return;

        // Клик по кнопке меню
        this.menuToggle.addEventListener('click', () => this.toggle());

        // Клик по ссылкам - закрыть меню
        this.navLinks.forEach(link => {
            link.addEventListener('click', () => this.close());
        });

        // Клик вне меню - закрыть
        document.addEventListener('click', (e) => {
            if (this.isOpen &&
                !this.nav.contains(e.target) &&
                !this.menuToggle.contains(e.target)) {
                this.close();
            }
        });

        // ESC - закрыть меню
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    toggle() {
        this.isOpen ? this.close() : this.open();
    }

    open() {
        this.nav.classList.add('is-open');
        this.menuToggle.classList.add('is-active');
        this.menuToggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
        this.isOpen = true;
    }

    close() {
        this.nav.classList.remove('is-open');
        this.menuToggle.classList.remove('is-active');
        this.menuToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        this.isOpen = false;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    new MobileMenu();
});

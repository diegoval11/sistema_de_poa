/**
 * Theme Toggle Script con Accesibilidad Mejorada
 * Alcaldía POA - Sistema de Gestión
 */

(function () {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    if (!themeToggle) return;

    // Cargar tema guardado o usar el predeterminado
    const savedTheme = localStorage.getItem('theme') || 'light';

    /**
     * Actualiza el estado del tema en el DOM y los atributos de accesibilidad
     */
    function updateThemeState(theme) {
        htmlElement.setAttribute('data-theme', theme);

        const isDark = theme === 'dark';
        if (isDark) {
            htmlElement.classList.add('dark');
        } else {
            htmlElement.classList.remove('dark');
        }

        themeToggle.setAttribute('aria-pressed', isDark);

        const tooltipText = isDark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
        themeToggle.setAttribute('data-tooltip', tooltipText);
        themeToggle.setAttribute('aria-label', tooltipText);
    }

    /**
     * Cambia el tema con animación y actualiza el estado
     */
    function toggleTheme() {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        themeToggle.classList.add('theme-changing');

        updateThemeState(newTheme);
        localStorage.setItem('theme', newTheme);

        setTimeout(() => {
            themeToggle.classList.remove('theme-changing');
        }, 600);
    }

    updateThemeState(savedTheme);

    themeToggle.addEventListener('click', toggleTheme);

    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
            e.preventDefault();
            toggleTheme();
        }
    });

    console.log('%c🌓 Tema Mejorado para Alcaldía POA', 'font-size: 16px; font-weight: bold; color: #006AD8;');
    console.log('%cUsa Ctrl+Shift+D (o Cmd+Shift+D en Mac) para cambiar el tema rápidamente.', 'color: #666;');
})();

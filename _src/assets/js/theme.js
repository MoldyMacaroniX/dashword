const htmlElement = document.documentElement;
const themeMedia = window.matchMedia('(prefers-color-scheme: dark)');

// Core function to update the DOM classes
function applyTheme(theme) {

    document.body.classList.add('preload');

    // Remove existing explicit target classes if your CSS treats light/dark differently
    htmlElement.classList.remove('dark', 'light', 'system');
    
    // Set data attribute for style hook scoping
    htmlElement.setAttribute('data-theme', theme);

    if (theme === 'dark') {
        htmlElement.classList.add('dark');
    } else if (theme === 'light') {
        htmlElement.classList.add('light');
    } else if (theme === 'system') {
        htmlElement.classList.add('system');
        // Check actual system settings
        if (themeMedia.matches) {
            htmlElement.classList.add('dark');
        }
    }

    setTimeout(() => {
        document.body.classList.remove('preload');
    }, 250);
}

// Function triggered when user clicks a theme switcher button
function setTheme(newTheme) {
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
}

// Listen for system theme changes dynamically
themeMedia.addEventListener('change', () => {
    const savedTheme = localStorage.getItem('theme') || 'system';
    if (savedTheme === 'system') {
        applyTheme('system');
    }
});

// Initialize on page load to sync UI controls (like select dropdowns or active classes)
document.addEventListener('DOMContentLoaded', () => {
    const currentTheme = localStorage.getItem('theme') || 'system';
    applyTheme(currentTheme);
    
    // Example: If you have a dropdown select element with id "themeSelector"
    const selector = document.getElementById('themeSelector');
    if (selector) {
        selector.value = currentTheme;
        selector.addEventListener('change', (e) => setTheme(e.target.value));
    }
});
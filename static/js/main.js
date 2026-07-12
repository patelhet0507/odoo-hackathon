document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;

    if (localStorage.getItem('theme') === 'dark') {
        html.setAttribute('data-bs-theme', 'dark');
        toggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
    }

    toggle.addEventListener('click', function() {
        const current = html.getAttribute('data-bs-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        toggle.innerHTML = next === 'dark' ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
    });
});

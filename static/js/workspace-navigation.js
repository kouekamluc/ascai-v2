document.querySelectorAll('[data-nav-search]').forEach((container) => {
    const input = container.querySelector('input[type="search"]');
    const nav = container.querySelector('nav');
    const empty = container.querySelector('[data-nav-empty]');
    if (!input || !nav) return;
    const normalize = (value) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
    input.addEventListener('input', () => {
        const query = normalize(input.value.trim());
        let count = 0;
        nav.querySelectorAll('a').forEach((link) => {
            link.hidden = !normalize(link.textContent).includes(query);
            if (!link.hidden) count++;
        });
        Array.from(nav.children).forEach((group) => {
            group.hidden = !Array.from(group.querySelectorAll('a')).some((link) => !link.hidden);
        });
        empty.hidden = count > 0;
    });
    input.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') { input.value = ''; input.dispatchEvent(new Event('input')); }
    });
    nav.querySelectorAll('a').forEach((link) => {
        if (new URL(link.href).pathname === window.location.pathname) link.setAttribute('aria-current', 'page');
    });
});

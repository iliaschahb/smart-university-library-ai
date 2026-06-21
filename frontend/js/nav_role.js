async function buildDynamicNavbar() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navHost = document.getElementById('dynamicNavbarHost');
    if (!navHost) return;

    let role = null;
    let authenticated = false;

    try {
        const me = await getCurrentUser();
        role = me.role;
        authenticated = !!me.authenticated;
    } catch (error) {
        console.error('Erreur menu dynamique:', error);
    }

    const isAdmin = authenticated && role === 'admin';
    const isAppUser = authenticated && ['admin', 'librarian'].includes(role);

    const sharedLinks = [
        { href: 'index.html', label: 'Accueil', icon: 'bi-house-door-fill' },
        { href: 'librarian_dashboard.html', label: 'Bibliothèque', icon: 'bi-speedometer2' },
        { href: 'dashboard.html', label: 'Tableau de bord', icon: 'bi-bar-chart-line-fill' },
        { href: 'books.html', label: 'Livres', icon: 'bi-book-fill' },
        { href: 'students.html', label: 'Étudiants', icon: 'bi-people-fill' },
        { href: 'loans.html', label: 'Emprunts', icon: 'bi-journal-check' },
        { href: 'bigdata.html', label: 'Analyses', icon: 'bi-graph-up-arrow' },
        { href: 'ml_hybrid.html', label: 'Prévisions', icon: 'bi-cpu-fill' },
        { href: 'recommendations.html', label: 'Suggestions', icon: 'bi-stars' },
    ];

    const adminLinks = [
        { href: 'admin_panel.html', label: 'Administration', icon: 'bi-person-gear' },
        { href: 'visualizations.html', label: 'Graphiques', icon: 'bi-pie-chart-fill' },
        { href: 'catalog_relational.html', label: 'Catalogue avancé', icon: 'bi-collection-fill' },
    ];

    let links = [];
    if (isAdmin) {
        links = [sharedLinks[0], adminLinks[0], ...sharedLinks.slice(1), adminLinks[1], adminLinks[2]];
    } else if (isAppUser) {
        links = sharedLinks;
    } else {
        links = [{ href: 'login.html', label: 'Connexion', icon: 'bi-box-arrow-in-right' }];
    }

    const linkHtml = links.map(link => `
        <a class="side-nav-link ${currentPage === link.href ? 'active' : ''}" href="${link.href}" title="${link.label}">
            <i class="bi ${link.icon}"></i>
            <span>${link.label}</span>
        </a>
    `).join('');

    navHost.innerHTML = `
        <aside class="side-shell" id="sideShell">
            <div class="side-rail">
                <button class="side-toggle" id="sideToggle" type="button" title="Ouvrir le menu" aria-label="Ouvrir le menu">
                    <i class="bi bi-list"></i>
                </button>
                ${links.slice(0, 7).map(link => `
                    <a class="rail-link ${currentPage === link.href ? 'active' : ''}" href="${link.href}" title="${link.label}">
                        <i class="bi ${link.icon}"></i>
                    </a>
                `).join('')}
            </div>

            <div class="side-panel" id="sidePanel">
                <div class="side-brand">
                    <div class="side-logo"><i class="bi bi-book-half"></i></div>
                    <div>
                        <div class="side-title">Smart Library AI</div>
                        <div class="side-role">${isAdmin ? 'Administration' : isAppUser ? 'Bibliothèque' : 'Connexion'}</div>
                    </div>
                </div>

                <nav class="side-links">
                    ${linkHtml}
                </nav>

                ${authenticated ? `
                    <button class="side-logout" onclick="logoutUser()">
                        <i class="bi bi-box-arrow-right"></i>
                        <span>Déconnexion</span>
                    </button>
                ` : ''}
            </div>
        </aside>
        <div class="side-backdrop" id="sideBackdrop"></div>
    `;

    const sideShell = document.getElementById('sideShell');
    const sideToggle = document.getElementById('sideToggle');
    const sideBackdrop = document.getElementById('sideBackdrop');

    function openMenu() {
        document.body.classList.add('sidebar-open');
        sideShell.classList.add('open');
    }

    function closeMenu() {
        document.body.classList.remove('sidebar-open');
        sideShell.classList.remove('open');
    }

    sideToggle.addEventListener('click', () => {
        if (sideShell.classList.contains('open')) closeMenu();
        else openMenu();
    });

    sideBackdrop.addEventListener('click', closeMenu);

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') closeMenu();
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildDynamicNavbar);
} else {
    buildDynamicNavbar();
}

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
        console.error('Erreur navbar dynamique:', error);
    }

    const isAdmin = authenticated && role === 'admin';
    const isAppUser = authenticated && ['admin', 'librarian'].includes(role);

    const sharedLinks = [
        { href: 'index.html', label: 'Accueil' },
        { href: 'librarian_dashboard.html', label: 'Bibliothèque' },
        { href: 'dashboard.html', label: 'Tableau de bord' },
        { href: 'books.html', label: 'Livres' },
        { href: 'students.html', label: 'Étudiants' },
        { href: 'loans.html', label: 'Emprunts' },
        { href: 'bigdata.html', label: 'Analyses' },
        { href: 'ml_hybrid.html', label: 'Prévisions' },
        { href: 'recommendations.html', label: 'Suggestions' },
    ];

    const adminLinks = [
        { href: 'admin_panel.html', label: 'Administration' },
        { href: 'visualizations.html', label: 'Graphiques' },
        { href: 'catalog_relational.html', label: 'Catalogue avancé' },
    ];

    let links = [];
    if (isAdmin) {
        links = [sharedLinks[0], adminLinks[0], ...sharedLinks.slice(1), adminLinks[1], adminLinks[2]];
    } else if (isAppUser) {
        links = sharedLinks;
    } else {
        links = [{ href: 'login.html', label: 'Connexion' }];
    }

    navHost.innerHTML = `
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid px-4">
                <a class="navbar-brand" href="${authenticated ? 'index.html' : 'login.html'}">Smart Library AI</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#dynamicNavbar" aria-controls="dynamicNavbar" aria-expanded="false" aria-label="Navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="dynamicNavbar">
                    <div class="navbar-nav ms-auto align-items-lg-center gap-lg-1">
                        ${links.map(link => `<a class="nav-link ${currentPage === link.href ? 'active' : ''}" href="${link.href}">${link.label}</a>`).join('')}
                        ${authenticated ? `<button class="btn btn-sm btn-outline-light ms-lg-2 mt-2 mt-lg-0" onclick="logoutUser()">Déconnexion</button>` : ''}
                    </div>
                </div>
            </div>
        </nav>
    `;
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildDynamicNavbar);
} else {
    buildDynamicNavbar();
}

async function requireAdmin() {
    try {
        const me = await apiGet('/auth/me');
        if (!me.authenticated || !me.is_admin) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    } catch (error) {
        console.error(error);
        window.location.href = 'login.html';
        return false;
    }
}

function renderKeyValueTable(obj) {
    return `
        <table class="table table-sm table-bordered table-striped">
            <tbody>
                ${Object.entries(obj).map(([k, v]) => `
                    <tr>
                        <th style="width: 40%">${k}</th>
                        <td>${v}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function loadAdminHealth() {
    const c = document.getElementById('adminHealthContainer');
    try {
        const data = await apiGet('/admin/health');
        c.innerHTML = renderKeyValueTable(data);
    } catch (error) {
        c.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function loadAdminUsers() {
    const c = document.getElementById('adminUsersContainer');
    try {
        const items = await apiGet('/admin/users');
        c.innerHTML = `
            <table class="table table-bordered table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Nom complet</th>
                        <th>Rôle</th>
                        <th>Actif</th>
                        <th>Dernière connexion</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(item => `
                        <tr>
                            <td>${item.id}</td>
                            <td>${item.username}</td>
                            <td>${item.full_name}</td>
                            <td><span class="badge ${item.role === 'admin' ? 'bg-danger' : 'bg-primary'}">${item.role}</span></td>
                            <td>${item.is_active ? 'Oui' : 'Non'}</td>
                            <td>${item.last_login_at || ''}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        c.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

(async function initAdminPanel() {
    const ok = await requireAdmin();
    if (!ok) return;
    await loadAdminHealth();
    await loadAdminUsers();
})();

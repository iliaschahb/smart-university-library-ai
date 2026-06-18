async function getCurrentUser() {
    return await apiGet('/auth/me');
}

async function requireAdminPage() {
    try {
        const me = await getCurrentUser();
        if (!me.authenticated || me.role !== 'admin') {
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

async function loginAdmin() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const message = document.getElementById('authMessage');
    message.innerHTML = '<span class="small-muted">Connexion en cours...</span>';
    try {
        const data = await apiPost('/auth/login', { username, password });
        if (data.user.role !== 'admin') {
            await apiPost('/auth/logout', {});
            message.innerHTML = '<span class="text-danger">Accès refusé : rôle admin requis.</span>';
            return;
        }
        message.innerHTML = '<span class="text-success">Connexion admin réussie. Redirection...</span>';
        setTimeout(() => { window.location.href = 'index.html'; }, 600);
    } catch (error) {
        message.innerHTML = `<span class="text-danger">${error.message}</span>`;
    }
}

async function logoutUser() {
    try { await apiPost('/auth/logout', {}); } catch (error) { console.error(error); }
    window.location.href = 'login.html';
}

async function getCurrentUser() {
    return await apiGet('/auth/me');
}

async function loginUser() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const message = document.getElementById('authMessage');

    message.innerHTML = '<span class="small-muted">Connexion en cours...</span>';

    try {
        const data = await apiPost('/auth/login', { username, password });
        const role = data.user.role;

        message.innerHTML = '<span class="text-success">Connexion réussie. Redirection...</span>';

        setTimeout(() => {
            if (role === 'admin') {
                window.location.href = 'index.html';
            } else if (role === 'librarian') {
                window.location.href = 'librarian_dashboard.html';
            } else {
                window.location.href = 'login.html';
            }
        }, 500);
    } catch (error) {
        message.innerHTML = `<span class="text-danger">${error.message}</span>`;
    }
}

async function logoutUser() {
    try {
        await apiPost('/auth/logout', {});
    } catch (error) {
        console.error(error);
    }
    window.location.href = 'login.html';
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

async function requireAppUserPage() {
    try {
        const me = await getCurrentUser();
        if (!me.authenticated || !['admin', 'librarian'].includes(me.role)) {
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

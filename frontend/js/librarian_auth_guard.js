async function requireLibrarianAuth() {
    try {
        const data = await apiGet('/auth/me');

        if (!data.authenticated) {
            window.location.href = 'login.html';
            return;
        }

        // autoriser librarian et admin
        if (!['librarian', 'admin'].includes(data.role)) {
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error(error);
        window.location.href = 'login.html';
    }
}

requireLibrarianAuth();
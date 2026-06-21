function renderKeyValueTable(obj) {
    return `
        <table class="table table-sm table-bordered table-striped">
            <tbody>
                ${Object.entries(obj).map(([k, v]) => `
                    <tr>
                        <th style="width:35%">${k}</th>
                        <td>${Array.isArray(v) ? v.join(", ") : v}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

async function loadAdminHealth() {
    const container = document.getElementById("adminHealthContainer");

    try {
        const data = await apiGet("/admin/health");
        container.innerHTML = renderKeyValueTable(data);
    } catch (error) {
        console.error("Erreur /admin/health :", error);
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function loadAdminUsers() {
    const container = document.getElementById("adminUsersContainer");

    try {
        const items = await apiGet("/admin/users");

        if (!items || !items.length) {
            container.innerHTML = "<p>Aucun utilisateur.</p>";
            return;
        }

        container.innerHTML = `
            <table class="table table-bordered table-striped align-middle">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Nom complet</th>
                        <th>Rôle</th>
                        <th>Actif</th>
                        <th>Dernière connexion</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(item => `
                        <tr>
                            <td>${item.id}</td>
                            <td>${escapeHtml(item.username)}</td>
                            <td>${escapeHtml(item.full_name)}</td>
                            <td>
                                <span class="badge ${item.role === "admin" ? "bg-danger" : "bg-primary"}">
                                    ${escapeHtml(item.role)}
                                </span>
                            </td>
                            <td>${item.is_active ? "Oui" : "Non"}</td>
                            <td>${item.last_login_at || ""}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-warning me-1"
                                        onclick="toggleUser(${item.id})">
                                    ${item.is_active ? "Désactiver" : "Activer"}
                                </button>
                                <button class="btn btn-sm btn-outline-danger"
                                        onclick='deleteUser(${item.id}, ${JSON.stringify(item.username)})'>
                                    Supprimer
                                </button>
                            </td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error("Erreur /admin/users :", error);
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function createUser() {
    const message = document.getElementById("createUserMessage");

    const payload = {
        username: document.getElementById("newUsername").value.trim(),
        full_name: document.getElementById("newFullName").value.trim(),
        password: document.getElementById("newPassword").value,
        role: document.getElementById("newRole").value,
    };

    message.innerHTML = '<span class="small-muted">Création...</span>';

    try {
        await apiPost("/admin/users", payload);

        message.innerHTML = '<span class="text-success">Utilisateur créé.</span>';

        document.getElementById("newUsername").value = "";
        document.getElementById("newFullName").value = "";
        document.getElementById("newPassword").value = "";
        document.getElementById("newRole").value = "librarian";

        await loadAdminUsers();
    } catch (error) {
        console.error("Erreur création user :", error);
        message.innerHTML = `<span class="text-danger">${error.message}</span>`;
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Supprimer l'utilisateur ${username} ?`)) {
        return;
    }

    try {
        await apiDelete(`/admin/users/${userId}`);
        await loadAdminUsers();
    } catch (error) {
        console.error("Erreur suppression user :", error);
        alert(error.message);
    }
}

async function toggleUser(userId) {
    try {
        await apiPost(`/admin/users/${userId}/toggle-active`, {});
        await loadAdminUsers();
    } catch (error) {
        console.error("Erreur toggle user :", error);
        alert(error.message);
    }
}

(async function initAdminPanel() {
    const ok = await requireAdminPage();
    if (!ok) return;

    await loadAdminHealth();
    await loadAdminUsers();
})();

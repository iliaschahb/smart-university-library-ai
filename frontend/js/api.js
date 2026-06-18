function getApiBaseUrl() {
    const host = window.location.hostname;
    if (host.includes('.app.github.dev')) {
        return `${window.location.protocol}//${host.replace('-5500.', '-5000.')}`;
    }
    return 'http://localhost:5000';
}

const API_BASE_URL = getApiBaseUrl();

async function parseJsonResponse(response) {
    const text = await response.text();
    try { return text ? JSON.parse(text) : {}; }
    catch (_) { return { error: text || 'Réponse non JSON du serveur' }; }
}

async function apiGet(endpoint) {
    let response;
    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'GET',
            credentials: 'include'
        });
    } catch (error) {
        throw new Error(`Impossible de joindre le backend Flask (${API_BASE_URL}). Vérifie que le port 5000 est lancé et exposé dans Codespaces.`);
    }
    const data = await parseJsonResponse(response);
    if (response.status === 401 && window.location.pathname.split('/').pop() !== 'login.html') {
        window.location.href = 'login.html';
        throw new Error('Authentification requise.');
    }
    if (!response.ok) throw new Error(data.error || data.message || 'Erreur API');
    return data;
}

async function apiPost(endpoint, payload = {}) {
    let response;
    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (error) {
        throw new Error(`Impossible de joindre le backend Flask (${API_BASE_URL}). Vérifie que le port 5000 est lancé et exposé dans Codespaces.`);
    }
    const data = await parseJsonResponse(response);
    if (!response.ok) throw new Error(data.error || data.message || 'Erreur API');
    return data;
}

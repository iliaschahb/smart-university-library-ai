function getApiBaseUrl() {
    const host = window.location.hostname;

    // GitHub Codespaces : frontend 5500 -> backend 5000
    if (host.includes('.app.github.dev')) {
        return `${window.location.protocol}//${host.replace('-5500.', '-5000.')}`;
    }

    // En local classique
    return 'http://localhost:5000';
}

const API_BASE_URL = getApiBaseUrl();

async function parseJsonResponse(response) {
    const text = await response.text();
    try {
        return text ? JSON.parse(text) : {};
    } catch (_) {
        return { error: text || 'Réponse non JSON du serveur' };
    }
}

async function apiGet(endpoint) {
    let response;
    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'GET',
            credentials: 'include'
        });
    } catch (error) {
        throw new Error(`Impossible de joindre le serveur (${API_BASE_URL}). Vérifie que le backend est lancé.`);
    }

    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data.error || data.message || 'Erreur API');
    }
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
        throw new Error(`Impossible de joindre le serveur (${API_BASE_URL}). Vérifie que le backend est lancé.`);
    }

    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data.error || data.message || 'Erreur API');
    }
    return data;
}

async function apiDelete(endpoint) {
    let response;
    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'DELETE',
            credentials: 'include'
        });
    } catch (error) {
        throw new Error(`Impossible de joindre le serveur (${API_BASE_URL}). Vérifie que le backend est lancé.`);
    }

    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data.error || data.message || 'Erreur API');
    }
    return data;
}

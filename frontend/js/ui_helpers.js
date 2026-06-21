function formatStatus(status) {
    const value = String(status || '').toUpperCase();
    const map = {
        BORROWED: 'En cours',
        RETURNED: 'Retourné',
        LATE: 'En retard',
        ACTIVE: 'Actif',
        INACTIVE: 'Inactif'
    };
    return map[value] || status || '-';
}

function statusBadge(status) {
    const value = String(status || '').toUpperCase();
    let cls = 'badge-neutral';
    if (value === 'BORROWED') cls = 'badge-borrowed';
    if (value === 'RETURNED') cls = 'badge-returned';
    if (value === 'LATE') cls = 'badge-late';
    return `<span class="badge-status ${cls}">${formatStatus(status)}</span>`;
}

function escapeHtmlSafe(text) {
    return String(text ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function escapeHtml(text) {
    return String(text ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function selectBookForStock(bookId) {
    document.getElementById('stockBookId').value = bookId;
    document.getElementById('stockBookId').focus();
}

async function loadBooksActions() {
    const c = document.getElementById('booksActionsContainer');
    const search = document.getElementById('searchInput').value.trim();
    c.innerHTML = '<div class="loading-text">Chargement...</div>';

    try {
        const endpoint = `/catalog/books?page_size=30${search ? `&search=${encodeURIComponent(search)}` : ''}`;
        const data = await apiGet(endpoint);
        const items = Array.isArray(data) ? data : (data.items || data.books || []);

        if (!items.length) {
            c.innerHTML = '<p>Aucun livre trouvé.</p>';
            return;
        }

        c.innerHTML = `
            <table class="table table-bordered table-striped align-middle">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Titre</th>
                        <th>Auteur</th>
                        <th>Note</th>
                        <th>Stock</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(item => `
                        <tr>
                            <td>${escapeHtml(item.book_id)}</td>
                            <td>${escapeHtml(item.title)}</td>
                            <td>${escapeHtml(item.authors || item.author || '')}</td>
                            <td>${escapeHtml(item.average_rating || '')}</td>
                            <td>${escapeHtml(item.available_quantity ?? item.inventory_available ?? '')}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="selectBookForStock(${item.book_id})">Gérer</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        c.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function updateStockFromForm() {
    const msg = document.getElementById('stockMessage');
    const bookId = Number(document.getElementById('stockBookId').value);
    const quantity = Number(document.getElementById('stockQuantity').value);
    const shelf = document.getElementById('stockShelf').value.trim();

    if (!bookId || Number.isNaN(quantity)) {
        msg.innerHTML = '<span class="text-danger">ID livre et quantité sont obligatoires.</span>';
        return;
    }

    msg.innerHTML = '<span class="small-muted">Mise à jour...</span>';
    try {
        const data = await apiPost(`/inventory/${bookId}/update`, {
            quantity,
            shelf_location: shelf,
        });
        msg.innerHTML = `<span class="text-success">${data.message}</span>`;
        await loadBooksActions();
    } catch (error) {
        msg.innerHTML = `<span class="text-danger">${error.message}</span>`;
    }
}

async function predictBookFromForm() {
    const msg = document.getElementById('stockMessage');
    const bookId = Number(document.getElementById('stockBookId').value);
    if (!bookId) {
        msg.innerHTML = '<span class="text-danger">Choisis d’abord un ID livre.</span>';
        return;
    }

    msg.innerHTML = '<span class="small-muted">Calcul de la prévision...</span>';
    try {
        const data = await apiGet(`/ml/hybrid/predict/${bookId}`);
        msg.innerHTML = `
            <div class="alert alert-info mt-3">
                <strong>${escapeHtml(data.title)}</strong><br>
                Score prévu : <strong>${Number(data.predicted_demand_score).toFixed(2)}</strong>
            </div>
        `;
    } catch (error) {
        msg.innerHTML = `<span class="text-danger">${error.message}</span>`;
    }
}

(async function initBooksActions() {
    const ok = await requireAppUserPage();
    if (!ok) return;
    await loadBooksActions();
})();

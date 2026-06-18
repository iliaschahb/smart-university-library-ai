function renderCatalog(items) {
    const container = document.getElementById("catalogContainer");
    if (!items || !items.length) {
        container.innerHTML = "<p>Aucun livre trouvé.</p>";
        return;
    }

    container.innerHTML = `
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Titre</th>
                    <th>Auteur(s)</th>
                    <th>Popularité</th>
                    <th>Stock</th>
                    <th>Emprunts locaux</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.book_id}</td>
                        <td>${item.title}</td>
                        <td>${item.authors || ""}</td>
                        <td>${item.global_popularity_level} (${Math.round(item.global_popularity_score)})</td>
                        <td>${item.available_quantity}/${item.quantity}</td>
                        <td>${item.local_loan_count}</td>
                        <td><button class="btn btn-sm btn-outline-primary" onclick="showBook(${item.book_id})">Détails</button></td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

function renderBookDetail(book) {
    const c = document.getElementById("detailContainer");
    c.innerHTML = `
        <h5>${book.title}</h5>
        <p><strong>Auteur(s):</strong> ${book.authors || ""}</p>
        <p><strong>Année:</strong> ${book.publication_year || ""}</p>
        <p><strong>Note moyenne:</strong> ${book.average_rating || 0}</p>
        <p><strong>Niveau de popularité:</strong> ${book.global_popularity_level}</p>
        <p><strong>Top tags:</strong> ${(book.top_tags || []).join(", ")}</p>
        <p><strong>Stock local:</strong> ${book.available_quantity}/${book.quantity}</p>
        <p><strong>Emprunts locaux:</strong> ${book.local_loan_count}</p>
        <p><strong>Retards locaux:</strong> ${book.local_late_count}</p>
        <p><strong>Stock recommandé:</strong> ${book.recommended_stock}</p>
    `;
}

async function loadCatalog() {
    const search = document.getElementById("searchInput").value.trim();
    const endpoint = search ? `/catalog/books?search=${encodeURIComponent(search)}` : "/catalog/books";
    try {
        const data = await apiGet(endpoint);
        renderCatalog(data.items || []);
    } catch (error) {
        alert("Erreur catalogue : " + error.message);
    }
}

async function showBook(bookId) {
    try {
        const book = await apiGet(`/catalog/books/${bookId}`);
        renderBookDetail(book);
    } catch (error) {
        alert("Erreur détail livre : " + error.message);
    }
}

async function loadStockAlerts() {
    try {
        const items = await apiGet("/catalog/stock-alerts");
        renderCatalog(items || []);
        document.getElementById("detailContainer").innerHTML = "<p>Mode alerte de stock affiché.</p>";
    } catch (error) {
        alert("Erreur alertes : " + error.message);
    }
}

loadCatalog();

function renderBooks(items) {
    const c = document.getElementById('booksContainer');

    if (!items || !items.length) {
        c.innerHTML = '<p>Aucun livre trouvé.</p>';
        return;
    }

    c.innerHTML = `
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Titre</th>
                    <th>Auteur(s)</th>
                    <th>Popularité</th>
                    <th>Stock</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.book_id}</td>
                        <td>${item.title}</td>
                        <td>${item.authors || ''}</td>
                        <td>${item.global_popularity_level} (${Math.round(item.global_popularity_score)})</td>
                        <td>${item.available_quantity}/${item.quantity}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="showBook(${item.book_id})">
                                Détails
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderBookDetail(book) {
    const c = document.getElementById('bookDetailContainer');

    c.innerHTML = `
        <h5>${book.title}</h5>
        <p><strong>Auteur(s):</strong> ${book.authors || ''}</p>
        <p><strong>Année:</strong> ${book.publication_year || ''}</p>
        <p><strong>Langue:</strong> ${book.language_code || ''}</p>
        <p><strong>Note moyenne:</strong> ${book.average_rating}</p>
        <p><strong>Popularité globale:</strong> ${book.global_popularity_level} (${Math.round(book.global_popularity_score)})</p>
        <p><strong>Top tags:</strong> ${(book.top_tags || []).join(', ')}</p>
        <p><strong>Stock local:</strong> ${book.available_quantity}/${book.quantity}</p>
        <p><strong>Emprunts locaux:</strong> ${book.local_loan_count}</p>
        <p><strong>Retards locaux:</strong> ${book.local_late_count}</p>
        <p><strong>Stock recommandé:</strong> ${book.recommended_stock}</p>
    `;
}

async function loadBooks() {
    const search = document.getElementById('searchInput').value.trim();
    const endpoint = search
        ? `/catalog/books?search=${encodeURIComponent(search)}&page_size=20`
        : '/catalog/books?page_size=20';

    try {
        const data = await apiGet(endpoint);
        renderBooks(data.items || []);
    } catch (error) {
        console.error(error);
        alert('Erreur livres : ' + error.message);
    }
}

async function showBook(bookId) {
    try {
        const data = await apiGet(`/catalog/books/${bookId}`);
        renderBookDetail(data);
    } catch (error) {
        console.error(error);
        alert('Erreur détails du livre : ' + error.message);
    }
}

loadBooks();

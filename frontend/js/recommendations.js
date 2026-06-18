function renderRecommendations(items, metaText = "") {
    const meta = document.getElementById("recommendationsMeta");
    const container = document.getElementById("recommendationsContainer");

    meta.textContent = metaText;

    if (!items || !items.length) {
        container.innerHTML = "<p>Aucune recommandation disponible.</p>";
        return;
    }

    container.innerHTML = `
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>Livre</th>
                    <th>Auteur(s)</th>
                    <th>Score</th>
                    <th>Popularité</th>
                    <th>Tags</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.title}</td>
                        <td>${item.authors || ""}</td>
                        <td>${item.recommendation_score ?? ""}</td>
                        <td>${item.popularity_level || ""}</td>
                        <td>${(item.tags || []).slice(0, 5).join(", ")}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

async function loadPopularRecommendations() {
    try {
        const data = await apiGet("/recommendations/popular");
        renderRecommendations(data.recommendations, `Algorithme : ${data.algorithm}`);
    } catch (error) {
        alert("Erreur : " + error.message);
    }
}

async function loadUserRecommendations() {
    try {
        const userId = document.getElementById("userId").value;
        const data = await apiGet(`/recommendations/user/${userId}`);
        renderRecommendations(
            data.recommendations,
            `Algorithme : ${data.algorithm} | Livres notés : ${data.rated_books_count ?? 0} | Livres aimés : ${data.liked_books_count ?? 0}`
        );
    } catch (error) {
        alert("Erreur : " + error.message);
    }
}

async function loadSimilarBooks() {
    try {
        const bookId = document.getElementById("bookId").value;
        const data = await apiGet(`/recommendations/similar/${bookId}`);
        renderRecommendations(data.recommendations, `Livre source : ${data.source_book.title} | Algorithme : ${data.algorithm}`);
    } catch (error) {
        alert("Erreur : " + error.message);
    }
}

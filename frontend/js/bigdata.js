async function loadBigDataSummary() {
    try {
        const data = await apiGet("/bigdata/summary");
        document.getElementById("totalBooks").textContent = data.total_books ?? 0;
        document.getElementById("totalRatings").textContent = data.total_ratings ?? 0;
        document.getElementById("totalUsers").textContent = data.total_users ?? 0;
        document.getElementById("totalToRead").textContent = data.total_to_read ?? 0;
        renderTopBooks(data.top_books || []);
        renderTopTags(data.top_tags || []);
        renderRatingDistribution(data.rating_distribution || []);
        renderPopularityLevels(data.popularity_levels || []);
    } catch (error) {
        alert("Erreur Big Data : " + error.message);
    }
}

function renderTopBooks(items) {
    const c = document.getElementById("topBooksContainer");
    if (!items.length) { c.innerHTML = "<p>Aucune donnée.</p>"; return; }
    c.innerHTML = `<table class="table table-striped"><thead><tr><th>ID</th><th>Titre</th><th>Ratings</th><th>Moyenne</th></tr></thead><tbody>${items.map(x => `<tr><td>${x.book_id}</td><td>${x.title}</td><td>${x.rating_count}</td><td>${Number(x.avg_user_rating || 0).toFixed(2)}</td></tr>`).join("")}</tbody></table>`;
}

function renderTopTags(items) {
    const c = document.getElementById("topTagsContainer");
    if (!items.length) { c.innerHTML = "<p>Aucune donnée.</p>"; return; }
    c.innerHTML = `<table class="table table-striped"><thead><tr><th>Tag</th><th>Usage</th></tr></thead><tbody>${items.map(x => `<tr><td>${x.tag_name}</td><td>${x.usage_count}</td></tr>`).join("")}</tbody></table>`;
}

function renderRatingDistribution(items) {
    const c = document.getElementById("ratingDistributionContainer");
    if (!items.length) { c.innerHTML = "<p>Aucune donnée.</p>"; return; }
    c.innerHTML = `<table class="table table-striped"><thead><tr><th>Note</th><th>Nombre</th></tr></thead><tbody>${items.map(x => `<tr><td>${x.rating}</td><td>${x.count}</td></tr>`).join("")}</tbody></table>`;
}

function renderPopularityLevels(items) {
    const c = document.getElementById("popularityLevelsContainer");
    if (!items.length) { c.innerHTML = "<p>Aucune donnée.</p>"; return; }
    c.innerHTML = `<table class="table table-striped"><thead><tr><th>Niveau</th><th>Nombre de livres</th></tr></thead><tbody>${items.map(x => `<tr><td>${x.popularity_level}</td><td>${x.count}</td></tr>`).join("")}</tbody></table>`;
}

loadBigDataSummary();

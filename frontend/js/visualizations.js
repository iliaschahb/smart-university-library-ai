const chartTitles = {
    "rating_distribution.png": "Distribution des notes",
    "popularity_levels.png": "Niveaux de popularité",
    "top_books.png": "Top livres",
    "top_tags.png": "Top tags",
    "user_activity.png": "Activité utilisateurs",
    "feature_importance.png": "Importance des variables IA",
    "confusion_matrix.png": "Matrice de confusion",
    "correlation_matrix.png": "Matrice de corrélation"
};

async function loadVisualizations() {
    const container = document.getElementById("chartsContainer");
    try {
        const data = await apiGet("/visualizations/list");

        if (!data.files || !data.files.length) {
            container.innerHTML = "<p>Aucune visualisation trouvée. Exécutez d'abord generate_charts.py.</p>";
            return;
        }

        container.innerHTML = data.files.map(file => `
            <div class="col-lg-6">
                <div class="table-container">
                    <h4>${chartTitles[file] || file}</h4>
                    <img src="${API_BASE_URL}/visualizations/${file}" class="img-fluid rounded" alt="${file}">
                </div>
            </div>
        `).join("");
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

loadVisualizations();

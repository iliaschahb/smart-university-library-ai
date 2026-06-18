function renderKeyValueTable(obj) {
    return `
        <table class="table table-sm table-bordered table-striped">
            <tbody>
                ${Object.entries(obj).map(([k, v]) => `
                    <tr>
                        <th style="width: 40%">${k}</th>
                        <td>${typeof v === 'number' ? Number(v).toFixed(4) : v}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function predictHybridBook() {
    const bookId = document.getElementById("bookId").value;
    const container = document.getElementById("hybridMlResult");
    container.innerHTML = "<div class='loading-text'>Chargement de la prédiction...</div>";

    try {
        const data = await apiGet(`/ml/hybrid/predict/${bookId}`);
        container.innerHTML = `
            <div class="mb-3">
                <h5>${data.title}</h5>
                <div class="small-muted">${data.authors || ""}</div>
            </div>
            <p>
                <strong>Demand score prédit :</strong>
                <span class="badge bg-primary">${Number(data.predicted_demand_score).toFixed(2)}</span>
            </p>
            <h6 class="mt-4">Variables utilisées</h6>
            ${renderKeyValueTable(data.features_used || {})}
        `;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function loadHybridMetrics() {
    const container = document.getElementById("hybridMlResult");
    container.innerHTML = "<div class='loading-text'>Chargement des métriques...</div>";

    try {
        const data = await apiGet("/ml/hybrid/metrics");
        container.innerHTML = `
            <p><strong>Modèle :</strong> ${data.model_type}</p>
            <p><strong>Nombre de lignes :</strong> ${data.dataset_rows}</p>
            <p><strong>MAE :</strong> ${Number(data.mae).toFixed(4)}</p>
            <p><strong>RMSE :</strong> ${Number(data.rmse).toFixed(4)}</p>
            <p><strong>R² :</strong> ${Number(data.r2).toFixed(4)}</p>
            <h6 class="mt-4">Importance des variables</h6>
            <table class="table table-sm table-bordered table-striped">
                <thead>
                    <tr>
                        <th>Variable</th>
                        <th>Importance</th>
                    </tr>
                </thead>
                <tbody>
                    ${(data.feature_importance || []).map(item => `
                        <tr>
                            <td>${item.feature}</td>
                            <td>${Number(item.importance).toFixed(4)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function loadHybridHealth() {
    const container = document.getElementById("hybridMlHealth");
    container.innerHTML = "<div class='loading-text'>Vérification...</div>";

    try {
        const data = await apiGet("/ml/hybrid/health");
        container.innerHTML = renderKeyValueTable(data);
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

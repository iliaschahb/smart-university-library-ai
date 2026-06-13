async function predictByBookId() {
    const bookId = document.getElementById("bookId").value;
    const container = document.getElementById("mlResult");

    try {
        const data = await apiGet(`/ml/popularity/predict/${bookId}`);
        container.innerHTML = `
            <h5>${data.title}</h5>
            <p><strong>Auteur(s):</strong> ${data.authors || ""}</p>
            <p><strong>Prédiction:</strong> <span class="badge bg-primary">${data.prediction}</span></p>
            <h6>Probabilités</h6>
            <pre>${JSON.stringify(data.probabilities, null, 2)}</pre>
            <h6>Variables utilisées</h6>
            <pre>${JSON.stringify(data.features_used, null, 2)}</pre>
        `;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function loadMetrics() {
    const container = document.getElementById("mlResult");
    try {
        const data = await apiGet("/ml/popularity/metrics");
        container.innerHTML = `
            <p><strong>Modèle:</strong> ${data.model_type}</p>
            <p><strong>Lignes dataset:</strong> ${data.dataset_rows}</p>
            <p><strong>Accuracy:</strong> ${Number(data.accuracy).toFixed(4)}</p>
            <p><strong>Balanced accuracy:</strong> ${Number(data.balanced_accuracy).toFixed(4)}</p>
            <h6>Distribution des classes</h6>
            <pre>${JSON.stringify(data.class_distribution, null, 2)}</pre>
            <h6>Importance des variables</h6>
            <pre>${JSON.stringify(data.feature_importance, null, 2)}</pre>
        `;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

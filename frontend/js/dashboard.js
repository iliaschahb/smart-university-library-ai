function kpiCard(title, value, subtitle = '') {
    return `
        <div class="col-md-6 col-lg-3">
            <div class="card card-stat h-100">
                <div class="card-body">
                    <div class="text-muted">${title}</div>
                    <div class="stat-value">${value}</div>
                    ${subtitle ? `<div class="small-muted">${subtitle}</div>` : ''}
                </div>
            </div>
        </div>`;
}

function renderSimpleTable(containerId, columns, rows) {
    const c = document.getElementById(containerId);
    if (!rows || !rows.length) {
        c.innerHTML = '<p>Aucune donnée.</p>';
        return;
    }

    c.innerHTML = `
        <table class="table table-striped table-bordered">
            <thead>
                <tr>${columns.map(x => `<th>${x.label}</th>`).join('')}</tr>
            </thead>
            <tbody>
                ${rows.map(row => `
                    <tr>
                        ${columns.map(col => `<td>${row[col.key] ?? ''}</td>`).join('')}
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function loadDashboardSummary() {
    try {
        const data = await apiGet('/dashboard/summary');

        document.getElementById('dashboardKpis').innerHTML = `
            ${kpiCard('Catalogue Kaggle', data.catalog_books)}
            ${kpiCard('Titres stockés', data.stocked_titles)}
            ${kpiCard('Exemplaires', data.total_copies, `${data.available_copies} disponibles`)}
            ${kpiCard('Étudiants', data.students, `${data.active_loans} emprunts actifs`)}
        `;

        renderSimpleTable(
            'topBorrowedContainer',
            [
                { key: 'title', label: 'Titre' },
                { key: 'loan_count', label: 'Emprunts' }
            ],
            data.top_borrowed || []
        );

        renderSimpleTable(
            'topPopularContainer',
            [
                { key: 'title', label: 'Titre' },
                { key: 'global_popularity_level', label: 'Niveau' },
                { key: 'global_popularity_score', label: 'Score' }
            ],
            (data.top_popular || []).map(x => ({
                ...x,
                global_popularity_score: Math.round(x.global_popularity_score)
            }))
        );
    } catch (error) {
        console.error(error);
        alert('Erreur dashboard : ' + error.message);
    }
}

loadDashboardSummary();

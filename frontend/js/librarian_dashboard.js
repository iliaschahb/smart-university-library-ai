let availabilityChart = null;
let loansStatusChart = null;
let booksByCategoryChart = null;
let topBorrowedBooksChart = null;
let refreshTimer = null;
let kpiMiniCharts = [];

function destroyChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

function destroyMiniCharts() {
    kpiMiniCharts.forEach(chart => chart.destroy());
    kpiMiniCharts = [];
}

function formatDateTime() {
    const now = new Date();
    return now.toLocaleString("fr-FR");
}

function kpiCard(id, title, value, subtitle = "", type = "line") {
    return `
        <div class="col-md-6 col-lg-3">
            <div class="card card-stat kpi-card-graphic h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <div class="text-muted">${title}</div>
                            <div class="stat-value">${value}</div>
                            ${subtitle ? `<div class="small-muted">${subtitle}</div>` : ""}
                        </div>
                        <div class="kpi-icon">●</div>
                    </div>
                    <div class="kpi-mini-chart mt-2">
                        <canvas id="${id}" height="42"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function makeMiniLineChart(canvasId, values) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const chart = new Chart(canvas, {
        type: "line",
        data: {
            labels: values.map((_, i) => i + 1),
            datasets: [{
                data: values,
                borderWidth: 2,
                tension: 0.35,
                fill: true,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            scales: { x: { display: false }, y: { display: false } },
            elements: { line: { borderWidth: 2 } }
        }
    });
    kpiMiniCharts.push(chart);
}

function makeMiniDoughnutChart(canvasId, values) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const chart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["Valeur", "Reste"],
            datasets: [{ data: values }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "70%",
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
    });
    kpiMiniCharts.push(chart);
}

function miniSeries(value, maxValue) {
    const base = Number(value || 0);
    const max = Math.max(Number(maxValue || 1), 1);
    const ratio = Math.max(base / max, 0.05);
    return [
        Math.round(max * ratio * 0.35),
        Math.round(max * ratio * 0.50),
        Math.round(max * ratio * 0.45),
        Math.round(max * ratio * 0.70),
        Math.round(max * ratio * 0.60),
        Math.round(max * ratio * 0.85),
        Math.round(max * ratio)
    ];
}

function renderKpis(kpis) {
    destroyMiniCharts();
    const container = document.getElementById("kpiContainer");

    const totalCopies = Math.max(kpis.total_book_copies || 1, 1);
    const totalLoans = Math.max(kpis.total_loans || 1, 1);
    const totalStudents = Math.max(kpis.total_students || 1, 1);

    container.innerHTML = `
        ${kpiCard("miniTitles", "Titres de livres", kpis.total_book_titles, "Catalogue", "line")}
        ${kpiCard("miniCopies", "Exemplaires", kpis.total_book_copies, "Stock total", "line")}
        ${kpiCard("miniAvailable", "Disponibles", kpis.available_books, "Disponibilité actuelle", "doughnut")}
        ${kpiCard("miniBorrowed", "Empruntés", kpis.borrowed_books, "Exemplaires sortis", "doughnut")}
        ${kpiCard("miniActiveLoans", "Emprunts actifs", kpis.active_loans, "En cours", "line")}
        ${kpiCard("miniLateLoans", "Retards", kpis.late_loans, kpis.late_loans > 0 ? "À traiter rapidement" : "Aucun retard", "doughnut")}
        ${kpiCard("miniStudents", "Étudiants", kpis.total_students, "Utilisateurs inscrits", "line")}
        ${kpiCard("miniStock", "Stock faible", kpis.low_stock_books, `${kpis.out_of_stock_books} en rupture`, "doughnut")}
    `;

    makeMiniLineChart("miniTitles", miniSeries(kpis.total_book_titles, Math.max(kpis.total_book_titles, 10)));
    makeMiniLineChart("miniCopies", miniSeries(kpis.total_book_copies, Math.max(kpis.total_book_copies, 10)));
    makeMiniDoughnutChart("miniAvailable", [kpis.available_books, Math.max(totalCopies - kpis.available_books, 0)]);
    makeMiniDoughnutChart("miniBorrowed", [kpis.borrowed_books, Math.max(totalCopies - kpis.borrowed_books, 0)]);
    makeMiniLineChart("miniActiveLoans", miniSeries(kpis.active_loans, Math.max(totalLoans, 5)));
    makeMiniDoughnutChart("miniLateLoans", [kpis.late_loans, Math.max(kpis.active_loans - kpis.late_loans, 1)]);
    makeMiniLineChart("miniStudents", miniSeries(kpis.total_students, Math.max(totalStudents, 5)));
    makeMiniDoughnutChart("miniStock", [kpis.low_stock_books, Math.max(kpis.total_book_titles - kpis.low_stock_books, 1)]);
}

function renderAvailabilityChart(data) {
    destroyChart(availabilityChart);
    const ctx = document.getElementById("availabilityChart");
    availabilityChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Disponibles", "Empruntés"],
            datasets: [{ data: [data.available, data.borrowed] }]
        }
    });
}

function renderLoansStatusChart(items) {
    destroyChart(loansStatusChart);
    const ctx = document.getElementById("loansStatusChart");
    loansStatusChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: items.map(x => x.status),
            datasets: [{ label: "Nombre d'emprunts", data: items.map(x => x.count) }]
        },
        options: { scales: { y: { beginAtZero: true } } }
    });
}

function renderBooksByCategoryChart(items) {
    destroyChart(booksByCategoryChart);
    const ctx = document.getElementById("booksByCategoryChart");
    booksByCategoryChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: items.map(x => x.category),
            datasets: [{ label: "Nombre de livres", data: items.map(x => x.count) }]
        },
        options: { indexAxis: "y", scales: { x: { beginAtZero: true } } }
    });
}

function renderTopBorrowedBooksChart(items) {
    destroyChart(topBorrowedBooksChart);
    const ctx = document.getElementById("topBorrowedBooksChart");
    if (!items.length) {
        ctx.parentElement.innerHTML = `<h4>Top livres empruntés</h4><p>Aucun emprunt enregistré.</p><canvas id="topBorrowedBooksChart"></canvas>`;
        return;
    }
    topBorrowedBooksChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: items.map(x => x.title.length > 28 ? x.title.substring(0, 28) + "..." : x.title),
            datasets: [{ label: "Nombre d'emprunts", data: items.map(x => x.loan_count) }]
        },
        options: { indexAxis: "y", scales: { x: { beginAtZero: true } } }
    });
}

function renderStockAlerts(items) {
    const container = document.getElementById("stockAlertsContainer");
    if (!items.length) {
        container.innerHTML = `<p>Aucune alerte de stock.</p>`;
        return;
    }
    container.innerHTML = `
        <table class="table table-sm table-striped">
            <thead><tr><th>Livre</th><th>Qté</th><th>Disponible</th><th>Alerte</th></tr></thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.title}</td><td>${item.quantity}</td><td>${item.available_quantity}</td>
                        <td><span class="badge ${item.alert_level === "rupture" ? "bg-danger" : "bg-warning text-dark"}">${item.alert_level}</span></td>
                    </tr>`).join("")}
            </tbody>
        </table>`;
}

function renderLateLoans(items) {
    const container = document.getElementById("lateLoansContainer");
    if (!items.length) {
        container.innerHTML = `<p>Aucun emprunt en retard.</p>`;
        return;
    }
    container.innerHTML = `
        <table class="table table-sm table-striped">
            <thead><tr><th>Étudiant</th><th>Livre</th><th>Date limite</th><th>Jours</th></tr></thead>
            <tbody>
                ${items.map(item => `
                    <tr><td>${item.student_name}</td><td>${item.book_title}</td><td>${item.due_date || ""}</td><td><span class="badge bg-danger">${item.days_late}</span></td></tr>`).join("")}
            </tbody>
        </table>`;
}

async function loadLibrarianDashboard() {
    try {
        const data = await apiGet("/librarian/dashboard");
        renderKpis(data.kpis);
        renderAvailabilityChart(data.availability_chart);
        renderLoansStatusChart(data.loans_status_chart || []);
        renderBooksByCategoryChart(data.books_by_category || []);
        renderTopBorrowedBooksChart(data.top_borrowed_books || []);
        renderStockAlerts(data.stock_alerts || []);
        renderLateLoans(data.late_loans || []);
        document.getElementById("lastUpdate").textContent = formatDateTime();

        if (!refreshTimer) {
            const seconds = data.auto_refresh_seconds || 30;
            refreshTimer = setInterval(loadLibrarianDashboard, seconds * 1000);
        }
    } catch (error) {
        console.error(error);
        alert("Erreur dashboard bibliothécaire : " + error.message);
    }
}

loadLibrarianDashboard();

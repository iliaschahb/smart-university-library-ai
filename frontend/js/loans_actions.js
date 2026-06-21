async function createLoanFromForm() {
    const message = document.getElementById('createLoanMessage');
    const payload = {
        student_id: Number(document.getElementById('loanStudentId').value),
        book_id: Number(document.getElementById('loanBookId').value),
        days: Number(document.getElementById('loanDays').value || 14),
    };

    message.innerHTML = '<span class="small-muted">Création en cours...</span>';
    try {
        const data = await apiPost('/loans/create', payload);
        message.innerHTML = `<span class="text-success">${data.message}</span>`;
        await loadLoansActions();
    } catch (error) {
        message.innerHTML = `<span class="text-danger">${error.message}</span>`;
    }
}

async function returnLoan(loanId) {
    if (!confirm(`Confirmer le retour de l'emprunt ${loanId} ?`)) return;
    try {
        const data = await apiPost(`/loans/${loanId}/return`, {});
        alert(data.message || 'Retour enregistré.');
        await loadLoansActions();
    } catch (error) {
        alert(error.message);
    }
}

async function loadLoansActions() {
    const c = document.getElementById('loansActionsContainer');
    c.innerHTML = '<div class="loading-text">Chargement...</div>';
    try {
        const data = await apiGet('/catalog/loans?page_size=50');
        const items = Array.isArray(data) ? data : (data.items || data.loans || []);
        if (!items.length) {
            c.innerHTML = '<p>Aucun emprunt trouvé.</p>';
            return;
        }
        c.innerHTML = `
            <table class="table table-bordered table-striped align-middle">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Étudiant</th>
                        <th>Livre</th>
                        <th>Début</th>
                        <th>Échéance</th>
                        <th>Retour</th>
                        <th>Statut</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(item => {
                        const loanId = item.loan_id || item.id;
                        const returned = item.return_date;
                        const studentLabel = item.student_name || item.student || item.student_id || '-';
                        const bookLabel = item.book_title || item.title || item.book || item.book_id || '-';
                        return `
                            <tr>
                                <td>${loanId}</td>
                                <td>${escapeHtmlSafe(studentLabel)}</td>
                                <td>${escapeHtmlSafe(bookLabel)}</td>
                                <td>${escapeHtmlSafe(item.borrow_date || '')}</td>
                                <td>${escapeHtmlSafe(item.due_date || '')}</td>
                                <td>${escapeHtmlSafe(item.return_date || '')}</td>
                                <td>${statusBadge(item.status)}</td>
                                <td>${returned ? '<span class="text-success">Retourné</span>' : `<button class="btn btn-sm btn-outline-success" onclick="returnLoan(${loanId})">Retourner</button>`}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        c.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

(async function initLoansActions() {
    const ok = await requireAppUserPage();
    if (!ok) return;
    await loadLoansActions();
})();

function renderLoans(items) {
    const c = document.getElementById('loansContainer');

    if (!items || !items.length) {
        c.innerHTML = '<p>Aucun emprunt trouvé.</p>';
        return;
    }

    c.innerHTML = `
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Étudiant</th>
                    <th>Livre</th>
                    <th>Date emprunt</th>
                    <th>Date limite</th>
                    <th>Date retour</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.loan_id}</td>
                        <td>${item.student_name || ''}</td>
                        <td>${item.book_title || ''}</td>
                        <td>${item.borrow_date || ''}</td>
                        <td>${item.due_date || ''}</td>
                        <td>${item.return_date || ''}</td>
                        <td>
                            <span class="badge ${
                                item.status === 'LATE'
                                    ? 'bg-danger'
                                    : item.status === 'BORROWED'
                                    ? 'bg-warning text-dark'
                                    : 'bg-success'
                            }">${item.status}</span>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function loadLoans() {
    try {
        const items = await apiGet('/catalog/loans');
        renderLoans(items || []);
    } catch (error) {
        console.error(error);
        alert('Erreur emprunts : ' + error.message);
    }
}

loadLoans();

function renderStudents(items) {
    const c = document.getElementById('studentsContainer');

    if (!items || !items.length) {
        c.innerHTML = '<p>Aucun étudiant trouvé.</p>';
        return;
    }

    c.innerHTML = `
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nom complet</th>
                    <th>Email</th>
                    <th>Département</th>
                    <th>Niveau</th>
                    <th>Nombre d'emprunts</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.student_id}</td>
                        <td>${item.full_name}</td>
                        <td>${item.email}</td>
                        <td>${item.department || ''}</td>
                        <td>${item.level || ''}</td>
                        <td>${item.loans_count}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function loadStudents() {
    try {
        const items = await apiGet('/catalog/students');
        renderStudents(items || []);
    } catch (error) {
        console.error(error);
        alert('Erreur étudiants : ' + error.message);
    }
}

loadStudents();

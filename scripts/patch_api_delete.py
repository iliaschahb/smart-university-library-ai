from pathlib import Path
path = Path('frontend/js/api.js')
content = path.read_text(encoding='utf-8')
if 'async function apiDelete' not in content:
    content += '''

async function apiDelete(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
        credentials: 'include'
    });
    const data = await parseJsonResponse(response);
    if (!response.ok) throw new Error(data.error || data.message || 'Erreur API');
    return data;
}
'''
    path.write_text(content, encoding='utf-8')
    print('apiDelete ajouté dans frontend/js/api.js')
else:
    print('apiDelete existe déjà')

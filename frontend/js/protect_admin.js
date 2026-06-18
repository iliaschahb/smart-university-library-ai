(async function protectAdminPage() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    if (currentPage === 'login.html') return;
    await requireAdminPage();
})();

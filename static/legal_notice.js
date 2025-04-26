document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('legalNoticeModal');
    const hasAccepted = localStorage.getItem('legalNoticeAccepted');

    if (modal && !hasAccepted) {
        setTimeout(() => {
            modal.classList.add('show');
        }, 500); // Delay to ensure DOM is fully loaded
    }
});

function closeLegalNotice() {
    const modal = document.getElementById('legalNoticeModal');
    if (modal) {
        modal.classList.remove('show');
        localStorage.setItem('legalNoticeAccepted', 'true');
    }
}

function showLegalNotice() {
    const modal = document.getElementById('legalNoticeModal');
    if (modal) {
        modal.classList.add('show');
    }
}
// Add a simple click animation for contact icons
document.querySelectorAll('.contact-form a').forEach(link => {
    link.addEventListener('mousedown', () => {
        link.style.transform = 'scale(0.92)';
    });
    link.addEventListener('mouseup', () => {
        link.style.transform = '';
    });
    link.addEventListener('mouseleave', () => {
        link.style.transform = '';
    });
});
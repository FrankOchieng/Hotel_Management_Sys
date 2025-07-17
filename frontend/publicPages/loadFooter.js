document.addEventListener('DOMContentLoaded', function() {
    fetch('footer.html') // Path to your footer HTML snippet
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.text();
        })
        .then(html => {
            const footerPlaceholder = document.getElementById('footer-placeholder');
            if (footerPlaceholder) {
                footerPlaceholder.innerHTML = html;
            } else {
                console.error('Footer placeholder div not found!');
            }
        })
        .catch(error => {
            console.error('There was a problem loading the footer:', error);
        });
});
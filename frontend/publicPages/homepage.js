document.addEventListener('DOMContentLoaded', function() {
    // Select the hamburger icon and the navigation links container
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.getElementById('navLinks');

    // Function to toggle the menu's active state
    function toggleMenu() {
        hamburger.classList.toggle('active'); // Toggles 'active' class on hamburger for animation
        navLinks.classList.toggle('active');   // Toggles 'active' class on nav links to show/hide
    }

    // Event listener for the hamburger icon click
    if (hamburger && navLinks) { // Ensure elements exist before adding listeners
        hamburger.addEventListener('click', toggleMenu);
    }

    // Optional: Close the menu when a navigation link is clicked (on small screens)
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            // Only close the menu if the screen width is within the mobile breakpoint
            if (window.innerWidth <= 768) {
                // Remove 'active' classes to hide menu and reset hamburger icon
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    });
});
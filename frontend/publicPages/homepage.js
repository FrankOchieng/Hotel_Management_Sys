document.addEventListener('DOMContentLoaded', function() {
    // --- Existing Navigation Toggling Functionality ---
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.getElementById('navLinks');

    function toggleMenu() {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    }

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', toggleMenu);
    }

    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    });

    // --- NEW: Auto-Scrolling Carousel Functionality for Features Section ---
    const carousel = document.querySelector('.features-carousel');
    let scrollDirection = 1; // 1 for right, -1 for left
    let scrollInterval;
    const scrollSpeed = 2; // Pixels per interval (smaller for smoother animation)
    const intervalTime = 20; // Milliseconds between scrolls (smaller for more frequent updates)
    const paddingBuffer = 100; // Extra padding to ensure smooth reversal

    if (carousel) { // FIX: Only check for the carousel element, arrows are gone
        // Add dynamic padding to the carousel to allow for smoother reversal
        // This ensures the carousel can scroll 'past' its true ends slightly before reversing.
        carousel.style.paddingRight = `${paddingBuffer}px`;
        carousel.style.paddingLeft = `${paddingBuffer}px`;

        // Function to start auto-scrolling
        const startAutoScroll = () => {
            if (scrollInterval) return; // Prevent multiple intervals running
            scrollInterval = setInterval(() => {
                carousel.scrollLeft += scrollDirection * scrollSpeed;

                // Determine effective scrollable width (total content minus visible area)
                const maxScrollLeft = carousel.scrollWidth - carousel.clientWidth;

                // Check if reached end (scrolling right)
                // Add a small tolerance (e.g., 1 pixel) for floating point inaccuracies
                if (scrollDirection === 1 && carousel.scrollLeft >= maxScrollLeft - 1) {
                    scrollDirection = -1; // Reverse direction to left
                }
                // Check if reached beginning (scrolling left)
                else if (scrollDirection === -1 && carousel.scrollLeft <= 1) { // Small tolerance for beginning
                    scrollDirection = 1; // Reverse direction to right
                }
            }, intervalTime);
        };

        // Function to stop auto-scrolling
        const stopAutoScroll = () => {
            clearInterval(scrollInterval);
            scrollInterval = null; // Clear the interval ID
        };

        // Start scrolling when page loads
        startAutoScroll();

        // Pause on hover
        carousel.addEventListener('mouseenter', stopAutoScroll);
        carousel.addEventListener('mouseleave', startAutoScroll);

        // Optional: Restart scrolling on window resize to re-evaluate dimensions
        window.addEventListener('resize', () => {
            stopAutoScroll();
            // Give a small delay before restarting in case layout is still settling
            setTimeout(startAutoScroll, 150);
        });
    }
});
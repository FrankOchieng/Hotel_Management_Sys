document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('jwt_token');
    const userName = localStorage.getItem('user_name') || 'Guest';

    // Diagnostic log to help you check if the browser remembers you
    console.log("Auth Status: ", token ? "Logged In" : "Logged Out", "| User: ", userName);

    if (token) {
        // 1. Find EVERY link that points to the login page
        const loginLinks = document.querySelectorAll('a[href*="loginPage.html"]');
        
        loginLinks.forEach(loginLink => {
            // Create the new Profile & Logout container
            const authContainer = document.createElement('div');
            // Using Tailwind classes so it perfectly matches your navigation styles
            authContainer.className = 'flex items-center space-x-4 ml-4'; 
            authContainer.innerHTML = `
                <span class="text-sm font-bold text-gray-800">👋 Hi, ${userName}</span>
                <button onclick="performLogout()" class="text-sm font-bold text-red-600 hover:text-red-800 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-md transition-colors shadow-sm">
                    Logout
                </button>
            `;

            // Replace the old Login link with the new Auth container
            if (loginLink.parentElement && loginLink.parentElement.tagName === 'LI') {
                // For pages using <ul><li> lists (like bookings)
                loginLink.parentElement.replaceChild(authContainer, loginLink);
            } else {
                // For pages using raw flex links (like rooms)
                loginLink.replaceWith(authContainer);
            }
        });

        // 2. Hide any remaining register links
        const registerLinks = document.querySelectorAll('a[href*="registrationPage.html"]');
        registerLinks.forEach(link => link.style.display = 'none');
    }
});

// Global Logout Function
window.performLogout = function() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    alert('You have been logged out.');
    window.location.href = 'loginPage.html';
};
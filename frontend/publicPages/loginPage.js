const API_BASE_URL = 'http://localhost:5000'; // Ensure this points to your Flask port

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // 1. Safely get the input elements
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const submitButton = loginForm.querySelector('button[type="submit"]');

            if (!emailInput || !passwordInput) {
                console.error("Email or Password input fields are missing from the HTML.");
                return;
            }

            const email = emailInput.value;
            const password = passwordInput.value;

            // 2. Visual feedback for the user
            const originalButtonText = submitButton.innerText;
            submitButton.innerText = 'Signing in...';
            submitButton.disabled = true;

            try {
                // 3. Send request to backend
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: email, password: password })
                });

                // 4. Check if the server returned HTML (error page) instead of JSON
                const contentType = response.headers.get("content-type");
                let data;
                
                if (contentType && contentType.includes("application/json")) {
                    data = await response.json();
                } else {
                    const text = await response.text();
                    throw new Error(`Server returned a non-JSON response. It might be crashing. Response snippet: ${text.substring(0, 50)}...`);
                }

                // 5. Process the JSON data
                if (response.ok) {
                    if (data.token) {
                        localStorage.setItem('jwt_token', data.token); 
                    }
                    localStorage.setItem('user_role', data.user.role || 'customer');
                    
                    // --- NEW: Save the user's name! ---
                    localStorage.setItem('user_name', data.user.first_name || 'Guest');

                    alert('Login successful! Welcome back.');
                    window.location.href = 'roomsPage.html'; 
                } 
                 else {
                    // Display the exact error sent by your Flask backend
                    alert(`Login failed: ${data.error || data.message || 'Invalid credentials'}`);
                    
                    // Reset button
                    submitButton.innerText = originalButtonText;
                    submitButton.disabled = false;
                }

            } catch (error) {
                console.error('Error during login:', error);
                alert(`Connection Error: ${error.message}`);
                
                // Reset button
                submitButton.innerText = originalButtonText;
                submitButton.disabled = false;
            }
        });
    }

    // Navigation active state logic
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
});
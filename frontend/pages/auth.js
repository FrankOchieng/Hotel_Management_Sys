 // Common JavaScript for navigation and logout (copied from index.html for self-containment)
        const API_BASE_URL = 'http://localhost:5000';

        function getAuthToken() {
            return localStorage.getItem('jwt_token');
        }

        function removeAuthToken() {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_role');
        }

        function showMessage(message, type = 'info', targetId = 'auth-message-box') {
            const msgBox = document.getElementById(targetId);
            msgBox.textContent = message;
            msgBox.className = 'mt-4 p-3 rounded-md text-sm';
            if (type === 'success') {
                msgBox.classList.add('bg-green-100', 'text-green-800');
            } else if (type === 'error') {
                msgBox.classList.add('bg-red-100', 'text-red-800');
            } else {
                msgBox.classList.add('bg-blue-100', 'text-blue-800');
            }
            msgBox.classList.remove('hidden');
            setTimeout(() => {
                msgBox.classList.add('hidden');
            }, 5000);
        }

        document.getElementById('logoutBtn').addEventListener('click', async () => {
            const token = getAuthToken();
            if (!token) {
                showMessage('You are not logged in.', 'info', 'auth-message-box');
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    removeAuthToken();
                    showMessage('Logged out successfully!', 'success', 'auth-message-box');
                    window.location.href = 'auth.html';
                } else {
                    const errorData = await response.json();
                    showMessage(`Logout failed: ${errorData.error || response.statusText}`, 'error', 'auth-message-box');
                }
            } catch (error) {
                console.error('Error during logout:', error);
                showMessage('An error occurred during logout. Please try again.', 'error', 'auth-message-box');
            }
        });

        // Specific JavaScript for auth.html
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        const formTitle = document.getElementById('form-title');
        const toggleFormLink = document.getElementById('toggle-form-link');
        const toggleFormText = document.getElementById('toggle-form-text');

        let isLoginForm = true;

        toggleFormLink.addEventListener('click', () => {
            isLoginForm = !isLoginForm;
            if (isLoginForm) {
                formTitle.textContent = 'Login';
                loginForm.classList.remove('hidden');
                registerForm.classList.add('hidden');
                toggleFormText.textContent = "Don't have an account?";
                toggleFormLink.textContent = "Register here";
            } else {
                formTitle.textContent = 'Register';
                loginForm.classList.add('hidden');
                registerForm.classList.remove('hidden');
                toggleFormText.textContent = "Already have an account?";
                toggleFormLink.textContent = "Login here";
            }
        });

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('jwt_token', data.token);
                    localStorage.setItem('user_role', data.user.role);
                    showMessage('Login successful!', 'success', 'auth-message-box');
                    window.location.href = 'index.html'; // Redirect to home or dashboard
                } else {
                    showMessage(`Login failed: ${data.error || 'Unknown error'}`, 'error', 'auth-message-box');
                }
            } catch (error) {
                console.error('Error during login:', error);
                showMessage('An error occurred. Please try again.', 'error', 'auth-message-box');
            }
        });

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const first_name = document.getElementById('register-first-name').value;
            const last_name = document.getElementById('register-last-name').value;
            const email = document.getElementById('register-email').value;
            const phone = document.getElementById('register-phone').value;
            const password = document.getElementById('register-password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ first_name, last_name, email, phone, password })
                });

                const data = await response.json();
                if (response.ok) {
                    showMessage('Registration successful! Please log in.', 'success', 'auth-message-box');
                    // Switch to login form after successful registration
                    isLoginForm = true;
                    formTitle.textContent = 'Login';
                    loginForm.classList.remove('hidden');
                    registerForm.classList.add('hidden');
                    toggleFormText.textContent = "Don't have an account?";
                    toggleFormLink.textContent = "Register here";
                    // Clear registration form fields
                    registerForm.reset();
                } else {
                    showMessage(`Registration failed: ${data.error || 'Unknown error'}`, 'error', 'auth-message-box');
                }
            } catch (error) {
                console.error('Error during registration:', error);
                showMessage('An error occurred. Please try again.', 'error', 'auth-message-box');
            }
        });

        // Basic check to show/hide admin link
        document.addEventListener('DOMContentLoaded', () => {
            const adminLink = document.querySelector('a[href="admin.html"]');
            const userRole = localStorage.getItem('user_role');
            if (userRole === 'admin') {
                adminLink.style.display = 'inline-block';
            } else {
                adminLink.style.display = 'none';
            }
        });
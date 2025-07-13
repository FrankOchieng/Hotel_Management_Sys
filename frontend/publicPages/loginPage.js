// Form submission
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember').checked;
            
            console.log('Login attempt:', { email, password, remember });
            
            // Simulate login process
            alert('Login successful! Welcome back to LuxeStay.');
            
            // Redirect to home page
            window.location.href = 'customerDshboard.html';
        });

        // Social login
        function socialLogin(provider) {
            alert(`${provider} login selected - Integration would happen here`);
        }

        // Navigation active state
        document.addEventListener('DOMContentLoaded', function() {
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const navLinks = document.querySelectorAll('.nav-links a');
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === currentPage) {
                    link.classList.add('active');
                }
            });
        });
const API_BASE_URL = 'http://localhost:5000'; 

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            
            const originalText = submitBtn.innerText;
            submitBtn.innerText = 'Creating Account...';
            submitBtn.disabled = true;

            try {
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        first_name: firstName,
                        last_name: lastName,
                        email: email,
                        password: password,
                        phone: '' 
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    alert('Registration successful! Please log in.');
                    window.location.href = 'loginPage.html'; 
                } else {
                    alert(`Registration failed: ${data.error || 'Check your details and try again.'}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Connection error. Ensure the backend server is running.');
            } finally {
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});
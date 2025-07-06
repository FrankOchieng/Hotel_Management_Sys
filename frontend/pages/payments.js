 // Common JavaScript for navigation and logout
        const API_BASE_URL = 'http://localhost:5000';

        function getAuthToken() {
            return localStorage.getItem('jwt_token');
        }

        function removeAuthToken() {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_role');
        }

        function showMessage(message, type = 'info', targetId = 'payments-message-box') {
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
                showMessage('You are not logged in.', 'info');
                return;
            }

            try     method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });
…        }{
                const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    removeAuthToken();
                    showMessage('Logged out successfully!', 'success');
                    window.location.href = 'auth.html';
                } else {
                    const errorData = await response.json();
                    showMessage(`Logout failed: ${errorData.error || response.statusText}`, 'error');
                }
            } catch (error) {
                console.error('Error during logout:', error);
                showMessage('An error occurred during logout. Please try again.', 'error');
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

            checkPaymentStatus();
        });

        // Specific JavaScript for payments.html
        const paymentStatusBox = document.getElementById('payment-status-box');

        async function checkPaymentStatus() {
            const urlParams = new URLSearchParams(window.location.search);
            const sessionId = urlParams.get('session_id'); // From Stripe success URL

            if (sessionId) {
                // In a real application, you'd likely have a backend endpoint
                // to verify the Stripe session and fetch payment details.
                // For this example, we'll just display a success message,
                // assuming the webhook handled the backend update.
                paymentStatusBox.innerHTML = `
                    <div class="success-icon">&#10004;</div>
                    <h3 class="text-2xl font-bold text-green-700 mb-2">Payment Successful!</h3>
                    <p class="text-gray-700">Your booking has been confirmed.</p>
                    <p class="text-gray-500 text-sm mt-2">Stripe Session ID: ${sessionId}</p>
                    <a href="bookings.html" class="form-button mt-4 inline-block">View My Bookings</a>
                `;
                showMessage('Payment processed successfully!', 'success');
            } else {
                // If no session_id, it might be a direct visit or a cancellation
                paymentStatusBox.innerHTML = `
                    <div class="error-icon">&#10060;</div>
                    <h3 class="text-2xl font-bold text-red-700 mb-2">Payment Status Unknown or Cancelled</h3>
                    <p class="text-gray-700">There was an issue with your payment, or the payment process was cancelled.</p>
                    <a href="bookings.html" class="form-button bg-blue-500 hover:bg-blue-600 mt-4 inline-block">Try Booking Again</a>
                `;
                showMessage('Payment was not completed or an error occurred.', 'error');

                // Optionally, fetch payment details if a bookingId is passed
                const bookingId = urlParams.get('bookingId');
                if (bookingId) {
                    try {
                        const token = getAuthToken();
                        if (!token) {
                            showMessage('Please log in to view payment details.', 'info');
                            return;
                        }
                        const response = await fetch(`${API_BASE_URL}/payments/${bookingId}`, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const data = await response.json();
                        if (response.ok && data.length > 0) {
                            const latestPayment = data[data.length - 1]; // Get the latest payment
                            paymentStatusBox.innerHTML = `
                                <h3 class="text-xl font-bold text-gray-700 mb-2">Payment Details for Booking ${bookingId.substring(0,8)}...</h3>
                                <p>Amount: $${latestPayment.amount}</p>
                                <p>Method: ${latestPayment.payment_method.toUpperCase()}</p>
                                <p>Status: <span class="${latestPayment.payment_status === 'paid' ? 'text-green-600' : latestPayment.payment_status === 'pending' ? 'text-yellow-600' : 'text-red-600'}">${latestPayment.payment_status.toUpperCase()}</span></p>
                                <p class="text-gray-500 text-sm mt-2">Transaction ID: ${latestPayment.stripe_payment_id || 'N/A'}</p>
                                <a href="bookings.html" class="form-button mt-4 inline-block">View My Bookings</a>
                            `;
                        } else {
                            showMessage('No payment details found for this booking.', 'info');
                        }
                    } catch (error) {
                        console.error('Error fetching payment details:', error);
                        showMessage('An error occurred while fetching payment details.', 'error');
                    }
                }
            }
        }
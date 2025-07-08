  // Common JavaScript for navigation and logout
        const API_BASE_URL = 'http://localhost:5000';

        function getAuthToken() {
            return localStorage.getItem('jwt_token');
        }

        function removeAuthToken() {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_role');
        }

        function showMessage(message, type = 'info', targetId = 'bookings-message-box') {
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

            // Redirect if not logged in
            if (!getAuthToken()) {
                showMessage('Please log in to view your bookings.', 'info');
                setTimeout(() => { window.location.href = 'auth.html'; }, 1500);
            } else {
                fetchBookings();
                fetchServicesForBookingForms();
            }
        });

        // Modals functionality
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'flex';
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }

        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }

        // Specific JavaScript for bookings.html
        const myBookingsList = document.getElementById('my-bookings-list');
        const createBookingForm = document.getElementById('create-booking-form');
        const createServicesList = document.getElementById('create-services-list');
        const modifyBookingForm = document.getElementById('modify-booking-form');
        const modifyServicesList = document.getElementById('modify-services-list');

        let allServices = []; // To store all available services

        async function fetchServicesForBookingForms() {
            try {
                const response = await fetch(`${API_BASE_URL}/services`, {
                    headers: { 'Authorization': `Bearer ${getAuthToken()}` }
                });
                const data = await response.json();
                if (response.ok) {
                    allServices = data;
                    renderServicesCheckboxes(createServicesList, 'create-service');
                    // renderServicesCheckboxes(modifyServicesList, 'modify-service'); // Will be called when modal opens
                } else {
                    showMessage(`Failed to load services: ${data.error || response.statusText}`, 'error', 'create-booking-message-box');
                }
            } catch (error) {
                console.error('Error fetching services:', error);
                showMessage('An error occurred while fetching services.', 'error', 'create-booking-message-box');
            }
        }

        function renderServicesCheckboxes(targetElement, prefix, selectedServiceIds = []) {
            targetElement.innerHTML = ''; // Clear previous
            if (allServices.length === 0) {
                targetElement.innerHTML = '<p class="text-gray-500">No services available.</p>';
                return;
            }

            allServices.forEach(service => {
                const isChecked = selectedServiceIds.includes(service.id);
                const checkboxDiv = document.createElement('div');
                checkboxDiv.className = 'flex items-center space-x-2';
                checkboxDiv.innerHTML = `
                    <input type="checkbox" id="${prefix}-${service.id}" name="${prefix}" value="${service.id}" data-price="${service.price}" ${isChecked ? 'checked' : ''} class="rounded text-blue-600 focus:ring-blue-500">
                    <label for="${prefix}-${service.id}" class="text-gray-700">${service.name} ($${service.price})</label>
                `;
                targetElement.appendChild(checkboxDiv);
            });
        }


        async function fetchBookings() {
            myBookingsList.innerHTML = '<p class="text-center text-gray-500 col-span-full">Loading your bookings...</p>';
            try {
                const token = getAuthToken();
                if (!token) {
                    showMessage('Authentication token not found. Please log in.', 'error');
                    return;
                }

                const response = await fetch(`${API_BASE_URL}/bookings`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                if (response.ok) {
                    displayBookings(data);
                } else {
                    showMessage(`Error fetching bookings: ${data.error || response.statusText}`, 'error');
                    myBookingsList.innerHTML = `<p class="text-center text-red-500 col-span-full">Error: ${data.error || 'Failed to load bookings.'}</p>`;
                }
            } catch (error) {
                console.error('Error fetching bookings:', error);
                showMessage('An error occurred while fetching bookings. Please try again.', 'error');
                myBookingsList.innerHTML = `<p class="text-center text-red-500 col-span-full">An unexpected error occurred.</p>`;
            }
        }

        function displayBookings(bookings) {
            myBookingsList.innerHTML = ''; // Clear previous results
            if (bookings.length === 0) {
                myBookingsList.innerHTML = '<p class="text-center text-gray-500 col-span-full">You have no bookings yet.</p>';
                return;
            }

            bookings.forEach(booking => {
                const bookingCard = document.createElement('div');
                bookingCard.className = 'booking-card';
                bookingCard.innerHTML = `
                    <h4 class="text-lg font-semibold mb-2">Booking ID: ${booking.id.substring(0, 8)}...</h4>
                    <p>Room: ${booking.room_number}</p>
                    <p>Check-in: ${new Date(booking.check_in_date).toLocaleDateString()}</p>
                    <p>Check-out: ${new Date(booking.check_out_date).toLocaleDateString()}</p>
                    <p>Total Amount: $${booking.total_amount}</p>
                    <p>Status: <span class="font-medium ${booking.booking_status === 'confirmed' ? 'text-green-600' : booking.booking_status === 'pending' ? 'text-yellow-600' : 'text-red-600'}">${booking.booking_status.toUpperCase()}</span></p>
                    <p>Payment: <span class="font-medium ${booking.payment_status === 'paid' ? 'text-green-600' : booking.payment_status === 'pending' ? 'text-yellow-600' : 'text-red-600'}">${booking.payment_status.toUpperCase()}</span></p>
                    <div class="mt-4 flex space-x-2">
                        <button class="form-button bg-blue-500 hover:bg-blue-600 px-3 py-1 text-sm" onclick="viewBookingDetails('${booking.id}')">Details</button>
                        <button class="form-button bg-yellow-500 hover:bg-yellow-600 px-3 py-1 text-sm" onclick="openModifyModal('${booking.id}')">Modify</button>
                        <button class="form-button bg-red-500 hover:bg-red-600 px-3 py-1 text-sm" onclick="cancelBooking('${booking.id}')">Cancel</button>
                    </div>
                `;
                myBookingsList.appendChild(bookingCard);
            });
        }

        createBookingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const room_id = document.getElementById('create-room-id').value;
            const check_in_date = document.getElementById('create-check-in-date').value;
            const check_out_date = document.getElementById('create-check-out-date').value;
            const payment_method = document.getElementById('create-payment-method').value;
            const special_requests = document.getElementById('create-special-requests').value;

            const selectedServices = Array.from(createServicesList.querySelectorAll('input[name="create-service"]:checked'))
                .map(checkbox => ({
                    service_id: checkbox.value,
                    quantity: 1 // Assuming quantity 1 for simplicity, could add input for quantity
                }));

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/bookings`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        room_id,
                        check_in_date,
                        check_out_date,
                        payment_method,
                        special_requests,
                        services: selectedServices
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    showMessage('Booking created successfully!', 'success', 'create-booking-message-box');
                    createBookingForm.reset();
                    fetchBookings(); // Refresh bookings list
                    if (data.checkout_url) {
                        setTimeout(() => {
                            window.location.href = data.checkout_url; // Redirect for card payments
                        }, 1000);
                    }
                } else {
                    showMessage(`Booking failed: ${data.error || response.statusText}`, 'error', 'create-booking-message-box');
                }
            } catch (error) {
                console.error('Error creating booking:', error);
                showMessage('An error occurred while creating booking. Please try again.', 'error', 'create-booking-message-box');
            }
        });

        async function viewBookingDetails(bookingId) {
            openModal('bookingDetailsModal');
            const detailsContent = document.getElementById('booking-details-content');
            detailsContent.innerHTML = '<p class="text-center text-gray-500">Loading details...</p>';
            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    detailsContent.innerHTML = `
                        <p><strong>Booking ID:</strong> ${data.id}</p>
                        <p><strong>User ID:</strong> ${data.user_id}</p>
                        <p><strong>Room:</strong> ${data.room_number} (ID: ${data.room_id})</p>
                        <p><strong>Check-in:</strong> ${new Date(data.check_in_date).toLocaleDateString()}</p>
                        <p><strong>Check-out:</strong> ${new Date(data.check_out_date).toLocaleDateString()}</p>
                        <p><strong>Total Nights:</strong> ${data.total_nights}</p>
                        <p><strong>Total Amount:</strong> $${data.total_amount}</p>
                        <p><strong>Booking Status:</strong> ${data.booking_status.toUpperCase()}</p>
                        <p><strong>Payment Status:</strong> ${data.payment_status.toUpperCase()}</p>
                        <p><strong>Special Requests:</strong> ${data.special_requests || 'None'}</p>
                        <p><strong>Booked On:</strong> ${new Date(data.created_at).toLocaleString()}</p>
                        <h4 class="font-semibold mt-4">Services:</h4>
                        <ul class="list-disc list-inside">
                            ${data.services && data.services.length > 0 ? data.services.map(s => `<li>${s.service_name} (x${s.quantity}) - $${s.total_price}</li>`).join('') : '<li>No additional services</li>'}
                        </ul>
                    `;
                } else {
                    detailsContent.innerHTML = `<p class="text-red-500">Error: ${data.error || response.statusText}</p>`;
                    showMessage(`Failed to load booking details: ${data.error || response.statusText}`, 'error', 'details-message-box');
                }
            } catch (error) {
                console.error('Error fetching booking details:', error);
                detailsContent.innerHTML = `<p class="text-red-500">An error occurred.</p>`;
                showMessage('An error occurred while fetching booking details.', 'error', 'details-message-box');
            }
        }

        async function openModifyModal(bookingId) {
            openModal('modifyBookingModal');
            document.getElementById('modify-booking-id').value = bookingId;
            const modifyMessageBox = document.getElementById('modify-booking-message-box');
            modifyMessageBox.classList.add('hidden'); // Hide previous messages

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    document.getElementById('modify-check-in-date').value = data.check_in_date.split('T')[0];
                    document.getElementById('modify-check-out-date').value = data.check_out_date.split('T')[0];

                    const selectedServiceIds = data.services ? data.services.map(s => s.service_id) : [];
                    renderServicesCheckboxes(modifyServicesList, 'modify-service', selectedServiceIds);
                } else {
                    showMessage(`Failed to load booking for modification: ${data.error || response.statusText}`, 'error', 'modify-booking-message-box');
                    closeModal('modifyBookingModal');
                }
            } catch (error) {
                console.error('Error loading booking for modification:', error);
                showMessage('An error occurred while loading booking for modification.', 'error', 'modify-booking-message-box');
                closeModal('modifyBookingModal');
            }
        }

        modifyBookingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const bookingId = document.getElementById('modify-booking-id').value;
            const new_check_in_date = document.getElementById('modify-check-in-date').value;
            const new_check_out_date = document.getElementById('modify-check-out-date').value;

            const newServices = Array.from(modifyServicesList.querySelectorAll('input[name="modify-service"]:checked'))
                .map(checkbox => ({
                    service_id: checkbox.value,
                    quantity: 1
                }));

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        new_check_in_date,
                        new_check_out_date,
                        new_services: newServices
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    showMessage('Booking modified successfully!', 'success', 'modify-booking-message-box');
                    closeModal('modifyBookingModal');
                    fetchBookings(); // Refresh bookings list
                } else {
                    showMessage(`Modification failed: ${data.error || response.statusText}`, 'error', 'modify-booking-message-box');
                }
            } catch (error) {
                console.error('Error modifying booking:', error);
                showMessage('An error occurred while modifying booking. Please try again.', 'error', 'modify-booking-message-box');
            }
        });

        async function cancelBooking(bookingId) {
            if (!confirm('Are you sure you want to cancel this booking?')) {
                return;
            }

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                const data = await response.json();
                if (response.ok) {
                    showMessage('Booking cancelled successfully!', 'success');
                    fetchBookings(); // Refresh bookings list
                } else {
                    showMessage(`Cancellation failed: ${data.error || response.statusText}`, 'error');
                }
            } catch (error) {
                console.error('Error cancelling booking:', error);
                showMessage('An error occurred while cancelling booking. Please try again.', 'error');
            }
        }

        // Pre-fill dates for convenience
        document.addEventListener('DOMContentLoaded', () => {
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(today.getDate() + 1);

            const formatDate = (date) => date.toISOString().split('T')[0];

            document.getElementById('create-check-in-date').value = formatDate(today);
            document.getElementById('create-check-out-date').value = formatDate(tomorrow);
        });
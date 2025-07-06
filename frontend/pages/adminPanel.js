  // Common JavaScript for navigation and logout
        const API_BASE_URL = 'http://localhost:5000';

        function getAuthToken() {
            return localStorage.getItem('jwt_token');
        }

        function removeAuthToken() {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_role');
        }

        function showMessage(message, type = 'info', targetId = 'admin-message-box') {
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

        // Specific JavaScript for admin.html
        document.addEventListener('DOMContentLoaded', () => {
            const userRole = localStorage.getItem('user_role');
            if (userRole !== 'admin') {
                showMessage('Access Denied. You must be an administrator to view this page.', 'error');
                setTimeout(() => { window.location.href = 'index.html'; }, 2000);
                return;
            }

            // Hide the admin link in the header if not admin
            const adminLink = document.querySelector('a[href="admin.html"]');
            if (userRole === 'admin') {
                adminLink.style.display = 'inline-block';
            } else {
                adminLink.style.display = 'none';
            }

            fetchDashboardStats();
            fetchRooms();
            fetchAllBookings();

            // Pre-fill report dates
            const today = new Date();
            const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
            const formatDate = (date) => date.toISOString().split('T')[0];
            document.getElementById('report-start-date').value = formatDate(firstDayOfMonth);
            document.getElementById('report-end-date').value = formatDate(today);
        });

        // Dashboard Functions
        async function fetchDashboardStats() {
            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    document.getElementById('total-bookings').textContent = data.total_bookings_this_month;
                    document.getElementById('total-revenue').textContent = `$${data.total_revenue_this_month}`;
                    document.getElementById('occupancy-rate').textContent = data.occupancy_rate;
                    document.getElementById('pending-bookings').textContent = data.pending_bookings_count;
                } else {
                    showMessage(`Error fetching dashboard stats: ${data.error || response.statusText}`, 'error');
                }
            } catch (error) {
                console.error('Error fetching dashboard stats:', error);
                showMessage('An error occurred while fetching dashboard stats.', 'error');
            }
        }

        // Room Management Functions
        const roomsTableBody = document.querySelector('#rooms-table tbody');
        const createRoomForm = document.getElementById('create-room-form');
        const editRoomForm = document.getElementById('edit-room-form');

        async function fetchRooms() {
            roomsTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-gray-500">Loading rooms...</td></tr>';
            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/rooms`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    displayRooms(data);
                } else {
                    showMessage(`Error fetching rooms: ${data.error || response.statusText}`, 'error');
                    roomsTableBody.innerHTML = `<tr><td colspan="6" class="text-center text-red-500">Error: ${data.error || 'Failed to load rooms.'}</td></tr>`;
                }
            } catch (error) {
                console.error('Error fetching rooms:', error);
                showMessage('An error occurred while fetching rooms.', 'error');
                roomsTableBody.innerHTML = `<tr><td colspan="6" class="text-center text-red-500">An unexpected error occurred.</td></tr>`;
            }
        }

        function displayRooms(rooms) {
            roomsTableBody.innerHTML = '';
            if (rooms.length === 0) {
                roomsTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-gray-500">No rooms found.</td></tr>';
                return;
            }
            rooms.forEach(room => {
                const row = roomsTableBody.insertRow();
                row.innerHTML = `
                    <td>${room.room_number}</td>
                    <td>${room.room_type.charAt(0).toUpperCase() + room.room_type.slice(1)}</td>
                    <td>${room.capacity}</td>
                    <td>$${room.price_per_night}</td>
                    <td><span class="font-medium ${room.status === 'available' ? 'text-green-600' : room.status === 'occupied' ? 'text-yellow-600' : 'text-red-600'}">${room.status.toUpperCase()}</span></td>
                    <td class="flex space-x-2">
                        <button class="form-button bg-yellow-500 hover:bg-yellow-600 px-3 py-1 text-sm" onclick="openEditRoomModal('${room.id}')">Edit</button>
                        <button class="form-button bg-red-500 hover:bg-red-600 px-3 py-1 text-sm" onclick="deleteRoom('${room.id}')">Delete</button>
                    </td>
                `;
            });
        }

        createRoomForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const roomData = {
                room_number: document.getElementById('new-room-number').value,
                room_type: document.getElementById('new-room-type').value,
                capacity: parseInt(document.getElementById('new-capacity').value),
                price_per_night: parseFloat(document.getElementById('new-price-per-night').value),
                description: document.getElementById('new-description').value,
                amenities: document.getElementById('new-amenities').value.split(',').map(a => a.trim()).filter(a => a),
                status: document.getElementById('new-status').value,
                images: document.getElementById('new-images').value.split(',').map(i => i.trim()).filter(i => i)
            };

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/rooms`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(roomData)
                });
                const data = await response.json();
                if (response.ok) {
                    showMessage('Room created successfully!', 'success', 'create-room-message-box');
                    createRoomForm.reset();
                    closeModal('createRoomModal');
                    fetchRooms();
                } else {
                    showMessage(`Failed to create room: ${data.error || response.statusText}`, 'error', 'create-room-message-box');
                }
            } catch (error) {
                console.error('Error creating room:', error);
                showMessage('An error occurred while creating room. Please try again.', 'error', 'create-room-message-box');
            }
        });

        async function openEditRoomModal(roomId) {
            openModal('editRoomModal');
            document.getElementById('edit-room-id').value = roomId;
            const editRoomMessageBox = document.getElementById('edit-room-message-box');
            editRoomMessageBox.classList.add('hidden');

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/rooms/${roomId}`, { // Using public rooms endpoint for details
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    document.getElementById('edit-room-number').value = data.room_number;
                    document.getElementById('edit-room-type').value = data.room_type;
                    document.getElementById('edit-capacity').value = data.capacity;
                    document.getElementById('edit-price-per-night').value = data.price_per_night;
                    document.getElementById('edit-description').value = data.description;
                    document.getElementById('edit-amenities').value = data.amenities ? data.amenities.join(', ') : '';
                    document.getElementById('edit-status').value = data.status;
                    document.getElementById('edit-images').value = data.images ? data.images.join(', ') : '';
                } else {
                    showMessage(`Failed to load room for editing: ${data.error || response.statusText}`, 'error', 'edit-room-message-box');
                    closeModal('editRoomModal');
                }
            } catch (error) {
                console.error('Error loading room for editing:', error);
                showMessage('An error occurred while loading room for editing.', 'error', 'edit-room-message-box');
                closeModal('editRoomModal');
            }
        }

        editRoomForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const roomId = document.getElementById('edit-room-id').value;
            const roomData = {
                room_number: document.getElementById('edit-room-number').value,
                room_type: document.getElementById('edit-room-type').value,
                capacity: parseInt(document.getElementById('edit-capacity').value),
                price_per_night: parseFloat(document.getElementById('edit-price-per-night').value),
                description: document.getElementById('edit-description').value,
                amenities: document.getElementById('edit-amenities').value.split(',').map(a => a.trim()).filter(a => a),
                status: document.getElementById('edit-status').value,
                images: document.getElementById('edit-images').value.split(',').map(i => i.trim()).filter(i => i)
            };

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/rooms/${roomId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(roomData)
                });
                const data = await response.json();
                if (response.ok) {
                    showMessage('Room updated successfully!', 'success', 'edit-room-message-box');
                    closeModal('editRoomModal');
                    fetchRooms();
                } else {
                    showMessage(`Failed to update room: ${data.error || response.statusText}`, 'error', 'edit-room-message-box');
                }
            } catch (error) {
                console.error('Error updating room:', error);
                showMessage('An error occurred while updating room. Please try again.', 'error', 'edit-room-message-box');
            }
        });

        async function deleteRoom(roomId) {
            if (!confirm('Are you sure you want to delete this room? This action might be irreversible or mark the room as unavailable.')) {
                return;
            }

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/rooms/${roomId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    showMessage('Room deleted successfully!', 'success');
                    fetchRooms();
                } else {
                    showMessage(`Failed to delete room: ${data.error || response.statusText}`, 'error');
                }
            } catch (error) {
                console.error('Error deleting room:', error);
                showMessage('An error occurred while deleting room. Please try again.', 'error');
            }
        }

        // Booking Management Functions
        const bookingsAdminTableBody = document.querySelector('#bookings-admin-table tbody');
        const updateBookingStatusForm = document.getElementById('update-booking-status-form');

        async function fetchAllBookings() {
            bookingsAdminTableBody.innerHTML = '<tr><td colspan="9" class="text-center text-gray-500">Loading bookings...</td></tr>';
            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/bookings`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    displayAllBookings(data);
                } else {
                    showMessage(`Error fetching all bookings: ${data.error || response.statusText}`, 'error');
                    bookingsAdminTableBody.innerHTML = `<tr><td colspan="9" class="text-center text-red-500">Error: ${data.error || 'Failed to load bookings.'}</td></tr>`;
                }
            } catch (error) {
                console.error('Error fetching all bookings:', error);
                showMessage('An error occurred while fetching all bookings.', 'error');
                bookingsAdminTableBody.innerHTML = `<tr><td colspan="9" class="text-center text-red-500">An unexpected error occurred.</td></tr>`;
            }
        }

        function displayAllBookings(bookings) {
            bookingsAdminTableBody.innerHTML = '';
            if (bookings.length === 0) {
                bookingsAdminTableBody.innerHTML = '<tr><td colspan="9" class="text-center text-gray-500">No bookings found.</td></tr>';
                return;
            }
            bookings.forEach(booking => {
                const row = bookingsAdminTableBody.insertRow();
                row.innerHTML = `
                    <td>${booking.id.substring(0, 8)}...</td>
                    <td>${booking.user_email}</td>
                    <td>${booking.room_number}</td>
                    <td>${new Date(booking.check_in_date).toLocaleDateString()}</td>
                    <td>${new Date(booking.check_out_date).toLocaleDateString()}</td>
                    <td>$${booking.total_amount}</td>
                    <td><span class="font-medium ${booking.booking_status === 'confirmed' ? 'text-green-600' : booking.booking_status === 'pending' ? 'text-yellow-600' : 'text-red-600'}">${booking.booking_status.toUpperCase()}</span></td>
                    <td><span class="font-medium ${booking.payment_status === 'paid' ? 'text-green-600' : booking.payment_status === 'pending' ? 'text-yellow-600' : 'text-red-600'}">${booking.payment_status.toUpperCase()}</span></td>
                    <td class="flex space-x-2">
                        <button class="form-button bg-blue-500 hover:bg-blue-600 px-3 py-1 text-sm" onclick="openUpdateBookingStatusModal('${booking.id}', '${booking.booking_status}')">Update Status</button>
                    </td>
                `;
            });
        }

        async function openUpdateBookingStatusModal(bookingId, currentStatus) {
            openModal('updateBookingStatusModal');
            document.getElementById('update-booking-id').value = bookingId;
            document.getElementById('booking-current-status').value = currentStatus.toUpperCase();
            document.getElementById('new-booking-status').value = currentStatus; // Set default to current
            document.getElementById('update-booking-status-message-box').classList.add('hidden');
        }

        updateBookingStatusForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const bookingId = document.getElementById('update-booking-id').value;
            const newStatus = document.getElementById('new-booking-status').value;

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/bookings/${bookingId}/status`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();
                if (response.ok) {
                    showMessage('Booking status updated successfully!', 'success', 'update-booking-status-message-box');
                    closeModal('updateBookingStatusModal');
                    fetchAllBookings();
                } else {
                    showMessage(`Failed to update booking status: ${data.error || response.statusText}`, 'error', 'update-booking-status-message-box');
                }
            } catch (error) {
                console.error('Error updating booking status:', error);
                showMessage('An error occurred while updating booking status. Please try again.', 'error', 'update-booking-status-message-box');
            }
        });

        // Report Generation Functions
        const reportForm = document.getElementById('report-form');
        const reportResultsDiv = document.getElementById('report-results');
        const reportOutputPre = document.getElementById('report-output');

        reportForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const reportType = document.getElementById('report-type').value;
            const startDate = document.getElementById('report-start-date').value;
            const endDate = document.getElementById('report-end-date').value;

            const queryParams = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });

            try {
                const token = getAuthToken();
                const response = await fetch(`${API_BASE_URL}/admin/reports/${reportType}?${queryParams.toString()}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    reportOutputPre.textContent = JSON.stringify(data, null, 2);
                    reportResultsDiv.classList.remove('hidden');
                    showMessage('Report generated successfully!', 'success', 'report-message-box');
                } else {
                    reportOutputPre.textContent = `Error: ${data.error || response.statusText}`;
                    reportResultsDiv.classList.remove('hidden');
                    showMessage(`Failed to generate report: ${data.error || response.statusText}`, 'error', 'report-message-box');
                }
            } catch (error) {
                console.error('Error generating report:', error);
                reportOutputPre.textContent = 'An unexpected error occurred.';
                reportResultsDiv.classList.remove('hidden');
                showMessage('An error occurred while generating the report. Please try again.', 'error', 'report-message-box');
            }
        });

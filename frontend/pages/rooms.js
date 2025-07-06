 const API_BASE_URL = 'http://localhost:5000';

        function getAuthToken() {
            return localStorage.getItem('jwt_token');
        }

        function removeAuthToken() {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_role');
        }

        function showMessage(message, type = 'info', targetId = 'rooms-message-box') {
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
        });

        // Specific JavaScript for rooms.html
        const roomSearchForm = document.getElementById('room-search-form');
        const roomResultsDiv = document.getElementById('room-results');

        roomSearchForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const checkInDate = document.getElementById('check-in-date').value;
            const checkOutDate = document.getElementById('check-out-date').value;
            const guests = document.getElementById('guests').value;
            const roomType = document.getElementById('room-type').value;
            const minPrice = document.getElementById('min-price').value;
            const maxPrice = document.getElementById('max-price').value;

            const queryParams = new URLSearchParams({
                check_in: checkInDate,
                check_out: checkOutDate,
                guests: guests
            });
            if (roomType) queryParams.append('room_type', roomType);
            if (minPrice) queryParams.append('min_price', minPrice);
            if (maxPrice) queryParams.append('max_price', maxPrice);

            try {
                const response = await fetch(`${API_BASE_URL}/rooms?${queryParams.toString()}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${getAuthToken()}` // Rooms search might be public or require token
                    }
                });

                const data = await response.json();
                if (response.ok) {
                    displayRoomResults(data);
                    if (data.length === 0) {
                        showMessage('No rooms found matching your criteria.', 'info');
                    } else {
                        showMessage(`Found ${data.length} rooms.`, 'success');
                    }
                } else {
                    showMessage(`Error searching rooms: ${data.error || response.statusText}`, 'error');
                    roomResultsDiv.innerHTML = `<p class="text-center text-red-500 col-span-full">Error: ${data.error || 'Failed to load rooms.'}</p>`;
                }
            } catch (error) {
                console.error('Error fetching rooms:', error);
                showMessage('An error occurred while searching for rooms. Please try again.', 'error');
                roomResultsDiv.innerHTML = `<p class="text-center text-red-500 col-span-full">An unexpected error occurred.</p>`;
            }
        });

        function displayRoomResults(rooms) {
            roomResultsDiv.innerHTML = ''; // Clear previous results
            if (rooms.length === 0) {
                roomResultsDiv.innerHTML = '<p class="text-center text-gray-500 col-span-full">No rooms found.</p>';
                return;
            }

            rooms.forEach(room => {
                const roomCard = document.createElement('div');
                roomCard.className = 'bg-white rounded-lg shadow-md p-6 flex flex-col';
                roomCard.innerHTML = `
                    ${room.images && room.images.length > 0 ? `<img src="${room.images[0]}" alt="${room.room_type} Room" class="w-full h-48 object-cover rounded-md mb-4 onerror="this.onerror=null;this.src='https://placehold.co/600x400/cccccc/333333?text=No+Image';"">` : `<img src="https://placehold.co/600x400/cccccc/333333?text=No+Image" alt="No Image" class="w-full h-48 object-cover rounded-md mb-4">`}
                    <h4 class="text-xl font-semibold text-gray-800 mb-2">${room.room_type.charAt(0).toUpperCase() + room.room_type.slice(1)} Room - #${room.room_number}</h4>
                    <p class="text-gray-600 text-sm mb-2">${room.description || 'No description available.'}</p>
                    <p class="text-gray-700 font-medium mb-1">Capacity: ${room.capacity} guests</p>
                    <p class="text-gray-700 font-medium mb-1">Price per night: $${room.price_per_night}</p>
                    <p class="text-gray-700 font-bold text-lg mb-4">Estimated Total: $${room.estimated_total_price}</p>
                    <button class="form-button mt-auto" onclick="viewRoomDetails('${room.id}')">View Details</button>
                `;
                roomResultsDiv.appendChild(roomCard);
            });
        }

        async function viewRoomDetails(roomId) {
            // This would typically open a modal or navigate to a dedicated room detail page
            // For now, let's just fetch and log the details, or show a simple alert/message.
            try {
                const response = await fetch(`${API_BASE_URL}/rooms/${roomId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${getAuthToken()}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    let details = `Room Number: ${data.room_number}\n`;
                    details += `Type: ${data.room_type}\n`;
                    details += `Capacity: ${data.capacity}\n`;
                    details += `Price: $${data.price_per_night} / night\n`;
                    details += `Description: ${data.description}\n`;
                    details += `Amenities: ${data.amenities ? data.amenities.join(', ') : 'None'}\n`;
                    details += `Status: ${data.status}\n`;
                    showMessage(`Room Details:\n${details}`, 'info');
                    // In a real app, you'd render this in a nice modal
                } else {
                    showMessage(`Failed to load room details: ${data.error || response.statusText}`, 'error');
                }
            } catch (error) {
                console.error('Error fetching room details:', error);
                showMessage('An error occurred while fetching room details.', 'error');
            }
        }

        // Pre-fill dates for convenience
        document.addEventListener('DOMContentLoaded', () => {
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(today.getDate() + 1);

            const formatDate = (date) => date.toISOString().split('T')[0];

            document.getElementById('check-in-date').value = formatDate(today);
            document.getElementById('check-out-date').value = formatDate(tomorrow);
        });
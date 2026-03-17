const API_BASE_URL = 'http://localhost:5000'; // Ensure this points to your Flask port

document.addEventListener('DOMContentLoaded', () => {
    
    // Fetch rooms from the database
    fetch(`${API_BASE_URL}/api/rooms`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(rooms => {
            // Use the container ID from your Tailwind HTML layout
            const roomShowcaseContainer = document.getElementById('roomShowcaseContainer') || document.getElementById('room-container');
            
            if (!roomShowcaseContainer) {
                console.error("Room container not found in HTML.");
                return;
            }

            // Clear the loading spinner
            roomShowcaseContainer.innerHTML = ''; 

            // Loop over the database results correctly
            rooms.forEach((room, index) => {
                const roomSection = document.createElement('div');
                roomSection.className = `room-section ${index % 2 !== 0 ? 'reverse-layout' : ''}`;

                // Safely handle missing images
                const imageUrl = (room.images && room.images.length > 0) ? room.images[0] : './images/hero-luxury-hotel-modern.jpg';
                
                // Safely parse JSON amenities from the backend
                let featuresHtml = '';
                if (room.amenities && Array.isArray(room.amenities)) {
                    featuresHtml = room.amenities.map(feature => `<li><i class="fa-solid fa-check"></i> ${feature}</li>`).join('');
                } else {
                    featuresHtml = `<li><i class="fa-solid fa-check"></i> Standard Amenities</li>`;
                }

                // Inject the dynamic HTML into the newly created element
                roomSection.innerHTML = `
                    <div class="room-image-area">
                        <img src="${imageUrl}" alt="${room.room_type}">
                    </div>
                    <div class="room-details-area">
                        <h2 class="room-title">${String(room.room_type).toUpperCase()} - Room ${room.room_number}</h2>
                        <p class="room-description">${room.description || 'Experience comfort in our premium rooms.'}</p>
                        <ul class="room-features">
                            ${featuresHtml}
                        </ul>
                        <div class="room-price-info">
                            <span class="price-from">Starting from</span>
                            <span class="price-value">$${room.price_per_night}</span>
                            <span class="price-per-night">/ night</span>
                        </div>
                        <button class="btn btn-primary room-btn" onclick="bookRoom('${room.id}', '${room.room_number}')">
                            <i class="fa-solid fa-circle-info"></i> Book Now
                        </button>
                    </div>
                `;

                // Append the correctly populated element to the container
                roomShowcaseContainer.appendChild(roomSection);
            });
        })
        .catch(error => {
            console.error('Error fetching room data:', error);
            const roomShowcaseContainer = document.getElementById('roomShowcaseContainer') || document.getElementById('room-container');
            if (roomShowcaseContainer) {
                roomShowcaseContainer.innerHTML = '<p style="color:red; text-align:center; padding:20px;">Error loading rooms from the database. Make sure the backend server is running.</p>';
            }
        }); 

        const selectedRoomId = localStorage.getItem('selected_room_id');
        if (selectedRoomId) {
            const roomInput = document.getElementById('create-room-id'); 
            if (roomInput) {
                roomInput.value = selectedRoomId;
                // Highlight it briefly so the user knows it auto-filled
                roomInput.classList.add('ring-2', 'ring-green-500');
                setTimeout(() => roomInput.classList.remove('ring-2', 'ring-green-500'), 2000);
                
                // Clear it from storage so it doesn't stick forever
                localStorage.removeItem('selected_room_id');
            }
        }
    // Navigation active state logic
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') && link.getAttribute('href').endsWith(currentPage || '')) {
             if (currentPage === 'roomsPage.html' || currentPage === '') { 
                 link.classList.add('active');
             }
        }
    });
});

// Book room function
function bookRoom(roomId, roomNumber) {
    // Save the ID to local storage so bookings.html knows which room the user clicked
    localStorage.setItem('selected_room_id', roomId);
    if (confirm(`Do you want to proceed to book Room ${roomNumber}?`)) {
        window.location.href = 'bookings.html';
    }
}
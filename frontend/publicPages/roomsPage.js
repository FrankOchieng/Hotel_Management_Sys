  // Room data
        const rooms = [
            {
                id: 1,
                name: 'Deluxe Suite',
                price: '$299',
                features: ['King Bed', 'Ocean View', 'Private Balcony', 'Mini Bar'],
                description: 'Spacious suite with breathtaking ocean views and premium amenities.'
            },
            {
                id: 2,
                name: 'Presidential Suite',
                price: '$599',
                features: ['Master Bedroom', 'Living Room', 'Jacuzzi', 'Butler Service'],
                description: 'Our most luxurious accommodation with personalized butler service.'
            },
            {
                id: 3,
                name: 'Garden Villa',
                price: '$399',
                features: ['Private Garden', 'Outdoor Shower', 'Fireplace', 'Kitchenette'],
                description: 'Intimate villa surrounded by lush gardens and natural beauty.'
            },
            {
                id: 4,
                name: 'Penthouse',
                price: '$799',
                features: ['Rooftop Terrace', 'Private Pool', 'City Views', 'Concierge Service'],
                description: 'Ultimate luxury with panoramic city views and exclusive amenities.'
            }
        ];

        // Render rooms
        function renderRooms() {
            const roomsGrid = document.getElementById('roomsGrid');
            
            rooms.forEach(room => {
                const roomCard = document.createElement('div');
                roomCard.className = 'room-card';
                
                roomCard.innerHTML = `
                    <div class="room-image">🏨</div>
                    <div class="room-content">
                        <div class="room-header">
                            <h3 class="room-name">${room.name}</h3>
                            <div>
                                <span class="room-price">${room.price}</span>
                                <span class="price-note">/night</span>
                            </div>
                        </div>
                        <p class="room-description">${room.description}</p>
                        <div class="room-features">
                            <h4 class="features-title">Features:</h4>
                            <div class="features-grid">
                                ${room.features.map(feature => `
                                    <div class="feature-item">
                                        <span class="feature-dot"></span>
                                        ${feature}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <button class="book-btn" onclick="bookRoom('${room.name}')">Book Now</button>
                    </div>
                `;
                
                roomsGrid.appendChild(roomCard);
            });
        }

        // Book room function
        function bookRoom(roomName) {
            alert(`Booking request for ${roomName} - Redirecting to booking system...`);
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            renderRooms();
            
            // Navigation active state
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const navLinks = document.querySelectorAll('.nav-links a');
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === currentPage) {
                    link.classList.add('active');
                }
            });
        });
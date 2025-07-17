
  // Room data
        /*
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
        
document.addEventListener('DOMContentLoaded', () => {
    // Room data
    const rooms = [
        {
            id: 1,
            name: 'Presidential Suite',
            price: '$950', // Match previous CSS example price
            perNight: '/ night',
            image: './images/Presidential-Suite-Master-Bedroom.jpg', // Path to your image
            features: [
                { icon: 'fa-bed', text: 'King Bed' },
                { icon: 'fa-users', text: '4 Guests' },
                { icon: 'fa-bath', text: 'Jacuzzi & Rain Shower' },
                { icon: 'fa-car', text: 'Valet Parking' }
            ],
            description: 'Indulge in unparalleled luxury within our grand Presidential Suite, offering panoramic city views, a private living area, and bespoke services. Designed for ultimate comfort and sophistication.'
        },
        {
            id: 2,
            name: 'Executive Deluxe Room',
            price: '$420',
            perNight: '/ night',
            image: './images/deluxe3.jpg',
            features: [
                { icon: 'fa-bed', text: 'Queen Bed' },
                { icon: 'fa-users', text: '2 Guests' },
                { icon: 'fa-wifi', text: 'High-Speed Wi-Fi' },
                { icon: 'fa-mug-hot', text: 'Complimentary Coffee' }
            ],
            description: 'Perfect for business or leisure, our Executive Deluxe Room blends modern amenities with classic comfort. Enjoy ergonomic workspaces, high-speed Wi-Fi, and serene garden views.'
        },
        {
            id: 3,
            name: 'Grand Ocean View',
            price: '$680',
            perNight: '/ night',
            image: './images/oceanView2.jpg',
            features: [
                { icon: 'fa-bed', text: 'King Bed' },
                { icon: 'fa-users', text: '2 Guests' },
                { icon: 'fa-water', text: 'Oceanfront Balcony' },
                { icon: 'fa-umbrella-beach', text: 'Beach Access' }
            ],
            description: 'Awaken to the soothing sounds of waves in our Grand Ocean View room. Featuring a private balcony, a spacious layout, and direct beach access for an unforgettable coastal escape.'
        },
        {
            id: 4,
            name: 'Family Interconnecting Suite',
            price: '$790',
            perNight: '/ night',
            image: './images/family2.jpg',
            features: [
                { icon: 'fa-bed', text: 'King & Twin Beds' },
                { icon: 'fa-users-line', text: '6 Guests' },
                { icon: 'fa-toy-dinosaur', text: 'Kids Play Area' },
                { icon: 'fa-kitchen-set', text: 'Mini Kitchenette' }
            ],
            description: 'Designed for families, this spacious suite offers two interconnecting rooms, ensuring privacy for adults and fun for kids. Enjoy ample space and tailored amenities for all ages.'
        },
        {
            id: 5,
            name: 'Penthouse Loft',
            price: '$1200',
            perNight: '/ night',
            image: './images/pentHouse4.jpg',
            features: [
                { icon: 'fa-bed', text: 'Super King Bed' },
                { icon: 'fa-users', text: '2 Guests' },
                { icon: 'fa-building', text: 'Rooftop Terrace' },
                { icon: 'fa-bell-concierge', text: 'Concierge Service' }
            ],
            description: 'Experience elevated living in our Penthouse Loft. A split-level design with a grand living space, private terrace, and personalized concierge service for an exclusive retreat.'
        }

            */
           fetch('/api/rooms')
            .then(response => response.json())
            .then(rooms => {
                const roomContainer = document.getElementById('room-container');
                data.forEach(room => {
                    const roomElement = document.createElement('div');
                    roomContainer.innerHTML = `
                    <h2>${room.name}</h2>
                    <p>${room.description}</p>
                    <p>Price: ${room.price} ${room.perNight}</p>
                    <img src="${room.image}" alt="${room.name}">
                    <ul>
                        ${room.features.map(feature => `<li><i class="fa-solid ${feature.icon}"></i> ${feature.text}</li>`).join('')}
                    </ul>
                    <button class="btn btn-primary" onclick="bookRoom('${room.name}')">Book Now</button>
                    `;
                    roomContainer.appendChild(roomElement);
                });
            })
            .catch(error => {
                console.error('Error fetching room data:', error);
                const roomContainer = document.getElementById('room-container');
                roomContainer.innerHTML = '<p>Error loading room data. Please try again later.</p>';
            }); 

    // Render rooms
    function renderRooms() {
        const roomShowcaseContainer = document.getElementById('roomShowcaseContainer');
        if (!roomShowcaseContainer) {
            console.error("Element with ID 'roomShowcaseContainer' not found.");
            return;
        }

        rooms.forEach((room, index) => {
            const roomSection = document.createElement('div');
            // Add 'reverse-layout' class for every second room (index 1, 3, 5, etc.)
            roomSection.className = `room-section ${index % 2 !== 0 ? 'reverse-layout' : ''}`;

            roomSection.innerHTML = `
                <div class="room-image-area">
                    <img src="${room.image}" alt="${room.name}">
                </div>
                <div class="room-details-area">
                    <h2 class="room-title">${room.name}</h2>
                    <p class="room-description">${room.description}</p>
                    <ul class="room-features">
                        ${room.features.map(feature => `
                            <li><i class="fa-solid ${feature.icon}"></i> ${feature.text}</li>
                        `).join('')}
                    </ul>
                    <div class="room-price-info">
                        <span class="price-from">Starting from</span>
                        <span class="price-value">${room.price}</span>
                        <span class="price-per-night">${room.perNight}</span>
                    </div>
                    <a href="#" class="btn btn-primary room-btn" onclick="bookRoom('${room.name}')">
                        <i class="fa-solid fa-circle-info"></i> View Details & Book
                    </a>
                </div>
            `;

            roomShowcaseContainer.appendChild(roomSection);
        });
    }
        // Book room function
        function bookRoom(roomName) {
            alert(`Booking request for ${roomName} - Redirecting to booking system...`);
            if (confirm('Do you want to proceed to the booking page?')) {
                window.location.href = 'bookings.html'; // Redirect to booking page
            }
        }

    // Initialize page
    // Using a single DOMContentLoaded listener for all page-specific initializations
    // This is more robust and standard practice.
    renderRooms();

    // Navigation active state (from your original snippet, assumes it's for this page only)
    // If this logic is global (e.g., in homepage.js), remove it from here to avoid duplication.
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        link.classList.remove('active');
        // Check if the link's href matches the current page, or if it's roomsPage.html
        if (link.getAttribute('href') && link.getAttribute('href').endsWith(currentPage || '')) {
             if (currentPage === 'roomsPage.html' || currentPage === '') { // Handles root path too if roomsPage is default
                 link.classList.add('active');
             }
        }
        // Specific handling for roomsPage.html in case path manipulation is tricky
        if (link.getAttribute('href') === 'roomsPage.html' && currentPage.includes('roomsPage.html')) {
             link.classList.add('active');
        }
    });

    console.log("Rooms Page JS Loaded and Rooms Rendered.");

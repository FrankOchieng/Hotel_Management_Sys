document.addEventListener('DOMContentLoaded', function() {
    // Array to hold your service data
    const services = [
        {
            iconClass: 'fas fa-concierge-bell',
            title: '24/7 Concierge Service',
            description: 'Our dedicated concierge team is available around the clock to assist with any request, from dining reservations to bespoke experiences.',
            link: '#'
        },
        {
            iconClass: 'fas fa-utensils',
            title: 'Gourmet Dining & Room Service',
            description: 'Savor exquisite culinary delights at our signature restaurants or enjoy a gourmet meal delivered to the comfort of your room, anytime.',
            link: '#'
        },
        {
            iconClass: 'fas fa-spa',
            title: 'Luxurious Spa & Wellness',
            description: 'Indulge in a world of relaxation and rejuvenation with our extensive spa treatments, saunas, and personalized wellness programs.',
            link: '#'
        },
        {
            iconClass: 'fas fa-dumbbell',
            title: 'State-of-the-Art Fitness Center',
            description: 'Maintain your routine in our modern fitness center, equipped with the latest machines and offering personal training sessions.',
            link: '#'
        },
        {
            iconClass: 'fas fa-car-side',
            title: 'Premium Valet & Parking',
            description: 'Enjoy seamless arrivals and departures with our complimentary valet parking, ensuring convenience throughout your stay.',
            link: '#'
        },
        {
            iconClass: 'fas fa-plane-departure',
            title: 'Exclusive Airport Transfers',
            description: 'Travel in ultimate comfort with our luxury airport transfer service, available for stress-free journeys to and from the hotel.',
            link: '#'
        },
        {
            iconClass: 'fas fa-wifi',
            title: 'High-Speed Wi-Fi Access',
            description: 'Stay connected with complimentary high-speed Wi-Fi available throughout the hotel, perfect for business or leisure.',
            link: '#'
        },
        {
            iconClass: 'fas fa-child',
            title: 'Kids Club & Activities',
            description: 'Our supervised Kids Club offers a vibrant array of activities and entertainment, ensuring a fun and engaging experience for younger guests.',
            link: '#'
        }
    ];

    const servicesGrid = document.getElementById('servicesGrid');

    // Check if the servicesGrid element exists to prevent errors
    if (servicesGrid) {
        // Loop through the services array and create HTML for each
        services.forEach(service => {
            const serviceCardHTML = `
                <div class="service-card">
                    <div class="service-icon-wrapper">
                        <i class="${service.iconClass} service-icon"></i>
                    </div>
                    <h3 class="service-title">${service.title}</h3>
                    <p class="service-description">${service.description}</p>
                    <a href="${service.link}" class="btn btn-secondary learn-more-btn">Learn More <i class="fas fa-arrow-right"></i></a>
                </div>
            `;
            servicesGrid.insertAdjacentHTML('beforeend', serviceCardHTML);
        });
    } else {
        console.error('Element with ID "servicesGrid" not found. Services cannot be populated.');
    }
});
 // Services data
        const services = [
            {
                id: 1,
                title: 'Spa & Wellness',
                description: 'Rejuvenate your body and soul with our premium spa treatments and wellness programs.',
                icon: '🧘',
                features: ['Massage Therapy', 'Facial Treatments', 'Aromatherapy', 'Yoga Classes']
            },
            {
                id: 2,
                title: 'Fine Dining',
                description: 'Experience culinary excellence with our world-class restaurants and room service.',
                icon: '🍽️',
                features: ['Michelin Star Restaurant', '24/7 Room Service', 'Wine Cellar', 'Private Chef']
            },
            {
                id: 3,
                title: 'Concierge Services',
                description: 'Let our dedicated concierge team handle all your needs and special requests.',
                icon: '🎩',
                features: ['Travel Planning', 'Event Tickets', 'Transportation', 'Personal Shopping']
            },
            {
                id: 4,
                title: 'Business Center',
                description: 'State-of-the-art facilities for all your business and conference needs.',
                icon: '💼',
                features: ['Meeting Rooms', 'Video Conferencing', 'Business Lounge', 'Secretary Services']
            },
            {
                id: 5,
                title: 'Recreation & Entertainment',
                description: 'Enjoy our premium recreational facilities and entertainment options.',
                icon: '🏊',
                features: ['Swimming Pool', 'Fitness Center', 'Tennis Court', 'Live Entertainment']
            },
            {
                id: 6,
                title: 'VIP Services',
                description: 'Exclusive services for our most distinguished guests.',
                icon: '👑',
                features: ['Airport Transfers', 'Butler Service', 'Private Events', 'Helicopter Tours']
            }
        ];

        // Render services
        function renderServices() {
            const servicesGrid = document.getElementById('servicesGrid');
            
            services.forEach(service => {
                const serviceCard = document.createElement('div');
                serviceCard.className = 'service-card';
                
                serviceCard.innerHTML = `
                    <span class="service-icon">${service.icon}</span>
                    <h3 class="service-title">${service.title}</h3>
                    <p class="service-description">${service.description}</p>
                    <ul class="service-features">
                        ${service.features.map(feature => `
                            <li>
                                <span class="feature-dot"></span>
                                ${feature}
                            </li>
                        `).join('')}
                    </ul>
                    <button class="learn-more-btn" onclick="learnMore('${service.title}')">Learn More</button>
                `;
                
                servicesGrid.appendChild(serviceCard);
            });
        }

        // Learn more function
        function learnMore(serviceTitle) {
            alert(`More information about ${serviceTitle} - Contact our concierge for details!`);
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            renderServices();
            
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
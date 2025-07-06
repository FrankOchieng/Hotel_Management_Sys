  // Common JavaScript for navigation and logout
        const API_BASE_URL = 'http://localhost:5000';

        function getAuthToken() {
            return localStorage.getItem('jwt_token');
        }

        function removeAuthToken() {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_role');
        }

        function showMessage(message, type = 'info', targetId = 'services-message-box') {
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

            fetchServices(); // Fetch services when the page loads
        });

        // Specific JavaScript for services.html
        const servicesListDiv = document.getElementById('services-list');

        async function fetchServices() {
            servicesListDiv.innerHTML = '<p class="text-center text-gray-500 col-span-full">Loading services...</p>';
            try {
                const token = getAuthToken();
                // Services might be public, but if restricted, add Authorization header
                const headers = { 'Content-Type': 'application/json' };
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`;
                }

                const response = await fetch(`${API_BASE_URL}/services`, {
                    method: 'GET',
                    headers: headers
                });

                const data = await response.json();
                if (response.ok) {
                    displayServices(data);
                    if (data.length === 0) {
                        showMessage('No services found.', 'info');
                    } else {
                        showMessage(`Found ${data.length} services.`, 'success');
                    }
                } else {
                    showMessage(`Error fetching services: ${data.error || response.statusText}`, 'error');
                    servicesListDiv.innerHTML = `<p class="text-center text-red-500 col-span-full">Error: ${data.error || 'Failed to load services.'}</p>`;
                }
            } catch (error) {
                console.error('Error fetching services:', error);
                showMessage('An error occurred while fetching services. Please try again.', 'error');
                servicesListDiv.innerHTML = `<p class="text-center text-red-500 col-span-full">An unexpected error occurred.</p>`;
            }
        }

        function displayServices(services) {
            servicesListDiv.innerHTML = ''; // Clear previous results
            if (services.length === 0) {
                servicesListDiv.innerHTML = '<p class="text-center text-gray-500 col-span-full">No services available.</p>';
                return;
            }

            // Group services by category
            const servicesByCategory = services.reduce((acc, service) => {
                const category = service.category.charAt(0).toUpperCase() + service.category.slice(1);
                if (!acc[category]) {
                    acc[category] = [];
                }
                acc[category].push(service);
                return acc;
            }, {});

            for (const category in servicesByCategory) {
                const categorySection = document.createElement('div');
                categorySection.className = 'col-span-full mb-4';
                categorySection.innerHTML = `<h3 class="text-2xl font-semibold text-gray-800 mb-4">${category} Services</h3>`;
                servicesListDiv.appendChild(categorySection);

                const categoryServicesGrid = document.createElement('div');
                categoryServicesGrid.className = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 col-span-full';
                servicesByCategory[category].forEach(service => {
                    const serviceCard = document.createElement('div');
                    serviceCard.className = 'service-card flex flex-col';
                    serviceCard.innerHTML = `
                        <h4 class="text-lg font-semibold text-gray-800 mb-2">${service.name}</h4>
                        <p class="text-gray-600 text-sm mb-2">${service.description || 'No description available.'}</p>
                        <p class="text-gray-700 font-medium mb-1">Price: $${service.price}</p>
                        <p class="text-gray-700 font-medium ${service.availability ? 'text-green-600' : 'text-red-600'}">
                            Availability: ${service.availability ? 'Available' : 'Unavailable'}
                        </p>
                    `;
                    categoryServicesGrid.appendChild(serviceCard);
                });
                servicesListDiv.appendChild(categoryServicesGrid);
            }
        }
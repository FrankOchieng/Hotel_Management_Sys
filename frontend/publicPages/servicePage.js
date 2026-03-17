const API_BASE_URL = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', () => {
    const servicesGrid = document.getElementById('servicesGrid');

    if (!servicesGrid) return;

    // --- NEW: Tailwind Responsive Grid Classes ---
    // grid-cols-1 = Mobile (1 column)
    // md:grid-cols-2 = Tablet (2 columns)
    // lg:grid-cols-3 = Laptop/Desktop (3 columns)
    servicesGrid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-8';

    fetch(`${API_BASE_URL}/services`)
        .then(res => {
            if (!res.ok) throw new Error("Failed to fetch");
            return res.json();
        })
        .then(services => {
            servicesGrid.innerHTML = ''; 

            if (services.length === 0) {
                servicesGrid.innerHTML = '<p class="text-gray-500 text-center col-span-full">No services available right now.</p>';
                return;
            }

            services.forEach(service => {
                const card = document.createElement('div');
                // Removed the old padding from the wrapper so the image goes edge-to-edge
                card.className = 'bg-white rounded-xl shadow-lg border border-gray-100 flex flex-col h-full overflow-hidden hover:shadow-xl transition-shadow duration-300';
                
                // Fallback image in case the database doesn't have one
                const imageUrl = service.image_url || './images/deluxe2.jpeg';

                card.innerHTML = `
                    <img src="${imageUrl}" alt="${service.name}" class="w-full h-48 object-cover">
                    
                    <div class="p-6 flex flex-col flex-grow">
                        <div class="mb-3 flex justify-between items-center">
                            <span class="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full uppercase tracking-wide font-bold">${service.category}</span>
                        </div>
                        <h3 class="text-xl font-bold text-gray-900 mb-2">${service.name}</h3>
                        <p class="text-gray-600 mb-6 flex-grow text-sm leading-relaxed">${service.description || 'Experience our premium amenities.'}</p>
                        
                        <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-100">
                            <span class="text-2xl font-black text-gray-900">$${service.price}</span>
                            <button onclick="bookService('${service.id}', '${service.name}')" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm">
                                Book Service
                            </button>
                        </div>
                    </div>
                `;
                servicesGrid.appendChild(card);
            });
        })
        .catch(err => {
            console.error(err);
            servicesGrid.innerHTML = '<p class="text-red-500 text-center col-span-full py-10">Failed to load services. Please check connection.</p>';
        });
});

function bookService(id, name) {
    if(confirm(`Would you like to head to the bookings page to add "${name}" to your stay?`)) {
        localStorage.setItem('selected_service_id', id);
        window.location.href = 'bookings.html';
    }
}
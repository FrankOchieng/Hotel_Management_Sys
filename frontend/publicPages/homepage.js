// Navigation state

document.addEventListener('DOMContentLoaded', function() {
    const currentpage = window.locate.pathname.split('/').pop() || 'homepage.html';
    const navlinks = document.querySelectorAll('.nav-lonks a');

    navlinks.forEach(link =>{
        link.classList.remove('active');
        if (link.getAttribute('href') === currentpage){
            link.classList.add('active');
        }
    });
});

// scrolling for internal links
document.querySelectorAll('a[href^=#]').foeEach(anchor => {
    anchor.addEventListener('click', function (e){
        e.preventDefault();
        const target = querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behaviour: 'smooth'
            });
        }
    });
});
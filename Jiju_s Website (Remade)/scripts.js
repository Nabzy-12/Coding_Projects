document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed'); // Debugging statement

    // Smooth scrolling for navigation links
    document.querySelectorAll('nav ul li a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            console.log(`Navigating to ${this.getAttribute('href')}`); // Debugging statement
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Back to Top button functionality
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        console.log('Back to Top button found'); // Debugging statement

        window.addEventListener('scroll', function () {
            console.log(`Window scrolled to ${window.scrollY}px`); // Debugging statement
            if (window.scrollY > 200) { // Show button after scrolling down 200px
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });

        backToTopButton.addEventListener('click', function () {
            console.log('Back to Top button clicked'); // Debugging statement
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    } else {
        console.error('Back to Top button not found'); // Debugging statement
    }

    // Sticky header functionality
    const header = document.querySelector('header');
    const topHeaderHeight = document.querySelector('.top-header').offsetHeight;
    if (header) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > topHeaderHeight) {
                header.classList.add('sticky');
            } else {
                header.classList.remove('sticky');
            }
        });
    } else {
        console.error('Header not found'); // Debugging statement
    }
});
// Simple JavaScript functionality for the file directory website

document.addEventListener('DOMContentLoaded', function() {
    // Search form validation
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    // Mobile-friendly category navigation
    const categoryNav = document.querySelector('.categories');
    if (categoryNav) {
        // Add active class to current category
        const currentPath = window.location.pathname;
        const categoryLinks = categoryNav.querySelectorAll('a');
        
        categoryLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    // Add click event for table rows to navigate to file details
    const fileTableRows = document.querySelectorAll('.file-table tbody tr');
    fileTableRows.forEach(row => {
        const fileLink = row.querySelector('.name-column a');
        if (fileLink) {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function(e) {
                // Don't trigger if they clicked on a link or button directly
                if (e.target.tagName.toLowerCase() !== 'a' && e.target.tagName.toLowerCase() !== 'button') {
                    window.location.href = fileLink.getAttribute('href');
                }
            });
        }
    });

    // Add tooltips for truncated text
    const truncatedElements = document.querySelectorAll('.truncate');
    truncatedElements.forEach(el => {
        if (el.scrollWidth > el.clientWidth) {
            el.title = el.textContent;
        }
    });
});

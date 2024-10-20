// Favorite and  last read toggle event listeners
document.addEventListener('click', function(e) {
    if (e.target.closest('.favorite-btn')) {
        const btn = e.target.closest('.favorite-btn');
        const annotationId = btn.dataset.annotationId;
        const isFavorite = btn.dataset.isFavorite === 'true';

        if (confirm("Are you sure you want to " + (isFavorite ? "unfavorite" : "favorite") + " this annotation?")) {
            fetch(`/toggle_favorite/${annotationId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        btn.dataset.isFavorite = (!isFavorite).toString();
                        btn.querySelector('svg').style.fill = isFavorite ? 'none' : 'currentColor';
                    }
                });
        }
    }

    if (e.target.closest('.last-read-btn')) {
        const btn = e.target.closest('.last-read-btn');
        const annotationId = btn.dataset.annotationId;

        fetch(`/update_last_read/${annotationId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const date = new Date(data.new_timestamp * 1000);
                    const formattedDate = date.toISOString().slice(0, 19).replace('T', ' ');
                    btn.querySelector('.last-read').textContent = formattedDate;
                }
            });
    }
});

function toggleChapterName(element) {
    const chapterName = element.previousElementSibling;
    chapterName.classList.toggle('hidden');
}

function toggleFilter(filterType) {
    fetch(`/toggle_filter/${filterType}`, { method: 'GET' })
        .then(response => {
            if (response.ok) { location.reload(); }
        })
        .catch(error => console.error('Error:', error));
}




// Filter dropdown
//////////////////
document.addEventListener('DOMContentLoaded', function() {
    const filterButton = document.getElementById('filter-menu-button');
    const filterMenu = document.getElementById('filter-menu');
    const applyFiltersButton = document.getElementById('apply-filters');
  
    filterButton.addEventListener('click', function() {
      filterMenu.classList.toggle('hidden');
    });
  
    applyFiltersButton.addEventListener('click', function() {
      const readFilter = document.querySelector('input[name="read_filter"]:checked').value;
      const favoriteFilter = document.querySelector('input[name="favorite_filter"]:checked').value;
  
      applyFilters(readFilter, favoriteFilter);
    });
  
    // Close the dropdown when clicking outside of it
    document.addEventListener('click', function(event) {
      if (!filterButton.contains(event.target) && !filterMenu.contains(event.target)) {
        filterMenu.classList.add('hidden');
      }
    });
  });
  
  function applyFilters(readFilter, favoriteFilter) {
    const params = new URLSearchParams();
    params.append('read_filter', readFilter);
    params.append('favorite_filter', favoriteFilter);
  
    fetch('/apply_filters?' + params.toString(), { method: 'GET' })
      .then(response => {
        if (response.ok) { 
          location.reload();
        }
      })
      .catch(error => console.error('Error:', error));
  }








// Highlight navigation buttons
///////////////////////////////

// Get all highlight elements
const highlights = document.querySelectorAll('.highlight');
let currentHighlightIndex = -1;

// Add event listeners to buttons
document.getElementById('prevHighlight').addEventListener('click', () => navigateHighlights('prev'));
document.getElementById('nextHighlight').addEventListener('click', () => navigateHighlights('next'));

function navigateHighlights(direction) {
  if (highlights.length === 0) return;

  // Remove outline from the previous highlight
  if (currentHighlightIndex >= 0) {
    highlights[currentHighlightIndex].classList.remove('highlight-current');
  }

  if (direction === 'next') {
    currentHighlightIndex = (currentHighlightIndex + 1) % highlights.length;
  } else {
    currentHighlightIndex = (currentHighlightIndex - 1 + highlights.length) % highlights.length;
  }

  const currentHighlight = highlights[currentHighlightIndex];

  // Add outline to the current highlight
  currentHighlight.classList.add('highlight-current');

  // Scroll to the current highlight
  const rect = currentHighlight.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

  window.scrollTo({
    top: rect.top + scrollTop - 80, // padding from the top
    behavior: 'smooth'
  });
}

// Optional: Keyboard navigation
document.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowUp') {
    event.preventDefault();
    navigateHighlights('prev');
  } else if (event.key === 'ArrowDown') {
    event.preventDefault();
    navigateHighlights('next');
  }
});

// Add CSS for highlight outline animation
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeOutline {
    0% { outline-color: rgba(99, 102, 241, 0); }
    50% { outline-color: rgba(99, 102, 241, 1); }
    100% { outline-color: rgba(99, 102, 241, 0.3); }
  }
  .highlight-current {
    outline: 2px solid rgba(99, 102, 241, 0.3);
    outline-offset: 0px;
    //outline-style: dashed;
    animation: fadeOutline 1s ease-in-out;
    background-color: rgba(99, 102, 241, 0.1);
  }
`;
document.head.appendChild(style);

// END Navigation between highlights
////////////////////////////////////
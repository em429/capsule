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

// Toggle a url param value between true/false, can be used for any named parameter
function toggleFilter(filterType) {
    const urlParams = new URLSearchParams(window.location.search);
    let currentValue = urlParams.get(filterType);
    
    if (currentValue === null) {
        urlParams.set(filterType, 'true');
    } else if (currentValue === 'true') {
        urlParams.set(filterType, 'false');
    } else {
        urlParams.delete(filterType);
    }

    window.location.search = urlParams.toString();
}

// Highlight navigation buttons
///////////////////////////////

// Get all highlight elements
const highlights = document.querySelectorAll('.highlight');
let currentHighlightIndex = -1;

// Create navigation buttons
const navContainer = document.createElement('div');
navContainer.className = 'flex fixed right-5 bottom-5 flex-col space-y-2';
navContainer.innerHTML = `
  <button id="prevHighlight" class="px-4 py-2 font-bold text-white bg-indigo-500 rounded hover:bg-indigo-700">↑</button>
  <button id="nextHighlight" class="px-4 py-2 font-bold text-white bg-indigo-500 rounded hover:bg-indigo-700">↓</button>
`;
document.body.appendChild(navContainer);

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
    top: rect.top + scrollTop - 80, // 20px padding from the top
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
    outline: 3px solid rgba(99, 102, 241, 0.3);
    outline-offset: 6px;
    //outline-style: dotted;
    animation: fadeOutline 1s ease-in-out;
  }
`;
document.head.appendChild(style);

// END Navigation between highlights
////////////////////////////////////
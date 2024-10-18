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
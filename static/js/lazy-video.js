// Keep video downloads off the initial page load.
document.querySelectorAll('video[data-autoplay]').forEach(function(video) {
    function loadVideo() {
        video.play().catch(function() {
            // Autoplay may be blocked; native controls remain available.
        });
    }

    if (!('IntersectionObserver' in window)) {
        loadVideo();
        return;
    }

    const observer = new IntersectionObserver(function(entries) {
        if (entries.some(function(entry) { return entry.isIntersecting; })) {
            observer.disconnect();
            loadVideo();
        }
    }, { rootMargin: '100px' });
    observer.observe(video);
});

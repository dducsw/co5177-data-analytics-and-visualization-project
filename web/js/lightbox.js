(function () {
    const figures = document.querySelectorAll('.figure-card img');
    if (!figures.length) return;

    const modal = document.createElement('div');
    modal.className = 'lightbox-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.innerHTML = `
        <div class="lightbox-backdrop"></div>
        <div class="lightbox-content">
            <button type="button" class="lightbox-close" aria-label="Đóng">&times;</button>
            <img src="" alt="">
            <p class="lightbox-caption"></p>
        </div>
    `;
    document.body.appendChild(modal);

    const modalImg = modal.querySelector('img');
    const modalCaption = modal.querySelector('.lightbox-caption');
    const closeBtn = modal.querySelector('.lightbox-close');
    const backdrop = modal.querySelector('.lightbox-backdrop');

    function close() {
        modal.classList.remove('is-open');
        document.body.style.overflow = '';
    }

    figures.forEach(function (img) {
        img.addEventListener('click', function () {
            modalImg.src = img.src;
            modalImg.alt = img.alt;
            const cap = img.closest('.figure-card').querySelector('figcaption');
            modalCaption.textContent = cap ? cap.textContent : img.alt;
            modal.classList.add('is-open');
            document.body.style.overflow = 'hidden';
        });
    });

    closeBtn.addEventListener('click', close);
    backdrop.addEventListener('click', close);
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal.classList.contains('is-open')) close();
    });
})();

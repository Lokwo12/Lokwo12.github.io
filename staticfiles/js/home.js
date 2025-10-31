// Homepage animations: testimonials, blog, projects
(function(){
  // Simple fade-up animation for testimonials
  function animateTestimonials() {
    document.querySelectorAll('.testimonial-card').forEach(function(card, i) {
      card.style.opacity = 0;
      card.style.transform = 'translateY(30px)';
      setTimeout(function() {
        card.style.transition = 'opacity 0.6s, transform 0.6s';
        card.style.opacity = 1;
        card.style.transform = 'translateY(0)';
      }, 200 + i * 200);
    });
  }

  // Animate on scroll utility
  function animateOnScroll(selector, animation) {
    const elements = document.querySelectorAll(selector);
    function check() {
      elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 60) {
          el.classList.add(animation);
        }
      });
    }
    window.addEventListener('scroll', check, { passive: true });
    check();
  }

  // Random animation effects for cards
  const blogEffects = ['fade-in', 'slide-up', 'zoom-in'];
  const projectEffects = ['slide-up', 'fade-in', 'flip-in'];
  const testimonialEffects = ['fade-up', 'zoom-in', 'rotate-in'];
  function randomEffect(effects) { return effects[Math.floor(Math.random() * effects.length)]; }
  function animateRandomOnScroll(selector, effects) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((el) => {
      const effect = randomEffect(effects);
      el.classList.add('pre-anim');
      el.setAttribute('data-effect', effect);
    });
    function check() {
      elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 60) {
          el.classList.add(el.getAttribute('data-effect'));
        }
      });
    }
    window.addEventListener('scroll', check, { passive: true });
    check();
  }

  // Init on DOM ready
  window.addEventListener('DOMContentLoaded', function(){
    animateTestimonials();
    animateOnScroll('.blog-card', 'fade-in');
    animateOnScroll('.project-card', 'slide-up');
    animateOnScroll('.testimonial-card', 'fade-up');

    animateRandomOnScroll('.blog-card', blogEffects);
    animateRandomOnScroll('.project-card', projectEffects);
    animateRandomOnScroll('.testimonial-card', testimonialEffects);

    // Initialize Selected Projects carousel if present
    initSelectedProjectsCarousel();
  });
})();

// Simple auto-advance carousel for Selected Projects
function initSelectedProjectsCarousel(){
  const carousels = document.querySelectorAll('.carousel');
  if(!carousels.length) return;
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  carousels.forEach(carousel => {
    const track = carousel.querySelector('.carousel-track');
    if(!track) return;
    const slides = Array.from(track.children);
    if(slides.length < 2) return; // nothing to slide

    let index = 0;
    let timer = null;
  const interval = parseInt(carousel.getAttribute('data-interval') || '4000', 10);
  // Default to NO auto unless explicitly set to "true"
  const da = (carousel.getAttribute('data-auto') || '').toLowerCase();
  const auto = da === 'true';

    function scrollToIndex(i){
      index = (i + slides.length) % slides.length;
      // Align target slide to the start (left) edge
      try {
        slides[index].scrollIntoView({behavior: prefersReduced ? 'auto' : 'smooth', inline:'start', block:'nearest'});
      } catch(_e){
        const target = slides[index];
        track.scrollTo({left: target.offsetLeft, behavior: prefersReduced ? 'auto' : 'smooth'});
      }
      updateDots();
    }

    function start(){
      if(!auto || prefersReduced) return;
      stop();
      timer = setInterval(() => { scrollToIndex(index + 1); }, interval);
    }
    function stop(){ if(timer){ clearInterval(timer); timer = null; } }

    // Create dots dynamically
    const dotsWrap = document.createElement('div');
    dotsWrap.className = 'carousel-dots';
    const dots = slides.map((_, i) => {
      const b = document.createElement('button');
      b.className = 'dot' + (i === 0 ? ' active' : '');
      b.setAttribute('aria-label', `Go to slide ${i+1}`);
      b.addEventListener('click', () => { stop(); scrollToIndex(i); start(); });
      dotsWrap.appendChild(b);
      return b;
    });
    carousel.appendChild(dotsWrap);

    function updateDots(){
      dots.forEach((d, i) => { if(i === index) d.classList.add('active'); else d.classList.remove('active'); });
    }

    // Nav buttons
    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');
    if(prevBtn){ prevBtn.addEventListener('click', () => { stop(); scrollToIndex(index - 1); start(); }); }
    if(nextBtn){ nextBtn.addEventListener('click', () => { stop(); scrollToIndex(index + 1); start(); }); }

    // Pause on hover or pointer down
    carousel.addEventListener('mouseenter', stop);
    carousel.addEventListener('mouseleave', start);
    carousel.addEventListener('pointerdown', stop);
    carousel.addEventListener('pointerup', start);

    // Update index based on scroll position
    let scrollDebounce = null;
    track.addEventListener('scroll', () => {
      if(scrollDebounce) cancelAnimationFrame(scrollDebounce);
      scrollDebounce = requestAnimationFrame(() => {
        const gap = parseFloat(getComputedStyle(track).gap || 0);
        const slideW = slides[0].getBoundingClientRect().width + gap;
        index = Math.round(track.scrollLeft / slideW);
        updateDots();
      });
    }, { passive: true });

    // Keyboard navigation on focused carousel
    if(!carousel.hasAttribute('tabindex')) carousel.setAttribute('tabindex','0');
    carousel.addEventListener('keydown', (e) => {
      if(e.key === 'ArrowLeft'){ e.preventDefault(); stop(); scrollToIndex(index - 1); start(); }
      if(e.key === 'ArrowRight'){ e.preventDefault(); stop(); scrollToIndex(index + 1); start(); }
    });

    // Kick things off
    start();
    updateDots();
  });
}

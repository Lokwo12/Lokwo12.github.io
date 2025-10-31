// Projects page: random animation and interactive hover for cards
(function(){
  const projectEffects = ['fade-in', 'slide-up', 'zoom-in', 'flip-in', 'rotate-in'];
  function randomEffect(effects) { return effects[Math.floor(Math.random() * effects.length)]; }
  window.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.project-card').forEach(function(card, i) {
      const effect = randomEffect(projectEffects);
      card.classList.add('pre-anim');
      card.setAttribute('data-effect', effect);
      setTimeout(function(){ card.classList.add(effect); }, 150 + i * 120);
      card.addEventListener('mouseenter', function(){
        card.style.boxShadow = '0 8px 32px rgba(0,0,0,0.18)';
        card.style.transform = 'scale(1.03)';
        card.style.transition = 'box-shadow 0.25s, transform 0.25s';
      });
      card.addEventListener('mouseleave', function(){
        card.style.boxShadow = '';
        card.style.transform = '';
      });
    });
  });
})();

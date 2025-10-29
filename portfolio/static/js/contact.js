// Contact page: random intro effect and subtle hover for form
(function(){
  const contactEffects = ['fade-in', 'zoom-in', 'slide-up', 'flip-in'];
  function randomContactEffect(effects) { return effects[Math.floor(Math.random() * effects.length)]; }
  window.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.contact-form');
    const info = document.querySelector('.info-card');
    if (!form) return;
    const effect = randomContactEffect(contactEffects);
    form.classList.add('pre-anim');
    form.setAttribute('data-effect', effect);
    requestAnimationFrame(() => form.classList.add(effect));
    form.addEventListener('mouseenter', function() {
      form.style.boxShadow = '0 8px 32px rgba(0,0,0,0.18)';
      form.style.transform = 'scale(1.02)';
      form.style.transition = 'box-shadow 0.25s, transform 0.25s';
    });
    form.addEventListener('mouseleave', function() {
      form.style.boxShadow = '';
      form.style.transform = '';
    });
    if(info){
      const effect2 = randomContactEffect(contactEffects);
      info.classList.add('pre-anim');
      info.setAttribute('data-effect', effect2);
      requestAnimationFrame(() => info.classList.add(effect2));
    }
  });
})();

// Inline Calendly: show skeleton until Calendly iframe is injected and loaded
(function(){
  window.addEventListener('DOMContentLoaded', function(){
    const wrapper = document.querySelector('.booking-wrapper');
    if(!wrapper) return;
    const embed = wrapper.querySelector('.booking-embed');
    const skeleton = wrapper.querySelector('.embed-skeleton');
    if(!embed || !skeleton) return;
    // Observe for iframe injection by Calendly script
    const obs = new MutationObserver(()=>{
      const iframe = embed.querySelector('iframe');
      if(iframe){
        iframe.addEventListener('load', ()=>{ skeleton.style.display = 'none'; obs.disconnect(); });
      }
    });
    obs.observe(embed, { childList: true, subtree: true });
    // Fallback: hide skeleton after 10s even if no event received
    setTimeout(()=>{ skeleton.style.display = 'none'; obs.disconnect(); }, 10000);
  });
})();

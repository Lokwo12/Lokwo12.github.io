(function(){
  function createModal(){
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.setAttribute('role','dialog');
    modal.setAttribute('aria-modal','true');
    modal.setAttribute('aria-label','Image viewer');

    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';

    const dialog = document.createElement('div');
    dialog.className = 'modal-dialog';

  const header = document.createElement('div');
    header.className = 'modal-header';
    const title = document.createElement('div');
    title.className = 'modal-title';
    title.style.fontWeight = '600';
  const openBtn = document.createElement('a');
  openBtn.className = 'btn';
  openBtn.textContent = 'Open';
  openBtn.target = '_blank';
  openBtn.rel = 'noopener';
    const closeBtn = document.createElement('button');
    closeBtn.className = 'btn secondary';
    closeBtn.innerText = 'Close';
    closeBtn.addEventListener('click', close);

  header.appendChild(title);
  header.appendChild(openBtn);
    header.appendChild(closeBtn);

  const body = document.createElement('div');
    body.className = 'modal-body';
    const img = document.createElement('img');
    img.style.maxWidth = '100%';
    img.style.height = 'auto';
    img.style.display = 'block';
    img.alt = '';
    body.appendChild(img);

  const desc = document.createElement('div');
  desc.className = 'modal-desc';
  desc.style.marginTop = '8px';
  desc.style.color = 'var(--muted)';
  desc.style.fontSize = '0.95rem';
  body.appendChild(desc);

    dialog.appendChild(header);
    dialog.appendChild(body);
    modal.appendChild(backdrop);
    modal.appendChild(dialog);

    function close(){
      if(modal.parentNode){
        document.removeEventListener('keydown', onKey);
        modal.parentNode.removeChild(modal);
        document.body.style.overflow = '';
      }
    }

    function onKey(e){
      if(e.key === 'Escape') close();
      else if(e.key === 'ArrowRight') navigate(1);
      else if(e.key === 'ArrowLeft') navigate(-1);
    }

    function openWith(src, alt, link, description){
      img.src = src;
      img.alt = alt || '';
      title.textContent = alt || '';
      if(link){
        openBtn.href = link;
        openBtn.style.display = '';
      } else {
        openBtn.removeAttribute('href');
        openBtn.style.display = 'none';
      }
      if(description){
        desc.textContent = description;
        desc.style.display = '';
      } else {
        desc.textContent = '';
        desc.style.display = 'none';
      }
      document.body.appendChild(modal);
      document.body.style.overflow = 'hidden';
      setTimeout(function(){ document.addEventListener('keydown', onKey); }, 0);
    }

    // Navigation support
    let items = [];
    let index = -1;
    function setItems(list, startIndex){
      items = list || [];
      index = startIndex || 0;
    }
    function navigate(delta){
      if(!items.length) return;
      index = (index + delta + items.length) % items.length;
      const el = items[index];
      if(el){
        const src = el.getAttribute('href');
        const alt = el.getAttribute('data-title') || el.getAttribute('aria-label') || '';
        const link = el.getAttribute('data-link') || '';
        const description = el.getAttribute('data-desc') || '';
        openWith(src, alt, link, description);
      }
    }

    // Expose minimal API
    return { el: modal, openWith, close, setItems, navigate };
  }

  function init(){
    const anchors = Array.prototype.slice.call(document.querySelectorAll('.gallery-item a'));
    if(!anchors.length) return;

    const modal = createModal();
    modal.setItems(anchors, 0);

    anchors.forEach(function(a, i){
      // Store human title
      const img = a.querySelector('img');
      const title = (img && img.getAttribute('alt')) || a.getAttribute('aria-label') || '';
      a.setAttribute('data-title', title);
      a.addEventListener('click', function(ev){
        // If modifier keys, allow normal behavior (open in new tab, etc.)
        if(ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
        ev.preventDefault();
        modal.setItems(anchors, i);
        const src = a.getAttribute('href') || (img && img.getAttribute('src'));
        const link = a.getAttribute('data-link') || '';
        const description = a.getAttribute('data-desc') || '';
        modal.openWith(src, title, link, description);
      });
    });

    // Close on backdrop click
    document.addEventListener('click', function(ev){
      const m = modal.el;
      if(!m.parentNode) return;
      if(ev.target.classList && ev.target.classList.contains('modal-backdrop')){
        modal.close();
      }
    });
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();

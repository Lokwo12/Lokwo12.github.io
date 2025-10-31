document.addEventListener('DOMContentLoaded', () => {
  const items = document.querySelectorAll('.gallery-item');
  items.forEach(item => {
    const caption = item.querySelector('[data-caption]');
    const btn = item.querySelector('[data-toggle]');
    if (!caption || !btn) return;
<<<<<<< HEAD
    caption.classList.add('collapsible');
    requestAnimationFrame(() => {
      const hasOverflow = caption.scrollHeight > caption.clientHeight + 2;
=======
    // Apply collapsible and check overflow
    caption.classList.add('collapsible');
    // Give the browser a moment to compute layout
    requestAnimationFrame(() => {
      const hasOverflow = caption.scrollHeight > caption.clientHeight + 2; // allow small rounding
>>>>>>> 28a634a793a1f685086431c8cec6c79f00d6e9f4
      if (hasOverflow) {
        btn.hidden = false;
        btn.addEventListener('click', () => {
          const expanded = caption.classList.toggle('expanded');
<<<<<<< HEAD
          btn.textContent = expanded ? 'Show less' : 'Show more';
        });
      } else {
=======
          if (expanded) {
            btn.textContent = 'Show less';
          } else {
            btn.textContent = 'Show more';
          }
        });
      } else {
        // No overflow, remove collapsible cap to avoid unnecessary clipping
>>>>>>> 28a634a793a1f685086431c8cec6c79f00d6e9f4
        caption.classList.remove('collapsible');
      }
    });
  });
});
(function(){
  function applyTheme(theme){
    var html = document.documentElement;
    if(theme === 'light') html.setAttribute('data-theme','light');
    else html.removeAttribute('data-theme'); // dark default via CSS
  }
  function currentTheme(){
    return localStorage.getItem('admin_theme') || 'dark';
  }
  function setTheme(theme){
    localStorage.setItem('admin_theme', theme);
    applyTheme(theme);
    var btn = document.getElementById('theme-toggle-admin');
    if(btn) btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
  }
  function ensureToggle(){
    var header = document.getElementById('header');
    if(!header) return;
    var tools = document.getElementById('user-tools');
    var container = tools || header;
    var btn = document.createElement('button');
    btn.id = 'theme-toggle-admin';
    btn.type = 'button';
    btn.title = 'Toggle theme';
    btn.setAttribute('aria-pressed','false');
    btn.style.marginLeft = '10px';
    btn.className = 'button';
    btn.textContent = '🌓';
    btn.addEventListener('click', function(){
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      setTheme(next);
    });
    container.appendChild(btn);
  }

  // Initialize
  document.addEventListener('DOMContentLoaded', function(){
    applyTheme(currentTheme());
    ensureToggle();

    // Add filter toggle on changelist
    var changelist = document.getElementById('changelist');
    var filterAside = document.getElementById('changelist-filter');
    var toolbar = changelist && changelist.querySelector('#toolbar');
    if(changelist && filterAside && toolbar){
      // Persist collapsed state
      var collapsed = sessionStorage.getItem('admin_filters_collapsed') === '1';
      if(collapsed) document.body.classList.add('admin-filters-collapsed');

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'button filter-toggle';
      btn.textContent = collapsed ? 'Show Filters' : 'Hide Filters';
      btn.addEventListener('click', function(){
        var isCollapsed = document.body.classList.toggle('admin-filters-collapsed');
        btn.textContent = isCollapsed ? 'Show Filters' : 'Hide Filters';
        sessionStorage.setItem('admin_filters_collapsed', isCollapsed ? '1' : '0');
      });

      // Place next to search bar
      var searchForm = toolbar.querySelector('form');
      if(searchForm){
        var container = document.createElement('span');
        container.className = 'search-container';
        // Move existing search elements into container
        while(searchForm.firstChild){ container.appendChild(searchForm.firstChild); }
        searchForm.appendChild(container);
        searchForm.appendChild(btn);
      } else {
        toolbar.appendChild(btn);
      }
    }
  });
})();

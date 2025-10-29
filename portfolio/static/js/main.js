// Simple typing animation + nav toggle
document.addEventListener('DOMContentLoaded', function(){
	// typing animation for element with data-roles
	const el = document.querySelector('[data-roles]');
	if(el){
		const roles = el.getAttribute('data-roles').split('|');
		let r=0, idx=0, forward=true;
		const speed = Number(el.getAttribute('data-speed')) || 80;
		const pause = Number(el.getAttribute('data-pause')) || 800;
		const backPause = Number(el.getAttribute('data-back-pause')) || 350;
		function tick(){
			const full = roles[r];
			if(forward){
				idx++;
				if(idx>=full.length){forward=false;setTimeout(tick,pause);return}
			} else {
				idx--;
				if(idx<=0){forward=true;r=(r+1)%roles.length;setTimeout(tick,backPause);return}
			}
			el.textContent = full.slice(0, idx);
			setTimeout(tick, speed);
		}
		tick();
	}

	// Lightweight GA event tracker (safe if GA not loaded or consent not given)
	function gaReady(){ return typeof window.gtag === 'function'; }
	function trackEvent(action, params){
		try{ if(gaReady()) { window.gtag('event', action, params || {}); } }catch(e){}
	}

	// Global click tracking for common interactions
	document.addEventListener('click', function(ev){
		const target = ev.target.closest('a, button');
		if(!target) return;

		// Explicit data-ev events for richer context
		if(target.dataset && target.dataset.ev){
			const evName = target.dataset.ev;
			const payload = {
				path: window.location.pathname,
				project: target.dataset.project,
				slug: target.dataset.slug,
				url: target.dataset.url || target.getAttribute('href')
			};
			trackEvent(evName, payload);
		}

		// Theme toggle
		if(target.id === 'theme-toggle'){
			trackEvent('theme_toggle', { location: window.location.pathname });
			return;
		}

		// Downloads (links with download attr or .pdf href)
		if(target.tagName === 'A'){
			const href = target.getAttribute('href') || '';
			const absHref = target.href || href;
			if(target.hasAttribute('download') || /\.pdf($|\?|#)/i.test(href)){
				trackEvent('download', { item: absHref, link_text: (target.textContent||'').trim() });
				return;
			}
			// Portfolio PDF explicit
			if(/portfolio\.pdf/i.test(href)){
				trackEvent('download_portfolio_pdf', { item: absHref });
			}
			// Outbound links
			try{
				if(absHref && new URL(absHref).origin !== window.location.origin){
					trackEvent('outbound_click', { url: absHref, link_text: (target.textContent||'').trim() });
					return;
				}
			}catch(e){}
		}

		// Navigation/CTA heuristics
		if(target.matches('a[href*="/projects/"]')){
			trackEvent('nav_projects_click', { path: window.location.pathname });
		}
		if(target.matches('a[href*="/contact/"]')){
			trackEvent('nav_contact_click', { path: window.location.pathname });
		}
		if(target.matches('a[href^="#projects"]')){
			trackEvent('cta_view_projects', { path: window.location.pathname });
		}
	});


	// Multi-theme + brand toggle (cycles through combinations)
	(function(){
		const btn = document.getElementById('theme-toggle');
		const root = document.documentElement;

		const brands = ['indigo','teal','green'];
		const themes = ['dark','light'];
		// Build ordered cycle of combinations
		const cycle = [
			{theme:'dark', brand:'indigo'},
			{theme:'dark', brand:'teal'},
			{theme:'dark', brand:'green'},
			{theme:'light', brand:'indigo'},
			{theme:'light', brand:'teal'},
			{theme:'light', brand:'green'},
		];

		function apply(theme, brand){
			// theme: 'light' or 'dark'
			if(theme === 'light'){
				root.setAttribute('data-theme','light');
				btn && btn.setAttribute('aria-pressed','false');
			}else{
				root.removeAttribute('data-theme'); // default dark
				btn && btn.setAttribute('aria-pressed','true');
			}
			// brand: 'indigo' uses default (remove attr), otherwise set
			if(brand && brand !== 'indigo'){
				root.setAttribute('data-brand', brand);
			}else{
				root.removeAttribute('data-brand');
			}
			// update button title for clarity
			if(btn){
				btn.title = `Theme: ${theme} · Brand: ${brand || 'indigo'}`;
			}
			localStorage.setItem('theme', theme);
			localStorage.setItem('brand', brand || 'indigo');
		}

		function loadInitial(){
			const storedTheme = localStorage.getItem('theme');
			const storedBrand = localStorage.getItem('brand');
			if(storedTheme){
				apply(storedTheme, storedBrand || 'indigo');
			}else{
				const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
				apply(prefersDark ? 'dark' : 'light', storedBrand || 'indigo');
			}
		}

		function currentIndex(){
			const t = localStorage.getItem('theme') || (root.getAttribute('data-theme') === 'light' ? 'light' : 'dark');
			const b = localStorage.getItem('brand') || (root.getAttribute('data-brand') || 'indigo');
			return Math.max(0, cycle.findIndex(x => x.theme===t && x.brand===(b || 'indigo')));
		}

		loadInitial();
		if(btn){
			btn.addEventListener('click', () => {
				const idx = currentIndex();
				const next = cycle[(idx + 1) % cycle.length];
				apply(next.theme, next.brand);
			});
		}
	})();

	// Header scroll behavior: compact on scroll only (never hide)
	(function(){
		const header = document.querySelector('.site-header');
		if(!header) return;
		let ticking = false;
		function onScroll(){
			const y = window.scrollY || 0;
			// toggle compact style
			if(y > 16){ header.classList.add('scrolled'); } else { header.classList.remove('scrolled'); }
			// ensure header is always visible
			header.classList.remove('hide');
			ticking = false;
		}
		window.addEventListener('scroll', ()=>{
			if(!ticking){ requestAnimationFrame(onScroll); ticking = true; }
		});
		// initial
		onScroll();
	})();

	// Top scroll progress bar
	(function(){
		const bar = document.getElementById('scroll-progress');
		if(!bar) return;
		let rafId = null;
		const update = () => {
			rafId = null;
			const doc = document.documentElement;
			const body = document.body;
			const scrollTop = doc.scrollTop || body.scrollTop || window.scrollY || 0;
			const maxScroll = (doc.scrollHeight || body.scrollHeight) - window.innerHeight;
			const ratio = maxScroll > 0 ? Math.min(1, Math.max(0, scrollTop / maxScroll)) : 0;
			bar.style.width = (ratio * 100).toFixed(2) + '%';
		};
		const onScroll = () => {
			if(rafId) return;
			rafId = requestAnimationFrame(update);
		};
		window.addEventListener('scroll', onScroll, { passive: true });
		window.addEventListener('resize', onScroll, { passive: true });
		update();
	})();

	// Active nav highlighting based on path and in-view sections
	(function(){
		const nav = document.querySelector('.site-nav');
		if(!nav) return;
		const links = Array.from(nav.querySelectorAll('a[href]'));
		function setActive(matchFn){
			links.forEach(a => a.classList.remove('active'));
			const active = links.find(matchFn);
			if(active) active.classList.add('active');
		}
		const path = window.location.pathname || '/';
		function byPath(p){ return a => (a.getAttribute('href')||'').startsWith(p); }
		if(path.startsWith('/about/')) setActive(byPath('/about/'));
		else if(path.startsWith('/projects/')) setActive(byPath('/projects/'));
		else if(path.startsWith('/blog/')) setActive(byPath('/blog/'));
		else if(path.startsWith('/contact/')) setActive(byPath('/contact/'));
		else setActive(a => (a.getAttribute('href')||'/') === '/');

		// On the homepage, when #projects section is in view, highlight Projects link
		if(path === '/' || path === ''){
			const projects = document.getElementById('projects');
			const projectsLink = links.find(byPath('/projects/'));
			const homeLink = links.find(a => (a.getAttribute('href')||'/') === '/');
			if(projects && projectsLink){
				const io = new IntersectionObserver((entries)=>{
					entries.forEach(e => {
						if(e.isIntersecting && e.intersectionRatio > 0.5){
							links.forEach(a => a.classList.remove('active'));
							projectsLink.classList.add('active');
						}else{
							if(homeLink){
								links.forEach(a => a.classList.remove('active'));
								homeLink.classList.add('active');
							}
						}
					});
				}, { threshold: [0.5] });
				io.observe(projects);
			}
		}
	})();
		// mobile nav - toggle class for better control and accessibility
		const toggle = document.querySelector('.nav-toggle');
		const nav = document.querySelector('.site-nav');
		if(toggle && nav){
			toggle.addEventListener('click', ()=>{
				const open = toggle.getAttribute('aria-expanded') === 'true';
				toggle.setAttribute('aria-expanded', String(!open));
				nav.classList.toggle('open');
				if(!open){
					// focus first link when opened
					const first = nav.querySelector('a');
					if(first) first.focus();
				}
			});
		}

			// show simple loading state on contact form submit
			const contactForm = document.querySelector('form[aria-label="Contact form"]');
			if(contactForm){
				contactForm.addEventListener('submit', ()=>{
					const submit = contactForm.querySelector('button[type="submit"]');
					if(submit){
						submit.disabled = true;
						submit.textContent = 'Sending...';
					}
					trackEvent('contact_submit_attempt', { path: window.location.pathname });
				});
			}

	// Fire case_study_view on project detail pages
	(function(){
		const h1 = document.querySelector('.project-detail h1');
		if(h1){
			const title = (h1.textContent || '').trim();
			// Try to extract slug from URL: /projects/<slug>/
			const m = window.location.pathname.match(/\/projects\/([^\/]*)\//);
			const slug = m ? m[1] : undefined;
			trackEvent('case_study_view', { path: window.location.pathname, project: title, slug });
		}
	})();

	// Minimal reveal-on-scroll effect applied to common sections/cards across pages
	(function(){
		if(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches){
			return; // respect reduced motion
		}
		const targets = Array.from(document.querySelectorAll(
			[
				'section.container',
				'.project-card',
				'.blog-post',
				'.resume-card',
				'.contact-card',
				'.tech-tile',
				'.stat',
				'.gallery-item'
			].join(',')
		));
		if(!targets.length) return;
		targets.forEach(el => el.classList.add('reveal'));
		const io = new IntersectionObserver((entries)=>{
			entries.forEach(e => {
				if(e.isIntersecting){
					e.target.classList.add('in-view');
					// Once revealed, unobserve to keep it minimal
					io.unobserve(e.target);
				}
			});
		}, { threshold: 0.15 });
		targets.forEach(el => io.observe(el));
	})();
});

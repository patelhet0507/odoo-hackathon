// === TRANSITOPS Micro-Interaction System ===
// Trigger → Rules → Feedback → Loops & Modes (Dan Saffer)

(function () {
  'use strict';

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouchDevice = window.matchMedia('(pointer: coarse)').matches;
  const springEasing = 'cubic-bezier(0.34, 1.56, 0.64, 1)';
  const standardEasing = 'cubic-bezier(0.2, 0, 0, 1)';

  // ============================================================
  // 1. Number Counter — KPI digit animation
  // Trigger: Element enters viewport
  // Rules: Count from 0 to target value with easing
  // Feedback: Digit updates on each frame
  // ============================================================
  function animateCounters() {
    document.querySelectorAll('[data-count-to]').forEach(function (el) {
      var target = parseInt(el.getAttribute('data-count-to'), 10);
      var suffix = el.getAttribute('data-count-suffix') || '';
      var duration = reducedMotion ? 1 : Math.min(1500, target * 8 + 200);
      var startTime = null;

      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = Math.min((timestamp - startTime) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3);
        var current = Math.floor(eased * target);
        el.textContent = current.toLocaleString() + suffix;
        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          el.textContent = target.toLocaleString() + suffix;
        }
      }
      requestAnimationFrame(step);
    });
  }

  // ============================================================
  // 2. Stagger Entrance — Cards/lists animate in sequence
  // Trigger: Element with .stagger-group comes into view
  // ============================================================
  function setupStagger() {
    document.querySelectorAll('.stagger-group').forEach(function (group) {
      var items = group.querySelectorAll('.stagger-item');
      if (items.length === 0) return;
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          items.forEach(function (item, i) {
            var delay = reducedMotion ? 0 : i * 60;
            item.style.transitionDelay = delay + 'ms';
            item.classList.add('stagger-visible');
          });
          observer.unobserve(group);
        });
      }, { threshold: 0.1 });
      observer.observe(group);
    });
  }

  // ============================================================
  // 3. Toast Notification System
  // Trigger: showToast(message, type) called programmatically
  // Rules: 3-5s auto-dismiss, stacks vertically
  // Feedback: Slide + fade, progress bar, dismiss button
  // ============================================================
  function createToastSystem() {
    var container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      container.style.cssText = 'position:fixed;top:80px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:8px;max-width:380px;pointer-events:none';
      document.body.appendChild(container);
    }

    window.showToast = function (message, type) {
      type = type || 'info';
      var colors = {
        success: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200',
        error: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200',
        warning: 'bg-amber-50 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200',
        info: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
      };
      var icons = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
      };

      var el = document.createElement('div');
      el.className = 'toast-' + Date.now() + ' flex items-center gap-3 p-4 rounded-xl border shadow-lg pointer-events-auto translate-x-full opacity-0 ' + (colors[type] || colors.info);
      el.style.transition = reducedMotion ? 'none' : 'all 350ms ' + springEasing;
      el.style.transform = 'translateX(100%)';
      el.style.opacity = '0';
      el.role = 'alert';

      el.innerHTML =
        '<span class="material-symbols-outlined text-xl shrink-0">' + (icons[type] || icons.info) + '</span>' +
        '<span class="text-sm font-medium flex-1">' + message + '</span>' +
        '<button class="p-1 rounded-lg hover:bg-black/10 dark:hover:bg-white/10 transition-colors" onclick="this.closest(\'[role=alert]\').remove()" aria-label="Dismiss">' +
        '<span class="material-symbols-outlined text-lg">close</span></button>';

      container.appendChild(el);

      requestAnimationFrame(function () {
        el.style.transform = 'translateX(0)';
        el.style.opacity = '1';
      });

      if (!reducedMotion) {
        var bar = document.createElement('div');
        bar.className = 'toast-bar';
        bar.style.cssText = 'position:absolute;bottom:0;left:0;height:3px;border-radius:0 0 12px 12px;background:currentColor;opacity:0.3;transition:width 4000ms linear';
        bar.style.width = '100%';
        el.style.position = 'relative';
        el.appendChild(bar);
        requestAnimationFrame(function () { bar.style.width = '0%'; });
      }

      setTimeout(function () {
        if (!el.parentNode) return;
        el.style.transform = 'translateX(100%)';
        el.style.opacity = '0';
        setTimeout(function () { if (el.parentNode) el.remove(); }, 350);
      }, reducedMotion ? 2000 : 4500);
    };
  }

  // ============================================================
  // 4. Button Ripple Effect
  // Trigger: Click on .btn-ripple or buttons inside .ripple-group
  // ============================================================
  function addRippleSupport() {
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('.btn-ripple, .btn-primary, [type="submit"], button:not([class*="no-ripple"])');
      if (!btn || btn.closest('.no-ripple')) return;
      if (reducedMotion) return;

      var rect = btn.getBoundingClientRect();
      var size = Math.max(rect.width, rect.height);
      var x = e.clientX - rect.left - size / 2;
      var y = e.clientY - rect.top - size / 2;

      var ripple = document.createElement('span');
      ripple.style.cssText =
        'position:absolute;top:' + y + 'px;left:' + x + 'px;width:' + size + 'px;height:' + size + 'px;' +
        'border-radius:50%;background:rgba(255,255,255,0.3);transform:scale(0);animation:ripple-effect 0.6s ease-out;' +
        'pointer-events:none';
      if (btn.classList.contains('dark') || btn.closest('.dark')) {
        ripple.style.background = 'rgba(255,255,255,0.2)';
      } else {
        ripple.style.background = 'rgba(65,67,213,0.15)';
      }
      btn.style.position = btn.style.position || 'relative';
      btn.style.overflow = btn.style.overflow || 'hidden';
      btn.appendChild(ripple);
      setTimeout(function () { if (ripple.parentNode) ripple.remove(); }, 600);
    });
  }

  // ============================================================
  // 5. Slide-Over Drawer with Spring Physics
  // Trigger: openSlideOver() / closeSlideOver()
  // ============================================================
  function enhanceSlideOver() {
    window.openSlideOver = function (panelId) {
      var panel = document.getElementById(panelId) || document.getElementById('slideOver');
      if (!panel) return;
      var backdrop = panel.querySelector('[data-backdrop]') || panel.querySelector('.absolute.inset-0');
      var slidePanel = panel.querySelector('[data-panel]') || panel.querySelector('.absolute.right-0');

      panel.style.display = 'block';
      panel.classList.remove('pointer-events-none');

      requestAnimationFrame(function () {
        if (backdrop) {
          backdrop.classList.remove('opacity-0');
          backdrop.classList.add('opacity-100');
        }
        if (slidePanel) {
          slidePanel.classList.remove('translate-x-full');
          slidePanel.classList.add('translate-x-0');
        }
      });

      document.body.style.overflow = 'hidden';
    };

    window.closeSlideOver = function (panelId) {
      var panel = document.getElementById(panelId) || document.getElementById('slideOver');
      if (!panel) return;
      var backdrop = panel.querySelector('[data-backdrop]') || panel.querySelector('.absolute.inset-0');
      var slidePanel = panel.querySelector('[data-panel]') || panel.querySelector('.absolute.right-0');

      if (backdrop) {
        backdrop.classList.remove('opacity-100');
        backdrop.classList.add('opacity-0');
      }
      if (slidePanel) {
        slidePanel.classList.remove('translate-x-0');
        slidePanel.classList.add('translate-x-full');
      }

      setTimeout(function () {
        panel.style.display = 'none';
        document.body.style.overflow = '';
      }, 300);
    };

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        var openPanel = document.querySelector('#slideOver[style*="display: block"], #slideOver[style*="display:block"]');
        if (openPanel) window.closeSlideOver();
      }
    });
  }

  // ============================================================
  // 6. Form Validation Feedback
  // Trigger: Input blur/change with data-validate
  // ============================================================
  function setupFormValidation() {
    document.addEventListener('blur', function (e) {
      var input = e.target.closest('[data-validate]');
      if (!input) return;

      var isValid = input.checkValidity();
      input.classList.remove('input-error', 'input-success');

      if (!isValid) {
        input.classList.add('input-error');
        if (!reducedMotion) {
          input.style.animation = 'none';
          requestAnimationFrame(function () {
            input.style.animation = 'shake 0.4s ease';
          });
        }
      } else if (input.value.length > 0) {
        input.classList.add('input-success');
      }
    });
  }

  // ============================================================
  // 7. Scroll Reveal — elements fade in on scroll
  // Trigger: .reveal element enters viewport
  // ============================================================
  function setupScrollReveal() {
    if (reducedMotion) {
      document.querySelectorAll('.reveal').forEach(function (el) {
        el.classList.add('reveal-visible');
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('reveal-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal').forEach(function (el) {
      observer.observe(el);
    });
  }

  // ============================================================
  // 8. Theme Toggle Animation — circular clip-path reveal
  // Trigger: Click on #themeToggle
  // ============================================================
  function enhanceThemeToggle() {
    var toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    var origHandler = toggle.click;
    toggle.addEventListener('click', function (e) {
      var isDark = document.documentElement.classList.contains('dark');
      var icon = document.getElementById('themeIcon');

      if (icon && !reducedMotion) {
        icon.style.transition = 'all 250ms ' + springEasing;
        icon.style.transform = 'scale(0.5) rotate(180deg)';
        icon.style.opacity = '0';
        setTimeout(function () {
          icon.textContent = isDark ? 'dark_mode' : 'light_mode';
          icon.style.transform = 'scale(1) rotate(0deg)';
          icon.style.opacity = '1';
        }, 150);
      }
    });
  }

  // ============================================================
  // 9. Active Status Pulse Rings
  // Trigger: Elements with .status-pulse
  // ============================================================
  function setupStatusPulse() {
    document.querySelectorAll('.status-pulse').forEach(function (el) {
      var ring = document.createElement('span');
      ring.className = 'pulse-ring';
      el.style.position = 'relative';
      el.appendChild(ring);
    });
  }

  // ============================================================
  // 10. Mobile Drawer — slide with spring
  // ============================================================
  function enhanceMobileDrawer() {
    var origToggle = window.toggleMobileSidebar;
    if (!origToggle) return;

    window.toggleMobileSidebar = function () {
      var sidebar = document.getElementById('sidebar');
      var overlay = document.getElementById('mobileDrawerOverlay');
      if (!sidebar || !overlay) return;

      if (sidebar.classList.contains('hidden')) {
        sidebar.classList.remove('hidden');
        sidebar.classList.add('flex');
        sidebar.style.transform = 'translateX(-100%)';
        requestAnimationFrame(function () {
          sidebar.style.transition = reducedMotion ? 'none' : 'transform 350ms ' + springEasing;
          sidebar.style.transform = 'translateX(0)';
        });
        overlay.classList.remove('hidden');
        overlay.style.opacity = '0';
        requestAnimationFrame(function () {
          overlay.style.transition = 'opacity 250ms ease';
          overlay.style.opacity = '1';
        });
        document.body.classList.add('overflow-hidden');
      } else {
        sidebar.style.transition = reducedMotion ? 'none' : 'transform 300ms ease-in';
        sidebar.style.transform = 'translateX(-100%)';
        overlay.style.opacity = '0';
        setTimeout(function () {
          sidebar.classList.add('hidden');
          sidebar.classList.remove('flex');
          sidebar.style.transform = '';
          overlay.classList.add('hidden');
          document.body.classList.remove('overflow-hidden');
        }, 300);
      }
    };
  }

  // ============================================================
  // 11. Profile Dropdown — scale+ fade
  // ============================================================
  function enhanceProfileDropdown() {
    var origToggle = window.toggleProfileDropdown;
    if (!origToggle) return;

    window.toggleProfileDropdown = function () {
      var dropdown = document.getElementById('profileDropdown');
      if (!dropdown) return;

      if (dropdown.classList.contains('hidden')) {
        dropdown.classList.remove('hidden');
        dropdown.style.opacity = '0';
        dropdown.style.transform = 'scale(0.95) translateY(-4px)';
        dropdown.style.transformOrigin = 'top right';
        requestAnimationFrame(function () {
          dropdown.style.transition = reducedMotion ? 'none' : 'all 200ms ease-out';
          dropdown.style.opacity = '1';
          dropdown.style.transform = 'scale(1) translateY(0)';
        });
      } else {
        dropdown.style.transition = reducedMotion ? 'none' : 'all 150ms ease-in';
        dropdown.style.opacity = '0';
        dropdown.style.transform = 'scale(0.95) translateY(-4px)';
        setTimeout(function () { dropdown.classList.add('hidden'); }, 150);
      }
    };
  }

  // ============================================================
  // 12. Radial Progress Ring — animate on mount
  // Trigger: .radial-progress circles
  // ============================================================
  function animateProgressRings() {
    document.querySelectorAll('.radial-progress .progress-circle').forEach(function (circle) {
      if (reducedMotion) return;
      var offset = circle.getAttribute('stroke-dashoffset');
      if (offset) {
        circle.style.strokeDashoffset = '88';
        requestAnimationFrame(function () {
          circle.style.transition = 'stroke-dashoffset 0.8s ' + springEasing;
          circle.style.strokeDashoffset = offset;
        });
      }
    });
  }

  // ============================================================
  // Init — runs on DOMContentLoaded
  // ============================================================
  function init() {
    // CSS injection for ripple keyframe
    if (!document.getElementById('animations-keyframes')) {
      var style = document.createElement('style');
      style.id = 'animations-keyframes';
      style.textContent =
        '@keyframes ripple-effect { to { transform: scale(4); opacity: 0; } }' +
        '@keyframes shake { ' +
        '0%,100% { transform: translateX(0); } ' +
        '20%,60% { transform: translateX(-6px); } ' +
        '40%,80% { transform: translateX(6px); } ' +
        '}' +
        '@keyframes pulse-ring { ' +
        '0% { transform: scale(1); opacity: 0.6; } ' +
        '100% { transform: scale(2.5); opacity: 0; } ' +
        '}' +
        '.pulse-ring { ' +
        'position: absolute; inset: 0; border-radius: 50%; ' +
        'border: 2px solid currentColor; ' +
        'animation: pulse-ring 2s ease-out infinite; ' +
        'pointer-events: none; ' +
        '}' +
        '.stagger-item { opacity: 0; transform: translateY(12px); transition: opacity 0.4s ease-out, transform 0.4s ease-out; }' +
        '.stagger-item.stagger-visible { opacity: 1; transform: translateY(0); }' +
        '.reveal { opacity: 0; transform: translateY(20px); transition: opacity 0.5s ease-out, transform 0.5s ease-out; }' +
        '.reveal.reveal-visible { opacity: 1; transform: translateY(0); }' +
        '.input-error { border-color: #ba1a1a !important; box-shadow: 0 0 0 3px rgba(186,26,26,0.12) !important; }' +
        '.input-success { border-color: #008259 !important; box-shadow: 0 0 0 3px rgba(0,130,89,0.12) !important; }';
      document.head.appendChild(style);
    }

    animateCounters();
    setupStagger();
    createToastSystem();
    addRippleSupport();
    enhanceSlideOver();
    setupFormValidation();
    setupScrollReveal();
    enhanceThemeToggle();
    setupStatusPulse();
    enhanceMobileDrawer();
    enhanceProfileDropdown();
    animateProgressRings();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

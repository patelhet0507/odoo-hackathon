// === TransitOps UI Helpers: Toasts + Confirm Modal + AJAX forms ===
(function () {
  'use strict';

  function getCookie(name) {
    var v = null;
    document.cookie.split(';').forEach(function (c) {
      var parts = c.trim().split('=');
      if (parts[0] === name) v = decodeURIComponent(parts.slice(1).join('='));
    });
    return v;
  }

  var TOAST_STYLES = {
    success: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800/40 text-green-800 dark:text-green-200',
    error: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800/40 text-red-800 dark:text-red-200',
    warning: 'bg-amber-50 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800/40 text-amber-800 dark:text-amber-200',
    info: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800/40 text-blue-800 dark:text-blue-200'
  };
  var TOAST_ICONS = { success: 'check_circle', error: 'error', warning: 'warning', info: 'info' };

  function showToast(message, type) {
    type = TOAST_STYLES[type] ? type : 'success';
    var container = document.getElementById('toastContainer');
    if (!container) return;

    var el = document.createElement('div');
    el.className = 'toast p-4 rounded-xl border flex items-start justify-between gap-3 shadow-lg animate-slide-in ' + TOAST_STYLES[type];
    el.setAttribute('role', 'status');

    var left = document.createElement('div');
    left.className = 'flex items-center gap-2';
    var icon = document.createElement('span');
    icon.className = 'material-symbols-outlined text-[20px] shrink-0';
    icon.textContent = TOAST_ICONS[type];
    var text = document.createElement('span');
    text.className = 'text-sm font-medium';
    text.textContent = message;
    left.appendChild(icon);
    left.appendChild(text);

    var close = document.createElement('button');
    close.className = 'text-outline hover:text-on-surface p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors shrink-0';
    close.setAttribute('aria-label', 'Dismiss');
    close.innerHTML = '<span class="material-symbols-outlined text-[16px]">close</span>';

    el.appendChild(left);
    el.appendChild(close);
    container.appendChild(el);

    var remove = function () {
      if (el && el.parentNode) {
        el.classList.add('opacity-0');
        setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 200);
      }
    };
    close.addEventListener('click', remove);
    setTimeout(remove, 4500);
  }

  // ---- Confirm Modal ----
  var confirmCallback = null;

  function openConfirm(opts) {
    opts = opts || {};
    var modal = document.getElementById('confirmModal');
    if (!modal) return;
    document.getElementById('confirmTitle').textContent = opts.title || 'Confirm Action';
    document.getElementById('confirmMessage').textContent = opts.message || 'Are you sure you want to continue?';
    var ok = document.getElementById('confirmOk');
    ok.textContent = opts.confirmText || 'Confirm';
    ok.className = 'px-4 py-2 rounded-xl text-sm font-semibold transition-all ' +
      (opts.danger
        ? 'bg-error text-white hover:opacity-90'
        : 'bg-primary text-white hover:bg-secondary');
    confirmCallback = opts.onConfirm || null;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }

  function closeConfirm() {
    var modal = document.getElementById('confirmModal');
    if (modal) { modal.classList.add('hidden'); modal.classList.remove('flex'); }
    confirmCallback = null;
  }

  function bindConfirmControls() {
    var ok = document.getElementById('confirmOk');
    if (ok) ok.addEventListener('click', function () {
      var cb = confirmCallback; closeConfirm(); if (cb) cb();
    });
    var cancel = document.getElementById('confirmCancel');
    if (cancel) cancel.addEventListener('click', closeConfirm);
    var modal = document.getElementById('confirmModal');
    if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeConfirm(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeConfirm(); });
  }

  function ajaxSubmit(form, onDone) {
    var fd = new FormData(form);
    fetch(form.getAttribute('action') || form.action, {
      method: 'POST',
      body: fd,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken') || ''
      },
      credentials: 'same-origin'
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data && data.message) showToast(data.message, (data.type) || 'success');
        else showToast('Done', 'success');
        if (onDone) onDone(data);
        else if (data && data.redirect) window.location.href = data.redirect;
        else window.location.reload();
      })
      .catch(function () { showToast('Something went wrong. Please try again.', 'error'); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindConfirmControls();

    // Promote server-rendered Django messages to toasts
    var sm = document.getElementById('serverMessages');
    if (sm) {
      sm.querySelectorAll('[data-toast-msg]').forEach(function (d) {
        showToast(d.getAttribute('data-toast-msg'), d.getAttribute('data-toast-type') || 'success');
      });
    }

    // data-confirm on links/buttons -> navigate on confirm (for simple GET actions)
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
      if (el.closest('form[data-ajax]')) return; // handled by ajax form
      el.addEventListener('click', function (e) {
        e.preventDefault();
        openConfirm({
          title: el.getAttribute('data-confirm-title') || 'Confirm Action',
          message: el.getAttribute('data-confirm') || 'Are you sure?',
          confirmText: el.getAttribute('data-confirm-ok') || 'Confirm',
          danger: el.hasAttribute('data-confirm-danger'),
          onConfirm: function () {
            if (el.tagName === 'A') window.location.href = el.href;
            else el.click();
          }
        });
      });
    });

    // AJAX forms -> submit via fetch, show toast, no full navigation
    document.querySelectorAll('form[data-ajax]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var cnf = form.getAttribute('data-confirm');
        if (cnf) {
          openConfirm({
            title: form.getAttribute('data-confirm-title') || 'Confirm Action',
            message: cnf,
            confirmText: form.getAttribute('data-confirm-ok') || 'Confirm',
            danger: form.hasAttribute('data-confirm-danger'),
            onConfirm: function () { ajaxSubmit(form); }
          });
        } else {
          ajaxSubmit(form);
        }
      });
    });
  });

  window.showToast = showToast;
  window.openConfirm = openConfirm;
})();

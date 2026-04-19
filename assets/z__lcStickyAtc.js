/* Phase 7 Sprint B - Task B5 (P1-10) - Decision 5
 * LC mobile sticky Add-to-Cart bar.
 *
 * Mobile-only (<=749px). IntersectionObserver on the in-flow ATC button.
 * Adds .is-visible to .lc-sticky-atc when the in-flow ATC leaves the
 * viewport; removes it when the in-flow ATC re-enters. Loaded `defer`.
 *
 * The sticky ATC button forwards its click to the in-flow ATC so they
 * share the same form submission. The variant recap text updates on any
 * option change in the form.
 */
(function () {
  'use strict';

  function init() {
    var sticky = document.querySelector('[data-lc-sticky-atc]');
    if (!sticky) return;

    var inflow = document.querySelector('.button--add-to-cart');
    if (!inflow) return;

    var media = window.matchMedia('(max-width: 749px)');

    sticky.removeAttribute('hidden');

    function onIntersect(entries) {
      entries.forEach(function (entry) {
        if (!media.matches) {
          sticky.classList.remove('is-visible');
          sticky.setAttribute('aria-hidden', 'true');
          return;
        }
        // Only show the sticky when the in-flow ATC has scrolled OUT THE TOP
        // of the viewport (rect.bottom < 0). Don't show on initial load when
        // the ATC is simply below the fold (rect.top > viewportHeight).
        var rect = entry.boundingClientRect;
        var scrolledPast = !entry.isIntersecting && rect.bottom < 0;
        if (scrolledPast) {
          sticky.classList.add('is-visible');
          sticky.setAttribute('aria-hidden', 'false');
        } else {
          sticky.classList.remove('is-visible');
          sticky.setAttribute('aria-hidden', 'true');
        }
      });
    }

    var observer = new IntersectionObserver(onIntersect, { threshold: 0 });
    observer.observe(inflow);

    media.addEventListener('change', function () {
      if (!media.matches) {
        sticky.classList.remove('is-visible');
        sticky.setAttribute('aria-hidden', 'true');
      }
    });

    var trigger = sticky.querySelector('[data-lc-sticky-trigger]');
    if (trigger) {
      trigger.addEventListener('click', function (e) {
        e.preventDefault();
        if (!inflow.disabled) {
          inflow.click();
        }
      });
    }

    var form = inflow.closest('form');
    if (form) {
      var meta = sticky.querySelector('[data-lc-sticky-meta]');
      function updateMeta() {
        if (!meta) return;
        var checked = form.querySelectorAll('input[type="radio"]:checked');
        var parts = [];
        Array.prototype.forEach.call(checked, function (input) {
          var value = (input.value || '').trim();
          if (!value || value.toLowerCase() === 'n/a') return;
          parts.push(value);
        });
        meta.textContent = parts.join(' / ');
      }
      form.addEventListener('change', updateMeta);
      updateMeta();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* Phase 7 Sprint B - Task B2 (P0-7, P1-14)
 * LC variant picker enhancements: Type-driven Colour-fieldset hide and
 * unavailable-combination handling on the PDP. Loaded `defer` from
 * sections/product__main.liquid.
 *
 * Behaviour:
 * 1. When the Type option changes, if the chosen Type is in the
 *    data-hide-on-type list on the Colour fieldset, hide the Colour
 *    fieldset and mark its inputs as not-required for ATC validation.
 * 2. On any option change, re-evaluate which swatches in this product
 *    have no available variant for the current partial selection and
 *    toggle [data-unavailable] on those .swatch-element nodes. Show the
 *    inline note if any swatch in the fieldset is unavailable.
 *
 * Scoped to .product_section so it runs once per PDP.
 */
(function () {
  'use strict';

  function init(root) {
    if (!root || root.dataset.lcVariantPickerInit === '1') return;
    root.dataset.lcVariantPickerInit = '1';

    var fieldsets = root.querySelectorAll('fieldset.swatch-fieldset');
    if (!fieldsets.length) return;

    var typeFieldset = null;
    var colourFieldset = null;
    fieldsets.forEach(function (fs) {
      var name = (fs.getAttribute('data-option-name') || '').toLowerCase().trim();
      if (name === 'type') typeFieldset = fs;
      if (name === 'colour' || name === 'color') colourFieldset = fs;
    });

    function applyTypeColourHide() {
      if (!typeFieldset || !colourFieldset) return;
      var hideList = (colourFieldset.getAttribute('data-hide-on-type') || '')
        .split(',')
        .map(function (s) { return s.trim().toLowerCase(); })
        .filter(Boolean);
      if (!hideList.length) return;

      var checked = typeFieldset.querySelector('input[type="radio"]:checked');
      var typeValue = checked ? checked.value.toLowerCase().trim() : '';
      var shouldHide = hideList.indexOf(typeValue) !== -1;

      colourFieldset.classList.toggle('lc-is-hidden', shouldHide);
      colourFieldset.toggleAttribute('aria-hidden', shouldHide);
      var inputs = colourFieldset.querySelectorAll('input[type="radio"]');
      inputs.forEach(function (i) {
        if (shouldHide) {
          i.setAttribute('data-lc-required-skip', 'true');
          i.setAttribute('disabled', 'disabled');
        } else {
          i.removeAttribute('data-lc-required-skip');
          i.removeAttribute('disabled');
        }
      });
    }

    function getOptionIndexFor(fs) {
      return parseInt(fs.getAttribute('data-option-index'), 10);
    }

    function getCurrentSelection(productVariants) {
      var selection = [];
      fieldsets.forEach(function (fs) {
        if (fs.classList.contains('lc-is-hidden')) {
          selection.push(null);
          return;
        }
        var checked = fs.querySelector('input[type="radio"]:checked');
        selection[getOptionIndexFor(fs)] = checked ? checked.value : null;
      });
      return selection;
    }

    function loadProductVariants() {
      var script = root.querySelector('[data-section-data]');
      if (!script) return null;
      try {
        var data = JSON.parse(script.textContent || '{}');
        if (data.product && data.product.variants) return data.product.variants;
      } catch (e) {
        return null;
      }
      return null;
    }

    function applyUnavailable() {
      var variants = loadProductVariants();
      if (!variants) return;
      var selection = getCurrentSelection(variants);

      fieldsets.forEach(function (fs) {
        if (fs.classList.contains('lc-is-hidden')) return;
        var idx = getOptionIndexFor(fs);
        var anyUnavailable = false;

        var swatches = fs.querySelectorAll('.swatch__option');
        swatches.forEach(function (sw) {
          var input = sw.querySelector('input[type="radio"]');
          var label = sw.querySelector('.swatch-element');
          if (!input || !label) return;

          var hypothetical = selection.slice();
          hypothetical[idx] = input.value;

          var match = variants.find(function (v) {
            for (var i = 0; i < hypothetical.length; i++) {
              var sel = hypothetical[i];
              if (sel === null || sel === undefined) continue;
              var opt = v['option' + (i + 1)];
              if (!opt) continue;
              if (opt !== sel) return false;
            }
            return true;
          });

          var available = match && match.available;
          if (!available) {
            label.setAttribute('data-unavailable', 'true');
            anyUnavailable = true;
          } else {
            label.removeAttribute('data-unavailable');
          }
        });

        var note = fs.querySelector('[data-lc-unavailable-note]');
        if (note) {
          note.hidden = !anyUnavailable;
        }
      });
    }

    function recompute() {
      applyTypeColourHide();
      applyUnavailable();
    }

    fieldsets.forEach(function (fs) {
      fs.addEventListener('change', function (e) {
        if (e.target && e.target.matches('input[type="radio"]')) {
          recompute();
        }
      });
    });

    recompute();
  }

  function boot() {
    var roots = document.querySelectorAll('.product_section');
    roots.forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

(function () {
  'use strict';

  function initMarquee() {
    var section = document.querySelector('[id*="trust_icon_bar"]');
    if (!section) return;

    var container = section.querySelector('.container');
    if (!container) return;

    var items = container.querySelectorAll('.icon-bar__block');
    if (!items.length) return;

    // Guard against double-init (e.g. theme editor)
    if (container.dataset.marqueeInit) return;
    container.dataset.marqueeInit = '1';

    // Wrap originals in a single track div.
    // CSS overrides :first-child / :last-child padding stripping so every
    // item boundary (including set-to-set) has identical 0.75rem padding.
    var track = document.createElement('div');
    track.className = 'trust-marquee__set';
    track.style.cssText = 'display:inline-flex;align-items:center;flex-shrink:0;';
    Array.from(items).forEach(function (item) { track.appendChild(item); });
    container.appendChild(track);

    // Measure one set after DOM insertion
    var setWidth = track.offsetWidth;
    if (!setWidth) return;

    // Clone until we have 3× viewport width worth of content (ensures no gap at any speed)
    var needed = Math.ceil((window.innerWidth * 3) / setWidth) + 1;
    for (var i = 0; i < needed; i++) {
      container.appendChild(track.cloneNode(true));
    }

    // Inject a keyframe that scrolls exactly one set width (seamless loop)
    if (!document.getElementById('trust-marquee-kf')) {
      var style = document.createElement('style');
      style.id = 'trust-marquee-kf';
      style.textContent = '@keyframes trustMarquee{to{transform:translateX(-' + setWidth + 'px)}}';
      document.head.appendChild(style);
    }

    // Speed: ~50px per second
    var duration = (setWidth / 50).toFixed(2);

    container.style.display = 'inline-flex';
    container.style.flexWrap = 'nowrap';
    container.style.maxWidth = 'none';
    container.style.animation = 'trustMarquee ' + duration + 's linear infinite';

    // Fade in — CSS has opacity:0 on .container to prevent pre-JS layout flash
    container.style.opacity = '1';

    container.addEventListener('mouseenter', function () {
      container.style.animationPlayState = 'paused';
    });
    container.addEventListener('mouseleave', function () {
      container.style.animationPlayState = 'running';
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMarquee);
  } else {
    initMarquee();
  }
})();

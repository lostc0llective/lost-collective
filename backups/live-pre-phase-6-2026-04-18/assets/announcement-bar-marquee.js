(function () {
  'use strict';

  function initAnnouncementMarquee() {
    var bar = document.getElementById('announcement-bar');
    if (!bar) return;

    // Guard against double-init (e.g. theme editor live reload)
    if (bar.dataset.marqueeInit) return;
    bar.dataset.marqueeInit = '1';

    // Find whichever text container is currently visible
    var mobileSlot = bar.querySelector('.is-hidden-desktop-only');
    var desktopSlot = bar.querySelector('.is-hidden-mobile-only');
    var container = (window.innerWidth < 799 && mobileSlot) ? mobileSlot : desktopSlot;
    if (!container) return;

    var source = container.querySelector('p, div');
    if (!source) return;

    var html = source.innerHTML.trim();
    if (!html) return;

    // --- Build the scrolling track ---
    var outer = document.createElement('div');
    outer.style.cssText = 'overflow:hidden;width:100%;display:block;';

    var track = document.createElement('div');
    track.className = 'announcement-marquee__track';
    track.style.cssText = 'display:inline-flex;align-items:center;white-space:nowrap;opacity:0;';

    // Create initial set
    function makeItem() {
      var span = document.createElement('span');
      span.innerHTML = html;
      span.style.cssText = 'flex-shrink:0;padding-left:2.5rem;padding-right:2.5rem;';
      return span;
    }

    var firstSet = makeItem();
    track.appendChild(firstSet);
    outer.appendChild(track);

    // Replace source content
    container.innerHTML = '';
    container.appendChild(outer);

    // Measure after DOM insertion
    requestAnimationFrame(function () {
      var itemWidth = firstSet.offsetWidth;
      if (!itemWidth) { track.style.opacity = '1'; return; }

      // Clone until we have 3× viewport width (guarantees no gap)
      var needed = Math.ceil((window.innerWidth * 3) / itemWidth) + 2;
      for (var i = 0; i < needed; i++) {
        track.appendChild(makeItem());
      }

      // Inject keyframe once
      if (!document.getElementById('announcement-marquee-kf')) {
        var s = document.createElement('style');
        s.id = 'announcement-marquee-kf';
        s.textContent = '@keyframes announcementScroll{from{transform:translateX(-' + itemWidth + 'px)}to{transform:translateX(0)}}';
        document.head.appendChild(s);
      }

      // Respect reduced-motion preference — show static text instead of scrolling
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        track.style.opacity = '1';
        return;
      }

      // Speed: ~55px per second
      var duration = (itemWidth / 55).toFixed(2);
      track.style.animation = 'announcementScroll ' + duration + 's linear infinite';
      track.style.opacity = '1';

      bar.addEventListener('mouseenter', function () {
        track.style.animationPlayState = 'paused';
      });
      bar.addEventListener('mouseleave', function () {
        track.style.animationPlayState = 'running';
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnnouncementMarquee);
  } else {
    initAnnouncementMarquee();
  }
})();

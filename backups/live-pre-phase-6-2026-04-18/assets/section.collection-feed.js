class CollectionFeed extends HTMLElement {
  STICKY_BREAKPOINT = 768;

  constructor() {
    super();
    this.stickyResizeObserver = null;
    this.stickyIntersectionObserver = null;
    this.sentinel = null;
    this.abortController = null;
  }

  connectedCallback() {
    this.abortController = new AbortController();
    this.sticky = this.querySelector('[data-sticky]');

    if (this.sticky) {
      this.initStickyPositioning();
      document.addEventListener(
        'list:hot-reload:updated',
        this.initStickyPositioning.bind(this),
        { signal: this.abortController.signal }
      ); /* from list.hot-reload */
    }
  }

  disconnectedCallback() {
    this.clearObserver('stickyResizeObserver');
    this.clearObserver('stickyIntersectionObserver');
    this.abortController.abort();
  }

  positionSticky() {
    const shouldStick = this.shouldStick();

    if (!shouldStick) {
      this.sticky.setAttribute('data-sticky', 'unstuck');
      this.clearObserver('stickyIntersectionObserver');
    } else if (!this.stickyIntersectionObserver) {
      this.initStickyIntersectionObserver();
    }
  }

  initStickyPositioning() {
    this.clearObserver('stickyResizeObserver');
    this.stickyResizeObserver = new ResizeObserver(this.positionSticky.bind(this));
    this.stickyResizeObserver.observe(this);
    this.positionSticky();
  }

  initStickyIntersectionObserver() {
    this.clearObserver('stickyIntersectionObserver');

    if (!this.sentinel) {
      this.sentinel = document.createElement('div');
      this.sentinel.style.height = '1px';
      this.sentinel.style.marginBottom = '-1px';
      this.sticky.parentElement.insertBefore(this.sentinel, this.sticky);
    }

    this.stickyIntersectionObserver = new IntersectionObserver(([entry]) => {
      if (entry.boundingClientRect.top < 0 && !entry.isIntersecting) {
        this.sentinel.style.marginBottom = `${this.sticky.offsetHeight - 1}px`;
        this.sticky.setAttribute('data-sticky', 'stuck');
      } else {
        this.sentinel.style.marginBottom = '-1px';
        this.sticky.setAttribute('data-sticky', 'unstuck');
      }
    });

    this.stickyIntersectionObserver.observe(this.sentinel);
  }

  clearObserver(observerKey) {
    if (!this[observerKey]) return;
    this[observerKey].disconnect();
    this[observerKey] = null;
  }

  shouldStick() {
    return this.sticky && window.matchMedia(`(width < ${this.STICKY_BREAKPOINT}px)`).matches;
  }
}

customElements.define('collection-feed', CollectionFeed);

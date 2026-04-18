import noUiSlider from 'vendor.nouislider';

class PriceRange extends HTMLElement {
  constructor() {
    super();
    this.slider = null;
  }

  connectedCallback() {
    this.sliderEl = this.querySelector('.price-range__slider');
    this.inputMinEl = this.querySelector('.price-range__input-min input');
    this.inputMaxEl = this.querySelector('.price-range__input-max input');

    this.minRange = parseFloat(this.getAttribute('min')) || 0;
    this.minValue = parseFloat(this.getAttribute('min-value')) || 0;
    this.maxRange = parseFloat(this.getAttribute('max')) || 100;
    this.maxValue = parseFloat(this.getAttribute('max-value')) || this.maxRange;
    this.hotReload = this.getAttribute('hot-reload') === 'true';

    this.direction = getComputedStyle(this).direction;

    this.createPriceRange();
  }

  disconnectedCallback() {
    if (this.slider) {
      this.slider.destroy();
      this.slider = null;
    }
  }

  createPriceRange() {
    if (this.slider) this.slider.destroy();

    this.slider = noUiSlider.create(this.sliderEl, {
      connect: true,
      direction: this.direction,
      start: [this.minValue, this.maxValue],
      range: {
        min: this.minRange,
        max: this.maxRange,
      },
    });

    this.setupSliderHandling();
    this.setupInputHandling();
  }

  setupSliderHandling() {
    // Update input values on slider change
    this.slider.on('update', (values, handle) => {
      const [min, max] = values.map(value => parseInt(value, 10));
      const inputMinValue = parseInt(this.inputMinEl.value, 10);
      const inputMaxValue = parseInt(this.inputMaxEl.value, 10);

      // Stop if slider values are the same as the input values
      if (min === inputMinValue && max === inputMaxValue) return;

      const inputEl = handle === 0 ? this.inputMinEl : this.inputMaxEl;
      const value = handle === 0 ? min : max;

      inputEl.value = value;
      if (this.hotReload) {
        inputEl.dispatchEvent(new Event(
          'list:price-range:slider-change',
          { bubbles: true }
        ));
      }
    });
  }

  setupInputHandling() {
    // Update slider on input change
    this.addEventListener('change', (event) => {
      const inputEl = event.target;

      if (!this.isPriceRangeInput(inputEl)) return;
      const [min, max] = this.slider.get(true);
      const value = parseInt(inputEl.value, 10);

      if (inputEl === this.inputMinEl && value !== min) {
        this.slider.set([value, null]);
      } else if (inputEl === this.inputMaxEl && value !== max) {
        this.slider.set([null, value]);
      }

      if (!this.hotReload) event.stopPropagation();
    });

    // Select input value on click (input cleared on typing)
    this.addEventListener('click', (e) => {
      if (this.isPriceRangeInput(e.target)) {
        e.target.select();
      }
    });
  }

  isPriceRangeInput(target) {
    return target === this.inputMinEl || target === this.inputMaxEl;
  }
}

customElements.define('price-range', PriceRange);

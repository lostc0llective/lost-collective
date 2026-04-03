/******/ (() => { // webpackBootstrap
var __webpack_exports__ = {};
window.PXUTheme.jsFixedMessage = {
  init: function ($section) {

    this.$el = $('.fixed-message-section');
    let fixedMessageCookie = Cookies.get('fixed-message');

    if (fixedMessageCookie !== 'dismiss') {
      this.$el.removeClass('is-hidden');

      // Attach event to hide fixed message if button is clicked
      $('.js-close-fixed-message').on('click', () => {
        this.hide();
      });

    }

  },
  hide: function () {
    this.$el.addClass('is-hidden');
    // Remove fixed message and set cookie to hide it for 30 days
    Cookies.set('fixed-message', 'dismiss', { expires: 30 });

    // Update Google Consent Mode v2 — grants all storage on explicit user acceptance
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        'analytics_storage': 'granted',
        'ad_storage': 'granted',
        'ad_user_data': 'granted',
        'ad_personalization': 'granted'
      });
    }

    // Update Shopify Customer Privacy API — signals consent to Shopify's native systems
    if (window.Shopify && window.Shopify.customerPrivacy) {
      window.Shopify.customerPrivacy.setTrackingConsent(
        { marketing: true, analytics: true, preferences: true, sale_of_data: true },
        function() {}
      );
    }

  },
  unload: function ($section) {

    // Clear event listeners in theme editor
    $('.js-close-fixed-message').off();
  }
}

/******/ })()
;

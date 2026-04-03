/******/ (() => { // webpackBootstrap
var __webpack_exports__ = {};
window.PXUTheme.jsVideo = {
  init: function ($section) {

    // Add settings from schema to current object
    window.PXUTheme.jsVideo = $.extend(this, window.PXUTheme.getSectionData($section));

    // Selectors
    const $videoElement = $section.find('[data-video-element]');
    const $playIcon = $section.find('.plyr--paused.plyr--video .plyr__control--overlaid');
    const $playButton = $section.find('[data-play-button]');
    const $videoTextContainer = $section.find('[data-video-text-container]');
    const $imageElement = $section.find('[data-image-element]');

    // Load video if the media has been added
    if (this.iframe_video || this.html5_video) {
      this.loadVideo($videoElement, $playIcon, $playButton, $videoTextContainer, $imageElement);
    } else {
      $imageElement.show();
    }

  },
  loadVideo: function($videoElement, $playIcon, $playButton, $videoTextContainer, $imageElement) {
    const self = this;
    const shouldAutoplay = this.autoplay;
    const hasPoster = this.poster;

    // Activate facade: move data-src → src on iframe, then init Plyr
    const activatePlayer = () => {
      const $iframe = $videoElement.find('iframe[data-src]');
      if ($iframe.length) {
        $iframe.attr('src', $iframe.data('src')).removeAttr('data-src');
      }
      initPlyr();
    };

    const initPlyr = () => {
      const player = new Plyr(`.video-${self.id}`, {
        controls: videoControls,
        loop: {
          active: self.autoloop
        },
        fullscreen: {
          enabled: true,
          fallback: true,
          iosNative: true
        },
        storage: {
          enabled: false
        }
      });

      player.muted = self.mute;
      player.ratio = self.aspect_ratio;

      // Capture the Plyr-generated wrapper (.plyr) so we can hide it independently
      // of $videoElement — Plyr wraps the original element in its own container which
      // remains visible (and shows black) even when $videoElement is hidden.
      const $plyrWrapper = $(player.elements.container);

      if (shouldAutoplay) {
        player.autoplay = true;
        $videoElement.hide();
        $plyrWrapper.hide();
      }

      // If button exists, clicking button will play video
      if (self.button) {
        $playButton.on('click', () => {
          player.play();
        });
      }

      // Clicking anywhere on video should play the video
      if (!self.button) {
        $videoTextContainer.on('click', () => {
          player.play();
        });
      }

      // If on mobile and text is below image, clicking the image wrapper should play the video
      if (!isScreenSizeLarge() && $videoElement.parents('.mobile-text--below-media')) {
        $imageElement.on('click', () => {
          player.play();
        });
      }

      // On player ready, hide play icon if play button visible; trigger autoplay
      player.on('ready', function(index, player) {
        if ($playButton && !isScreenSizeLarge() && $videoElement.parents('.mobile-text--below-media')) {
          $playIcon.show();
        } else if ($playButton) {
          $playIcon.hide();
        } else {
          $playIcon.show();
        }
        if (shouldAutoplay) {
          player.play();
        }
      });

      // On play, cross-fade poster out and video in (300ms opacity transition).
      // $plyrWrapper must be shown alongside $videoElement because Plyr wraps
      // $videoElement inside it — showing $videoElement alone has no effect if
      // the outer .plyr container is still display:none.
      player.on('play', function(index, player) {
        $videoTextContainer.hide();
        $imageElement.fadeOut(300);
        $videoElement.show();
        $plyrWrapper.css('opacity', 0).show().animate({ opacity: 1 }, 300);
      });

      // On player pause, show play icon if play button hidden
      player.on('pause', function(index, player) {
        if (!$playButton) {
          $playIcon.show();
        }
      });

      if (shouldAutoplay) {
        player.play();
      }
    };

    // Facade pattern: defer iframe + Plyr load until user interaction when a
    // poster image is set and autoplay is off. Autoplay bypasses the facade.
    if (shouldAutoplay) {
      activatePlayer();
      $videoElement.hide();
    } else if (hasPoster) {
      // Show poster; activate player only when user interacts
      $imageElement.show();
      $videoTextContainer.show();

      const onUserInteract = () => {
        $imageElement.off('click', onUserInteract);
        $videoTextContainer.off('click', onUserInteract);
        $playButton.off('click', onUserInteract);
        activatePlayer();
      };

      $imageElement.one('click', onUserInteract);
      if (self.button) {
        $playButton.one('click', onUserInteract);
      } else {
        $videoTextContainer.one('click', onUserInteract);
      }
    } else {
      // No poster — activate immediately, show video element
      activatePlayer();
      $imageElement.hide();
      $videoElement.show();
      $videoTextContainer.show();
    }

  },
  unload: function($section) {
    const $playButton = $section.find('[data-play-button]');
    const $videoTextContainer = $section.find('[data-video-text-container]');

    $playButton.off();
    $videoTextContainer.off();
  }
}

/******/ })()
;

// Set data-count attribute for CSS Grid layout
// Styling is now handled via CSS using data-count selector in custom.css
document.addEventListener('DOMContentLoaded', function () {
  var sizeElements = document.querySelectorAll('.swatch__options.custom-size, .swatch__options.custom-type, .swatch__options.custom-colour');
  sizeElements.forEach(function (sizeElement) {
    var childCount = sizeElement.children.length;
    sizeElement.setAttribute('data-count', childCount);
  });
});

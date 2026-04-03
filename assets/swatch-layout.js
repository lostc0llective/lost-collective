document.addEventListener('DOMContentLoaded', function () {
  var sizeElements = document.querySelectorAll('.swatch__options.custom-size, .swatch__options.custom-type, .swatch__options.custom-colour');
  sizeElements.forEach(function (sizeElement) {
    var childCount = sizeElement.children.length;
    sizeElement.style.cssText = 'display: flex; width: 100%;';
    Array.from(sizeElement.children).forEach(function (child) {
      child.style.flex = '0 0 calc(' + (100 / childCount) + '% - 10px)';
    });
  });
});

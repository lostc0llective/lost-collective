const optionSelectors = document.querySelectorAll('[data-variant-option]');

// Watch for changes
optionSelectors.forEach((select) => {
  select.addEventListener('change', function (event) {
    const selectedOption = select.value;
  });
});

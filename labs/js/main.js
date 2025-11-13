// main.js – navigation + fade transitions

function nav(url) {
  document.body.classList.remove('fade-in');
  document.body.classList.add('fade-out');
  setTimeout(function () {
    window.location.href = url;
  }, 180);
}

// Ensure fade-in runs on entry, including back/forward navigation
window.addEventListener('pageshow', function () {
  document.body.classList.remove('fade-out');
  document.body.classList.add('fade-in');
});

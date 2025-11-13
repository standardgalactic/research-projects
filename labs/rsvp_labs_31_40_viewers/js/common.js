
function nav(url){
  document.body.classList.remove('fade-in');
  document.body.classList.add('fade-out');
  setTimeout(function(){ window.location.href = url; }, 160);
}
window.addEventListener('pageshow', function(){
  document.body.classList.add('fade-in');
});

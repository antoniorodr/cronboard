document$.subscribe(function() {
  /* Tab switching */
  var tabs = document.querySelectorAll('.tab');
  if (tabs.length > 0) {
    tabs.forEach(function(tab) {
      var clone = tab.cloneNode(true);
      tab.parentNode.replaceChild(clone, tab);
      clone.addEventListener('click', function() {
        var target = clone.getAttribute('data-tab');
        document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
        document.querySelectorAll('.install-panel').forEach(function(p) { p.classList.remove('active'); });
        clone.classList.add('active');
        document.querySelector('[data-panel="' + target + '"]').classList.add('active');
      });
    });
  }

  /* Copy buttons */
  var copyBtns = document.querySelectorAll('.term-copy');
  if (copyBtns.length > 0) {
    copyBtns.forEach(function(btn) {
      var clone = btn.cloneNode(true);
      btn.parentNode.replaceChild(clone, btn);
      clone.addEventListener('click', function(e) {
        e.stopPropagation();
        var text = clone.getAttribute('data-copy');
        navigator.clipboard.writeText(text);
        clone.classList.add('copied');
        setTimeout(function() { clone.classList.remove('copied'); }, 1200);
      });
    });
  }

  /* Copy all button */
  var copyAllBtns = document.querySelectorAll('.term-copy-all-btn');
  if (copyAllBtns.length > 0) {
    copyAllBtns.forEach(function(btn) {
      var clone = btn.cloneNode(true);
      btn.parentNode.replaceChild(clone, btn);
      clone.addEventListener('click', function(e) {
        e.stopPropagation();
        var text = clone.getAttribute('data-copy');
        navigator.clipboard.writeText(text);
        clone.classList.add('copied');
        setTimeout(function() { clone.classList.remove('copied'); }, 1200);
      });
    });
  }
});

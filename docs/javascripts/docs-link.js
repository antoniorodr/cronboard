document$.subscribe(function() {
  if (!document.querySelector('.cronboard-home')) return;

  var headerInner = document.querySelector('.md-header__inner');
  if (headerInner && !document.querySelector('.md-header__docs-link')) {
    var link = document.createElement('a');
    link.href = 'installation/';
    link.className = 'md-header__docs-link';
    link.innerHTML = '<svg width="16" height="16" fill="currentColor"><use href="images/sprites.svg#icon-docs"/></svg><span>Docs</span>';
    var palette = headerInner.querySelector('.md-header__option');
    if (palette) {
      headerInner.insertBefore(link, palette);
    } else {
      headerInner.appendChild(link);
    }
  }
});

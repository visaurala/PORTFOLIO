/* =========================================================
   GALLERY — fills thumb grids from data attributes + lightbox
   Usage:
   <div class="thumb-grid cols-3"
        data-folder="images/bramblefort/characters"
        data-files="01.png, 02.png, 03.png"
        data-alt="Bramblefort character"></div>
   Files that don't exist are quietly skipped.
   Clicking a thumb opens the original file in the lightbox.
   ========================================================= */
(function () {
  'use strict';

  /* ---------- build grids ---------- */
  var grids = document.querySelectorAll('.thumb-grid[data-files]');
  Array.prototype.forEach.call(grids, function (grid) {
    var folder = (grid.getAttribute('data-folder') || '').replace(/\/+$/, '');
    var alt = grid.getAttribute('data-alt') || '';
    grid.getAttribute('data-files').split(',').forEach(function (name) {
      name = name.trim();
      if (!name) return;
      var url = (folder ? folder + '/' : '') + encodeURIComponent(name);
      var a = document.createElement('a');
      a.href = url;
      a.setAttribute('data-full', '');
      var img = new Image();
      img.loading = 'lazy';
      img.decoding = 'async';
      img.alt = alt;
      img.src = url;
      img.onerror = function () {
        if (a.parentNode) a.parentNode.removeChild(a);
      };
      a.appendChild(img);
      grid.appendChild(a);
    });
  });

  /* ---------- lightbox ---------- */
  var box = document.createElement('div');
  box.className = 'lightbox';
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-modal', 'true');
  box.innerHTML =
    '<img class="lightbox-img" alt="">' +
    '<div class="lightbox-bar">' +
    '<button type="button" data-act="prev">[ PREV ]</button>' +
    '<span class="lightbox-count"></span>' +
    '<button type="button" data-act="next">[ NEXT ]</button>' +
    '<button type="button" data-act="close">[ CLOSE ]</button>' +
    '</div>';
  document.body.appendChild(box);

  var big = box.querySelector('.lightbox-img');
  var count = box.querySelector('.lightbox-count');
  var list = [];
  var index = 0;

  function show() {
    var a = list[index];
    var thumb = a.querySelector('img');
    big.src = a.href;
    big.alt = thumb ? thumb.alt : '';
    count.textContent = (index + 1) + ' / ' + list.length;
  }
  function open(group, i) {
    list = group;
    index = i;
    show();
    box.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    box.classList.remove('open');
    big.removeAttribute('src');
    document.body.style.overflow = '';
  }
  function step(d) {
    index = (index + d + list.length) % list.length;
    show();
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('.thumb-grid a[data-full], a.feature-image[data-full]') : null;
    if (a) {
      e.preventDefault();
      var scope = a.closest('.work-box') || a.parentNode;
      var group = Array.prototype.slice.call(scope.querySelectorAll('a[data-full]'));
      open(group, group.indexOf(a));
      return;
    }
    if (!box.classList.contains('open')) return;
    var act = e.target.getAttribute && e.target.getAttribute('data-act');
    if (act === 'prev') step(-1);
    else if (act === 'next') step(1);
    else if (act === 'close' || e.target === box) close();
  });

  document.addEventListener('keydown', function (e) {
    if (!box.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') step(-1);
    else if (e.key === 'ArrowRight') step(1);
  });
})();

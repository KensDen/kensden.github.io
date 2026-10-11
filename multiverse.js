/* multiverse.js: decorative motion for multiverse-control-plane.html; without it every figure
   is still. No network, eval or innerHTML. */
(function () {
  'use strict';
  var doc = document;
  doc.documentElement.classList.add('js');
  function $$(sel, el) { return [].slice.call((el || doc).querySelectorAll(sel)); }

  /* One-shots (prune/grow, badge vs behavior): CSS keyed to .run; replay restarts them. */
  function start(fig) { fig.classList.remove('run'); void fig.offsetWidth; fig.classList.add('run'); }
  $$('.replay').forEach(function (b) {
    b.addEventListener('click', function () { start(b.closest('figure')); });
  });

  /* .in-view runs loops (CSS pauses them off screen); one-shots start once at 35%. */
  var figs = $$('[data-anim]'), begun = [];
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var f = e.target;
        f.classList.toggle('in-view', e.isIntersecting);
        if (f.dataset.anim === 'once' && e.intersectionRatio >= 0.35 && begun.indexOf(f) < 0) {
          begun.push(f);
          start(f);
        }
      });
    }, { threshold: [0, 0.35] });
    figs.forEach(function (f) { io.observe(f); });
  } else figs.forEach(function (f) { if (f.dataset.anim === 'once') start(f); });

  /* 3. Stack <-> table: hover or tap lights a layer in both. */
  var lit = null;
  function light(n) {
    if (n === lit) return;
    lit = /^[1-6]$/.test(n) ? n : null;
    $$('[data-l]').forEach(function (el) { el.classList.toggle('hl', el.dataset.l === lit); });
  }
  $$('[data-l]').forEach(function (el) {
    function hover(e) { if (e.pointerType === 'mouse') light(e.type === 'pointerenter' ? el.dataset.l : null); }
    el.addEventListener('pointerenter', hover);
    el.addEventListener('pointerleave', hover);
  });
  /* Taps via pointerup: iOS sends no click for these. */
  var down = null;
  doc.addEventListener('pointerdown', function (e) { down = e; }, true);
  doc.addEventListener('pointerup', function (e) {
    if (!down || e.pointerType === 'mouse' || Math.abs(e.clientX - down.clientX) + Math.abs(e.clientY - down.clientY) > 10) return;
    var row = e.target.closest('[data-l]');
    light(row && row.dataset.l !== lit ? row.dataset.l : null);
  });

  /* 4. Tune the Orrery: the chips are a radiogroup (arrows move), the card is aria-live,
     and a tap on one of the nine dots picks it. Card text comes from the no-JS list. */
  var tune = doc.querySelector('.tune');
  if (tune) {
    var chips = $$('[role=radio]', tune), items = $$('.tune-list li', tune), svg = tune.querySelector('svg');
    var card = tune.querySelector('.tune-card'), halo = tune.querySelector('.sel-halo');
    var dotOf = function (c) { return /^\d+$/.test(c.dataset.e) && tune.querySelector('.dot[data-e="' + c.dataset.e + '"]'); };
    var pick = function (k, focus) {
      var dot = dotOf(chips[k]), li = items[k];
      if (!dot || !li) return;
      chips.forEach(function (c, j) { c.setAttribute('aria-checked', j === k); c.tabIndex = j === k ? 0 : -1; });
      $$('.dot.sel', tune).forEach(function (d) { d.classList.remove('sel'); });
      dot.classList.add('sel');
      halo.setAttribute('cx', dot.getAttribute('cx'));
      halo.setAttribute('cy', dot.getAttribute('cy'));
      card.querySelector('.tc-h').textContent = li.querySelector('.tc-h').textContent;
      card.querySelector('.tc-d').textContent = li.querySelector('.tc-d').textContent;
      if (focus) chips[k].focus();
    };
    chips.forEach(function (c, j) {
      c.addEventListener('click', function () { pick(j); });
      c.addEventListener('keydown', function (e) {
        var n = chips.length, d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        var to = d ? (j + d + n) % n : e.key === 'Home' ? 0 : e.key === 'End' ? n - 1 : -1;
        if (to >= 0) { e.preventDefault(); pick(to, true); }
      });
    });
    svg.addEventListener('click', function (e) { // a tap near one of the nine dots picks it
      var m = svg.getScreenCTM(), best = -1, bd = 784; // within 28 units
      if (!m) return;
      var p = new DOMPoint(e.clientX, e.clientY).matrixTransform(m.inverse());
      chips.forEach(function (c, j) {
        var d = dotOf(c), dx = d ? d.cx.baseVal.value - p.x : 1e9, dy = d ? d.cy.baseVal.value - p.y : 0;
        if (dx * dx + dy * dy < bd) { bd = dx * dx + dy * dy; best = j; }
      });
      if (best >= 0) pick(best);
    });
  }
})();

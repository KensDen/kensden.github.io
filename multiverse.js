/* multiverse.js: decorative motion for multiverse-control-plane.html; without it every figure
   is still. No network, eval or innerHTML. */
(function () {
  'use strict';
  var doc = document;
  doc.documentElement.classList.add('js');
  var mq = window.matchMedia && matchMedia('(prefers-reduced-motion: no-preference)');
  function moving() { return !!(mq && mq.matches); }
  function $$(sel, el) { return [].slice.call((el || doc).querySelectorAll(sel)); }

  /* 2. Audit log: type a hidden copy; the real <pre> stays for readers. */
  function typer(fig) {
    var pre = fig.querySelector('.alog'), vis = pre.cloneNode(true), chars = [], at = 0, gap = 0, raf = 0;
    var narrow = matchMedia('(max-width: 519.98px)').matches; // phone layout
    vis.classList.add('alog-v');
    vis.setAttribute('aria-hidden', 'true');
    $$('.ln', vis).forEach(function (ln, i) {
      if (i) gap += 90; // a beat per line
      if (ln.classList.contains('bad')) gap += 600; // Mandrakk hesitates
      var walk = doc.createTreeWalker(ln, NodeFilter.SHOW_TEXT), nodes = [], t;
      while ((t = walk.nextNode())) nodes.push(t);
      nodes.forEach(function (node) {
        var frag = doc.createDocumentFragment(), skip = narrow && node.parentNode.closest('.px');
        for (var k = 0; k < node.data.length; k++) {
          var c = frag.appendChild(doc.createElement('span'));
          c.textContent = node.data[k];
          if (!skip) { at += 7 + gap; gap = 0; } // pause on visible chars
          chars.push({ el: c, at: at });
        }
        node.parentNode.replaceChild(frag, node);
      });
    });
    function paint(cls) { chars.forEach(function (c) { c.el.className = cls; }); }
    paint('h');
    pre.after(vis); // same size, no shift
    pre.classList.add('sr-only'); // after the copy
    return {
      play: function () {
        cancelAnimationFrame(raf);
        fig.classList.remove('done', 'pulse');
        paint('h');
        var i = 0, t0 = performance.now(), cur = null;
        (function step(now) {
          while (i < chars.length && chars[i].at <= now - t0) chars[i++].el.className = '';
          if (cur) cur.classList.remove('cur');
          if (i < chars.length) {
            (cur = chars[i].el).classList.add('cur'); // block cursor
            raf = requestAnimationFrame(step);
          } else fig.classList.add('done', 'pulse');
        })(t0);
      },
      finish: function () { cancelAnimationFrame(raf); paint(''); fig.classList.add('done'); }
    };
  }
  var auditFig = doc.querySelector('.audit'), log = null;
  function getLog() {
    try { if (!log && auditFig) log = typer(auditFig); } catch (err) { log = null; }
    return log;
  }
  if (moving()) getLog();

  /* One-shots: prune/grow and the log. */
  function start(fig) {
    if (fig !== auditFig) { fig.classList.remove('run'); void fig.offsetWidth; fig.classList.add('run'); }
    else if (moving()) { if (getLog()) log.play(); }
    else if (log) log.finish();
  }
  if (mq && mq.addEventListener) mq.addEventListener('change', function () { if (!moving() && log) log.finish(); });
  $$('.replay').forEach(function (b) {
    b.addEventListener('click', function () { start(b.closest('figure')); });
  });

  /* .in-view runs loops; one-shots start once at 35%. */
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

  /* 4. Orrery readout: the dot nearest the pointer. */
  var orr = doc.querySelector('.orrery svg'), out = doc.querySelector('.orr-out');
  var dots = orr ? $$('.dot', orr) : [], base = out ? out.textContent : '', on = -1;
  function show(i) {
    if (i === on) return;
    if (on >= 0) dots[on].classList.remove('on');
    if ((on = i) >= 0) dots[i].classList.add('on');
    out.textContent = i < 0 ? base : '> earth-' + i + ': tenant ' + i + ' of 52_';
  }
  function nearest(e) {
    var m = orr.getScreenCTM(), best = -1, bd = 784; // 28 units
    if (!m) return -1;
    var p = new DOMPoint(e.clientX, e.clientY).matrixTransform(m.inverse());
    dots.forEach(function (d, i) {
      var dx = d.cx.baseVal.value - p.x, dy = d.cy.baseVal.value - p.y;
      if (dx * dx + dy * dy < bd) { bd = dx * dx + dy * dy; best = i; }
    });
    return best;
  }
  function track(e) { if (e.pointerType === 'mouse') show(e.type === 'pointerleave' ? -1 : nearest(e)); }
  if (orr && out) { orr.addEventListener('pointermove', track); orr.addEventListener('pointerleave', track); }

  /* Taps via pointerup: iOS sends no click for these. */
  var down = null;
  doc.addEventListener('pointerdown', function (e) { down = e; }, true);
  doc.addEventListener('pointerup', function (e) {
    if (!down || e.pointerType === 'mouse' || Math.abs(e.clientX - down.clientX) + Math.abs(e.clientY - down.clientY) > 10) return;
    var row = e.target.closest('[data-l]');
    light(row && row.dataset.l !== lit ? row.dataset.l : null);
    if (orr && out) show(orr.contains(e.target) ? nearest(e) : -1);
  });
})();

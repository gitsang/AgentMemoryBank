/* Reader UI for the book page: glossary popovers and visibility toggles. */
(function () {
  'use strict';

  /* ---------------------------------------------------------- toggles --- */
  function setupToggle(btnId, hideClass, storageKey, fallback) {
    var btn = document.getElementById(btnId);
    if (!btn) return;
    var label = btn.getAttribute('data-label') || fallback;
    var tip = btn.querySelector('.tool-tip');
    function apply(hidden) {
      document.body.classList.toggle(hideClass, hidden);
      btn.classList.toggle('is-off', hidden);
      btn.setAttribute('aria-pressed', String(!hidden));
      var state = hidden ? '\u663e\u793a' : '\u9690\u85cf';
      btn.setAttribute('aria-label', label + '\uff1a' + state);
      if (tip) tip.textContent = state + label;
    }
    var hidden = false;
    try { hidden = localStorage.getItem(storageKey) === 'off'; } catch (e) {}
    apply(hidden);
    btn.addEventListener('click', function () {
      hidden = !document.body.classList.contains(hideClass);
      apply(hidden);
      try { localStorage.setItem(storageKey, hidden ? 'off' : 'on'); } catch (e) {}
    });
  }

  setupToggle('trToggle', 'no-tr', 'tlb-csi-translation', '\u4e2d\u6587');
  setupToggle('noteToggle', 'no-notes', 'tlb-csi-notes', '\u6279\u6ce8');

  /* ------------------------------------------------ chapter rail ------ */
  var rail = document.getElementById('rail');
  if (rail && 'IntersectionObserver' in window) {
    var links = {};
    Array.prototype.forEach.call(rail.querySelectorAll('a'), function (a) {
      links[a.getAttribute('href').slice(1)] = a;
    });
    var active = null;
    function activate(id) {
      var a = links[id];
      if (!a || a === active) return;
      if (active) active.classList.remove('is-active');
      active = a;
      a.classList.add('is-active');
      var top = a.offsetTop;
      if (top < rail.scrollTop ||
          top > rail.scrollTop + rail.clientHeight - 32) {
        rail.scrollTop = top - rail.clientHeight / 2;
      }
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) activate(en.target.id);
      });
    }, { rootMargin: '-12% 0px -72% 0px' });
    Object.keys(links).forEach(function (id) {
      var sec = document.getElementById(id);
      if (sec) observer.observe(sec);
    });
  }

  /* --------------------------------------------------------- glossary --- */
  var holder = document.getElementById('glossary-data');
  if (!holder) return;

  var terms;
  try { terms = JSON.parse(holder.textContent).terms; } catch (e) { return; }
  if (!terms || !terms.length) return;

  var byId = {};
  terms.forEach(function (t) { byId[t.id] = t; });

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  // One pattern per term, aliases folded in, longest alternative first.
  var patterns = terms.map(function (t) {
    var forms = [t.en].concat(t.aliases || [])
      .sort(function (a, b) { return b.length - a.length; })
      .map(escapeRe);
    return {
      id: t.id,
      weight: Math.max.apply(null, forms.map(function (f) { return f.length; })),
      re: new RegExp('\\b(?:' + forms.join('|') + ')\\b')
    };
  }).sort(function (a, b) { return b.weight - a.weight; });

  var SKIP = 'a,button,sup,figcaption,nav,header,footer,script,style,.tr,' +
             '.sidenote,.chapter-label,.box-title,.note-num,.glossary-pop,' +
             'h1,h2,h3,h4,h5,h6';

  function eligible(node) {
    if (!node.nodeValue || !node.nodeValue.trim()) return false;
    var parent = node.parentElement;
    return !!parent && !parent.closest(SKIP);
  }

  function firstMatchNode(root, re) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var node;
    while ((node = walker.nextNode())) {
      if (eligible(node) && re.test(node.nodeValue)) return node;
    }
    return null;
  }

  function wrap(node, re, id) {
    var m = re.exec(node.nodeValue);
    if (!m) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'term';
    btn.setAttribute('data-term', id);
    btn.textContent = m[0];
    var parent = node.parentNode;
    parent.insertBefore(document.createTextNode(node.nodeValue.slice(0, m.index)), node);
    parent.insertBefore(btn, node);
    parent.insertBefore(document.createTextNode(node.nodeValue.slice(m.index + m[0].length)), node);
    parent.removeChild(node);
  }

  // First occurrence of each term per section keeps the page from turning into
  // a wall of dotted underlines, while every chapter still gets its own hints.
  Array.prototype.forEach.call(document.querySelectorAll('section'), function (sec) {
    var used = Object.create(null);
    patterns.forEach(function (p) {
      if (used[p.id]) return;
      var node = firstMatchNode(sec, p.re);
      if (!node) return;
      wrap(node, p.re, p.id);
      used[p.id] = true;
    });
  });

  var pop = document.createElement('div');
  pop.className = 'glossary-pop';
  pop.setAttribute('role', 'dialog');
  pop.hidden = true;
  document.body.appendChild(pop);
  var active = null;

  function close() {
    pop.hidden = true;
    if (active) active.classList.remove('is-open');
    active = null;
  }

  function open(btn) {
    var t = byId[btn.getAttribute('data-term')];
    if (!t) return;
    if (active === btn) { close(); return; }
    if (active) active.classList.remove('is-open');
    active = btn;
    btn.classList.add('is-open');

    pop.textContent = '';
    var en = document.createElement('div');
    en.className = 'gp-en';
    en.textContent = t.en;
    var zh = document.createElement('div');
    zh.className = 'gp-zh';
    zh.textContent = t.zh;
    var note = document.createElement('div');
    note.className = 'gp-note';
    note.textContent = t.note;
    pop.appendChild(en);
    pop.appendChild(zh);
    pop.appendChild(note);

    pop.hidden = false;
    var r = btn.getBoundingClientRect();
    var maxLeft = window.scrollX + document.documentElement.clientWidth
                  - pop.offsetWidth - 12;
    pop.style.top = (r.bottom + window.scrollY + 8) + 'px';
    pop.style.left = Math.max(12 + window.scrollX,
                              Math.min(r.left + window.scrollX, maxLeft)) + 'px';
  }

  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest && ev.target.closest('.term');
    if (btn) { open(btn); return; }
    if (!pop.contains(ev.target)) close();
  });

  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') close();
  });
})();

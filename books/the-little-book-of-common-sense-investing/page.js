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

  /* ------------------------------------------ chapter navigation ------ */
  // The fixed rail (wide screens) and the <details> menu (narrow screens)
  // carry the same links, so the highlight is driven through one mechanism
  // for whichever of them is present.
  var menus = ['rail', 'tocDrop'].map(function (id) {
    return document.getElementById(id);
  }).filter(Boolean);

  if (menus.length) {
    var linksById = {};
    menus.forEach(function (menu) {
      Array.prototype.forEach.call(
        menu.querySelectorAll('a[href^="#"]'), function (a) {
          var id = a.getAttribute('href').slice(1);
          if (!document.getElementById(id)) return;
          (linksById[id] = linksById[id] || []).push(a);
        });
    });

    // document order, so the scan can stop at the first section still below
    // the reading line
    var sections = Array.prototype.filter.call(
      document.querySelectorAll('section'),
      function (sec) { return linksById[sec.id]; });

    var activeId = null;
    function activate(id) {
      if (id === activeId || !linksById[id]) return;
      if (activeId && linksById[activeId]) {
        linksById[activeId].forEach(function (a) {
          a.classList.remove('is-active');
        });
      }
      activeId = id;
      linksById[id].forEach(function (a) {
        a.classList.add('is-active');
        var box = a.closest('.rail');
        if (!box) return;
        var top = a.offsetTop;
        if (top < box.scrollTop ||
            top > box.scrollTop + box.clientHeight - 32) {
          box.scrollTop = top - box.clientHeight / 2;
        }
      });
    }

    // The current section is the last one whose top has crossed the reading
    // line. Recomputed from position on every scroll rather than latched when
    // an observer fires, so a jumped-to or previously-visited chapter cannot
    // keep the highlight.
    var ticking = false;
    function update() {
      ticking = false;
      var line = window.innerHeight * 0.28;
      var found = sections[0];
      for (var i = 0; i < sections.length; i++) {
        if (sections[i].getBoundingClientRect().top <= line) {
          found = sections[i];
        } else {
          break;
        }
      }
      if (found) activate(found.id);
    }
    function request() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    update();

    // navigating from the menu should not leave it hanging open
    var drop = document.getElementById('tocDrop');
    if (drop) {
      drop.addEventListener('click', function (ev) {
        if (ev.target.closest && ev.target.closest('a')) drop.open = false;
      });
    }
  }

  /* ------------------------------------------------- glossary dialog --- */
  var glossBtn = document.getElementById('glossToggle');
  var glossModal = document.getElementById('glossaryModal');
  if (glossBtn && glossModal) {
    var glossFilter = document.getElementById('gmFilter');
    var glossEmpty = document.getElementById('gmEmpty');
    var glossEntries = Array.prototype.slice.call(
      glossModal.querySelectorAll('.gl-entry'));

    function filterGlossary() {
      if (!glossFilter) return;
      var q = glossFilter.value.trim().toLowerCase();
      var shown = 0;
      glossEntries.forEach(function (el) {
        var hay = el.getAttribute('data-term') || '';
        var hit = !q || hay.indexOf(q) >= 0;
        el.hidden = !hit;
        if (hit) shown++;
      });
      if (glossEmpty) glossEmpty.hidden = shown > 0;
    }

    function setGlossary(open) {
      glossModal.hidden = !open;
      glossBtn.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('gm-open', open);
      if (open) {
        if (glossFilter) { glossFilter.value = ''; filterGlossary(); }
        if (glossFilter) glossFilter.focus();
      } else {
        glossBtn.focus();
      }
    }

    glossBtn.addEventListener('click', function (ev) {
      ev.stopPropagation();
      setGlossary(glossModal.hidden);
    });
    glossModal.addEventListener('click', function (ev) {
      if (ev.target.closest && ev.target.closest('[data-gm-close]')) {
        setGlossary(false);
      }
    });
    if (glossFilter) glossFilter.addEventListener('input', filterGlossary);
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && !glossModal.hidden) setGlossary(false);
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

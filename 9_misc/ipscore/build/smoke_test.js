#!/usr/bin/env node
// Functional smoke test: run buildPages()+fillDemo() (or just buildPages() for the
// blank form) in a sandboxed DOM close enough to a real browser to compute the
// actual IPscore/VAN, and print the results. Run against both the original and the
// regenerated file to compare -- this is the real correctness check, since a raw
// text diff will legitimately differ (JSON array formatting) without being wrong.
const fs = require('fs');
const vm = require('vm');

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function noop() { return undefined; }
const elementsById = new Map();
function stubCanvasCtx() {
  const ctx = {};
  return new Proxy(ctx, { get: () => noop });
}
function makeEl(id) {
  const el = {
    className: '', style: {}, innerHTML: '', checked: false, textContent: '',
    classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
    addEventListener: noop, appendChild: noop, querySelectorAll: () => [],
    querySelector: () => null, getContext: () => stubCanvasCtx(),
  };
  let _value = '';
  Object.defineProperty(el, 'value', { get() { return _value; }, set(v) { _value = v; } });
  return el;
}
function getElementById(id) {
  if (!elementsById.has(id)) elementsById.set(id, makeEl(id));
  return elementsById.get(id);
}

const pagesDiv = { appendChild: noop, innerHTML: '' };
const sandbox = {
  document: {
    addEventListener: noop,
    getElementById: (id) => (id === 'pages' ? pagesDiv : id === 'step-bar' ? makeEl('step-bar') : getElementById(id)),
    querySelector: () => ({ checked: false, classList: { add: noop, remove: noop, toggle: noop } }),
    querySelectorAll: () => [],
    createElement: () => makeEl(Symbol('anon')),
  },
  console,
  setTimeout: (fn) => fn(),
  Math, Object, Array, JSON, String, Number, Boolean, Date,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(script, sandbox, { filename: htmlPath, timeout: 5000 });

sandbox.buildPages();
if (typeof sandbox.fillDemo === 'function') {
  try { sandbox.fillDemo(); } catch (e) { /* tail nav call, harmless */ }
} else {
  // Blank form: select the middle option (3) for all 40 questions to get a
  // deterministic, non-trivial score, then fill plausible financials.
  sandbox.QS.forEach(q => sandbox.onRadio(q.id, 3));
  ['fin_turnover', 'fin_direct', 'fin_indirect', 'fin_depreciation'].forEach(id => {});
  getElementById('fin_turnover').value = 1000000;
  getElementById('fin_direct').value = 600000;
  getElementById('fin_indirect').value = 150000;
  getElementById('fin_depreciation').value = 30000;
  getElementById('fin_deprecPeriod').value = 7;
  getElementById('fin_sectorShare').value = 100;
  getElementById('fin_discount').value = 10;
}
sandbox.updateResults();

const total = getElementById('r-total').textContent;
const pct = getElementById('r-pct').textContent;
const vanTotal = getElementById('van-total').textContent;
console.log(JSON.stringify({ total, pct, vanTotal }));

#!/usr/bin/env node
// Extract the demo dataset out of a tool's fillDemo() function: every
// document.getElementById(id).value = ... assignment, plus whichever of
// onRadio(qid,val) / selectOEK(id,val) / selectQual(id,val) it calls, plus any
// alert() narrative text. We run the real fillDemo() in a sandboxed DOM and
// intercept these calls rather than retyping 40+ field assignments by hand.
//
// Usage: node extract_filldemo.js <path-to-html>

const fs = require('fs');
const vm = require('vm');

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function noop() { return undefined; }

const fieldValues = {};
const elementsById = new Map();
function getElementById(id) {
  if (!elementsById.has(id)) {
    const el = {
      className: '', style: {}, innerHTML: '', checked: false,
      classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
      addEventListener: noop, appendChild: noop,
    };
    Object.defineProperty(el, 'value', {
      get() { return fieldValues[id]; },
      set(v) { fieldValues[id] = v; },
    });
    elementsById.set(id, el);
  }
  return elementsById.get(id);
}

const calls = { onRadio: [], selectOEK: [], selectQual: [], onFin: [] };
const alerts = [];

const sandbox = {
  document: {
    addEventListener: noop,
    getElementById,
    querySelector: () => ({
      checked: false,
      classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
    }),
    querySelectorAll: () => [],
    createElement: getElementById.bind(null, Symbol('anon')),
  },
  console: { log: noop, error: noop, warn: noop },
  alert: (msg) => { alerts.push(msg); },
  Math, Object, Array, JSON, String, Number, Boolean, Date,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(script, sandbox, { filename: htmlPath, timeout: 5000 });

for (const fn of Object.keys(calls)) {
  if (typeof sandbox[fn] === 'function') {
    const orig = sandbox[fn];
    sandbox[fn] = function (...args) { calls[fn].push(args); return orig.apply(this, args); };
  }
}

if (typeof sandbox.fillDemo !== 'function') {
  console.error('fillDemo() not found in ' + htmlPath);
  process.exit(1);
}
try {
  sandbox.fillDemo();
} catch (e) {
  // fillDemo's tail call (goToPage/navigate) touches real page DOM nodes our stub doesn't
  // fully model; harmless here since all field/score assignments happen before it.
  process.stderr.write('(non-fatal, ignored) ' + e.message + '\n');
}

process.stdout.write(JSON.stringify({ fieldValues, calls, alerts }, null, 2));

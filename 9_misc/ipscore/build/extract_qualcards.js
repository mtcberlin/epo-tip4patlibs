#!/usr/bin/env node
// Extract the 6 qualitative-question definitions (id, question text, 3 options) out of the
// NPV Target Planner. These aren't in a clean top-level data object -- they're passed as
// literal args to qualCard(id, text, opts) inside buildPages()'s template-literal HTML. We
// let the real script build its pages in a sandboxed DOM, but intercept qualCard so we
// capture every call's arguments instead of retyping the 6 questions/18 options by hand.
//
// Usage: node extract_qualcards.js <path-to-html>

const fs = require('fs');
const vm = require('vm');

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function noop() { return undefined; }
function stubEl() {
  return {
    value: '', textContent: '', className: '', style: {}, innerHTML: '',
    classList: { add: noop, remove: noop, contains: () => false },
    addEventListener: noop, appendChild: noop, querySelectorAll: () => [],
    querySelector: () => null,
  };
}

const sandbox = {
  document: {
    addEventListener: noop,
    getElementById: stubEl,
    querySelector: () => null,
    querySelectorAll: () => [],
    createElement: stubEl,
  },
  console: { log: noop, error: noop, warn: noop },
  Math, Object, Array, JSON, String, Number, Boolean, Date,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(script, sandbox, { filename: htmlPath, timeout: 5000 });

const calls = [];
const originalQualCard = sandbox.qualCard;
sandbox.qualCard = function (id, text, opts) {
  calls.push({ id, t: text, opts });
  return originalQualCard.apply(this, arguments);
};

sandbox.buildPages();

process.stdout.write(JSON.stringify(calls, null, 2));

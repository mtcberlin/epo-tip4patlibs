#!/usr/bin/env node
// Extract the 8 oekCard(id, icon, title, question, context, opts) definitions out of
// the NPV Target Planner -- same rationale as extract_qualcards.js: this is rich,
// hand-authored copy (page title, question phrasing, 5 plain-language option
// label/desc pairs each) passed as literal args inside buildPages()'s template
// literal, not a clean top-level data object. Intercepting the real call captures
// it exactly instead of retyping ~40 option pairs by hand.
//
// Usage: node extract_oekcards.js <path-to-html>

const fs = require('fs');
const vm = require('vm');

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function noop() { return undefined; }
function stubEl() {
  return {
    value: '', textContent: '', className: '', style: {}, innerHTML: '',
    classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
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
const originalOekCard = sandbox.oekCard;
sandbox.oekCard = function (id, icon, title, question, context, opts) {
  calls.push({ id, icon, title, question, context, opts });
  return originalOekCard.apply(this, arguments);
};

sandbox.buildPages();

process.stdout.write(JSON.stringify(calls, null, 2));

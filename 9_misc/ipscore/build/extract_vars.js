#!/usr/bin/env node
// Extract top-level JS variables out of one of the Dennemeyer single-file HTML tools.
// Usage: node extract_vars.js <path-to-html> <varName1> [varName2 ...]
// Prints a JSON object {varName: value, ...} to stdout.
//
// Why a VM instead of regex/manual parsing: QS/INSIGHTS/etc. are hand-written JS object
// literals (single- or double-quoted strings, string concatenation with '+', HTML entities,
// nested quotes). Evaluating the real script is the only way to extract them faithfully
// instead of retyping 40 questions x N languages by hand. DOM calls are stubbed no-ops so
// the script's own function *definitions* (never invoked, since DOMContentLoaded never fires
// in this sandbox) can't throw.

const fs = require('fs');
const vm = require('vm');

const [, , htmlPath, ...varNames] = process.argv;
if (!htmlPath || varNames.length === 0) {
  console.error('Usage: node extract_vars.js <html> <var1> [var2 ...]');
  process.exit(1);
}

const html = fs.readFileSync(htmlPath, 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
  console.error('No <script> block found in ' + htmlPath);
  process.exit(1);
}
const script = scriptMatch[1];

function noop() { return undefined; }
function stubEl() {
  return {
    value: '', textContent: '', className: '', style: {},
    classList: { add: noop, remove: noop, contains: () => false },
    addEventListener: noop, appendChild: noop, querySelectorAll: () => [],
    querySelector: () => null, getContext: () => stubCanvasCtx(),
  };
}
function stubCanvasCtx() {
  const ctx = {};
  const methods = ['beginPath','moveTo','lineTo','closePath','stroke','fill','arc','fillText',
    'clearRect','save','restore','translate','rotate','scale','setLineDash'];
  methods.forEach(m => { ctx[m] = noop; });
  return new Proxy(ctx, { get: (t, p) => (p in t ? t[p] : (typeof p === 'string' ? noop : undefined)) });
}

const sandbox = {
  document: {
    addEventListener: noop,
    getElementById: stubEl,
    querySelector: () => null,
    querySelectorAll: () => [],
    createElement: stubEl,
  },
  window: {},
  console: { log: noop, error: noop, warn: noop },
  Math, Object, Array, JSON, String, Number, Boolean, Date,
};
sandbox.window = sandbox;
vm.createContext(sandbox);

try {
  vm.runInContext(script, sandbox, { filename: htmlPath, timeout: 5000 });
} catch (e) {
  console.error('Error evaluating script from ' + htmlPath + ': ' + e.message);
  process.exit(1);
}

const out = {};
for (const name of varNames) {
  if (!(name in sandbox)) {
    console.error('Variable not found after eval: ' + name);
    process.exit(1);
  }
  out[name] = sandbox[name];
}
process.stdout.write(JSON.stringify(out, null, 2));

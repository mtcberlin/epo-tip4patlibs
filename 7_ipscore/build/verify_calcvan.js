#!/usr/bin/env node
// Sandbox-run the real calcVAN()/calcNPV() straight out of a rendered HTML's
// <script> block against a set of test cases supplied as JSON on stdin, and
// report computed vs. expected NPV for each. Used to cross-check the engine
// against values read directly out of the EPO IPscore Excel workbook -- see
// verify_against_excel.py, which is the intended caller.
//
// stdin JSON shape:
// { "htmlPath": "...", "fnName": "calcVAN"|"calcNPV", "cases": [
//     { "name": "...", "fin": {...}, "oek": {...}, "expectedNPV": 123.45,
//       // OR, for calcNPV which reads globals instead of taking args:
//       "inputs": {...}, "oekScores": {...} }
// ]}
const fs = require('fs');
const vm = require('vm');

const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const html = fs.readFileSync(payload.htmlPath, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function noop() { return undefined; }
const sandbox = {
  console, Math, Object, Array, JSON, String, Number, Boolean, Date,
  document: { addEventListener: noop, getElementById: () => null, querySelector: () => null, querySelectorAll: () => [] },
  setTimeout: (fn) => fn(),
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(script, sandbox, { filename: payload.htmlPath, timeout: 5000 });

const results = [];
for (const c of payload.cases) {
  let van;
  if (payload.fnName === 'calcVAN') {
    van = sandbox.calcVAN(c.fin, c.oek).van;
  } else {
    sandbox.inputs = c.inputs;
    sandbox.oekScores = c.oekScores;
    van = sandbox.calcNPV();
  }
  const diff = Math.abs(van - c.expectedNPV);
  results.push({ name: c.name, computed: van, expected: c.expectedNPV, diff, pass: diff < 0.01 });
}
process.stdout.write(JSON.stringify(results));

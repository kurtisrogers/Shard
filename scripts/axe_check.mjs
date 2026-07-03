#!/usr/bin/env node
/**
 * Run axe-core against an HTML file or HTML fragment on stdin.
 * Outputs a JSON array of violations to stdout.
 */
import { readFileSync } from "node:fs";
import { JSDOM } from "jsdom";
import axe from "axe-core";

const inputPath = process.argv[2];
const html = inputPath ? readFileSync(inputPath, "utf8") : readFileSync(0, "utf8");

function wrapFragment(source) {
  if (/<html[\s>]/i.test(source)) {
    return source;
  }

  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Shrd accessibility check</title>
  </head>
  <body>
    <div data-shrd-a11y-root>${source}</div>
  </body>
</html>`;
}

const dom = new JSDOM(wrapFragment(html), { runScripts: "dangerously" });
const { window } = dom;

const script = window.document.createElement("script");
script.textContent = axe.source;
window.document.head.appendChild(script);

const results = await window.axe.run(window.document, {
  runOnly: {
    type: "tag",
    values: ["wcag2a", "wcag2aa", "best-practice"],
  },
  rules: {
    // jsdom cannot evaluate contrast or layout accurately.
    "color-contrast": { enabled: false },
    "color-contrast-enhanced": { enabled: false },
    // Component fragments are embedded in page landmarks at runtime.
    region: { enabled: false },
    "landmark-main-is-top-level": { enabled: false },
    "landmark-no-duplicate-main": { enabled: false },
    "landmark-unique": { enabled: false },
  },
});

const violations = results.violations.map((violation) => ({
  code: violation.id,
  message: violation.help,
  impact: violation.impact,
  selector: violation.nodes[0]?.target?.join(" ") ?? violation.id,
  helpUrl: violation.helpUrl,
  count: violation.nodes.length,
}));

process.stdout.write(JSON.stringify(violations));

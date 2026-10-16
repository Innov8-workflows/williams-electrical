// Strip developer comments from the files this site actually publishes.
//
// GitHub Pages serves the committed branch through Jekyll, which skips any path
// segment starting with "_" or ".". So "published" = git-tracked .html/.css/.js
// outside those paths. Untracked local working files (LIVE/, v2/, audit drafts)
// are never touched.
//
// Uses the site-kit stripper (acorn-backed, token-checked), so nothing but
// comments can change. Run from the site folder; _build.py calls it after every build.
'use strict';
const fs = require('fs'), path = require('path'), os = require('os'), { execSync } = require('child_process');
const { stripHtml, stripCss, stripJs } = require(path.join(os.homedir(), '.claude', 'site-kit', 'engine', 'strip-comments.js'));

const root = process.cwd();
const files = execSync('git ls-files', { cwd: root, encoding: 'utf8' })
  .split('\n').filter(Boolean)
  .filter(f => /\.(html?|css|m?js)$/i.test(f))
  .filter(f => !f.split('/').some(seg => seg.startsWith('_') || seg.startsWith('.')));

const problems = [];
let total = 0, changed = 0;
for (const rel of files) {
  const f = path.join(root, rel);
  if (!fs.existsSync(f)) continue;
  const src = fs.readFileSync(f, 'utf8');
  let r;
  try { r = /\.html?$/i.test(f) ? stripHtml(src, problems, rel) : /\.css$/i.test(f) ? stripCss(src) : stripJs(src); }
  catch (e) { problems.push(rel + ': left as is (' + e.message + ')'); continue; }
  if (!r.n || r.out === src) continue;
  fs.writeFileSync(f, r.out);
  total += r.n; changed++;
}
for (const p of problems) console.log('PROBLEM ' + p);
console.log(` stripped ${total} comments from ${changed} of ${files.length} published files, ${problems.length} problems`);
process.exitCode = problems.length ? 2 : 0;

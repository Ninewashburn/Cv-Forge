// Garde anti-tells IA : aucun caractère « signature IA » dans les sources
// (convention CLAUDE.md). Ne cible QUE les codepoints listés :
// les lettres accentuées ne sont jamais concernées, par construction.
import { readdirSync, readFileSync } from 'node:fs';
import { extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOTS = [
  fileURLToPath(new URL('../src', import.meta.url)),
  fileURLToPath(new URL('../../prototypes', import.meta.url)),
];
const EXTENSIONS = new Set(['.ts', '.html', '.json', '.md', '.css', '.js', '.mjs']);

const NAMES = {
  '–': 'demi-cadratin',
  '—': 'tiret cadratin',
  '‘': 'apostrophe courbe ouvrante',
  '’': 'apostrophe courbe fermante',
  '“': 'guillemet courbe ouvrant',
  '”': 'guillemet courbe fermant',
  '…': 'ellipse',
  '←': 'fleche gauche',
  '→': 'fleche droite',
  '⇒': 'double fleche',
};
const FORBIDDEN = new RegExp(`[${Object.keys(NAMES).join('')}]`);

let findings = 0;

function walk(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(path);
    } else if (EXTENSIONS.has(extname(entry.name))) {
      check(path);
    }
  }
}

function check(path) {
  const lines = readFileSync(path, 'utf8').split('\n');
  lines.forEach((line, index) => {
    const match = line.match(FORBIDDEN);
    if (match) {
      findings += 1;
      console.error(`${relative(process.cwd(), path)}:${index + 1}  ${NAMES[match[0]]} (U+${match[0].codePointAt(0).toString(16).toUpperCase()})`);
    }
  });
}

for (const root of ROOTS) {
  walk(root);
}
if (findings > 0) {
  console.error(`\n${findings} tell(s) IA trouvé(s) - corriger à la main, en préservant les accents.`);
  process.exit(1);
}
console.log('Aucun tell IA dans src/ ni prototypes/.');

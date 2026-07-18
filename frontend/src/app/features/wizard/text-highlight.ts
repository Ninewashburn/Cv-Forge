/** Surlignage live de l'étape Adaptation - fonctions pures, affichage seul.
 *
 * Aucun nouveau calcul de matching : on retrouve simplement DANS le texte
 * affiché les mots-clés que l'API a déjà jugés couverts. Pour cela, un miroir
 * TS volontairement minimal du normalize/stem de keyword_engine.py suffit.
 * Le rendu passe par des segments interpolés ({{ }}) - jamais d'innerHTML.
 */

export type HighlightKind = 'plain' | 'keyword' | 'section';

export interface HighlightSegment {
  readonly text: string;
  readonly kind: HighlightKind;
}

const TOKEN_RE = /[\p{L}\p{N}+#.]{2,}/gu;

/** Premier mot (normalisé) des titres de sections courants d'un CV. */
const SECTION_FIRST_WORDS = new Set([
  'experience',
  'experiences',
  'competence',
  'competences',
  'formation',
  'formations',
  'diplome',
  'diplomes',
  'langue',
  'langues',
  'profil',
  'resume',
  'contact',
  'coordonnees',
  'projet',
  'projets',
  'certification',
  'certifications',
  'interets',
  'centres',
  'loisirs',
  'activites',
  'references',
  'atouts',
  'savoir-etre',
  'savoir-faire',
]);

function normalizeToken(word: string): string {
  return word
    .toLowerCase()
    .replace(/œ/g, 'oe')
    .replace(/æ/g, 'ae')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

/** Même stemming minimal que le moteur Python (pluriels, -euse/-eur, -trice/-teur). */
function stem(word: string): string {
  let s = word;
  if (s.length > 3 && s.endsWith('s')) s = s.slice(0, -1);
  if (s.length > 5 && s.endsWith('euse')) s = s.slice(0, -4) + 'eur';
  else if (s.length > 6 && s.endsWith('trice')) s = s.slice(0, -5) + 'teur';
  else if (s.length > 4 && s.endsWith('ee')) s = s.slice(0, -1);
  return s;
}

/** Ligne qui ressemble à un titre de section : courte, sans ponctuation finale,
 *  tout en majuscules OU commençant par un nom de section connu. */
function isSectionLine(line: string): boolean {
  const trimmed = line.trim().replace(/\s*:$/, '');
  if (trimmed.length < 3 || trimmed.length > 40) return false;
  if (/[.;!?,]$/.test(trimmed)) return false;
  if (!/\p{L}/u.test(trimmed)) return false;
  if (trimmed === trimmed.toUpperCase() && trimmed !== trimmed.toLowerCase()) return true;
  const words = normalizeToken(trimmed).split(/\s+/);
  return words.length <= 4 && SECTION_FIRST_WORDS.has(words[0]);
}

/** Découpe le texte en segments à surligner. `coveredKeywords` vient du
 *  matching live (mots-clés de l'offre couverts par le texte courant) ;
 *  les bigrammes sont surlignés via chacun de leurs mots. */
export function buildHighlightSegments(
  text: string,
  coveredKeywords: readonly string[],
): HighlightSegment[] {
  const stems = new Set<string>();
  for (const keyword of coveredKeywords) {
    for (const part of keyword.split(' ')) stems.add(stem(part));
  }

  const segments: HighlightSegment[] = [];
  const push = (chunk: string, kind: HighlightKind): void => {
    if (!chunk) return;
    const last = segments[segments.length - 1];
    if (last && last.kind === kind) {
      segments[segments.length - 1] = { text: last.text + chunk, kind };
    } else {
      segments.push({ text: chunk, kind });
    }
  };

  const lines = text.split('\n');
  lines.forEach((line, index) => {
    if (isSectionLine(line)) {
      push(line, 'section');
    } else {
      let cursor = 0;
      for (const match of line.matchAll(TOKEN_RE)) {
        const token = match[0];
        const start = match.index ?? 0;
        const covered = stems.has(stem(normalizeToken(token.replace(/\.+$/, ''))));
        push(line.slice(cursor, start), 'plain');
        push(token, covered ? 'keyword' : 'plain');
        cursor = start + token.length;
      }
      push(line.slice(cursor), 'plain');
    }
    if (index < lines.length - 1) push('\n', 'plain');
  });
  // Ligne fantôme finale : le fond suit le textarea jusqu'au bout du scroll.
  push('\n', 'plain');
  return segments;
}

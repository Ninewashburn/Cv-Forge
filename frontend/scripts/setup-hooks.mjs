// Active les hooks git versionnes (.githooks/) pour ce clone.
// A lancer une fois apres le clone :  node frontend/scripts/setup-hooks.mjs
// (core.hooksPath n'est pas partage par git, il vit dans la config locale.)
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const repoRoot = fileURLToPath(new URL('../../', import.meta.url));

try {
  execFileSync('git', ['config', 'core.hooksPath', '.githooks'], {
    cwd: repoRoot,
    stdio: 'inherit',
  });
  console.log('Hooks git actives : .githooks/ (pre-commit anti-tells).');
} catch (err) {
  console.error('Echec de l\'activation des hooks git :', err.message);
  process.exit(1);
}

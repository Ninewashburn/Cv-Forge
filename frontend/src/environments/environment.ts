/**
 * Configuration d'environnement.
 *
 * `apiBaseUrl = '/api'` fonctionne dans les deux modes :
 * - dev : `ng serve` (4200) proxifie `/api` vers `localhost:8000` (proxy.conf.json) ;
 * - prod (Phase 5) : FastAPI sert le build Angular ET l'API sur la même origine.
 * Aucune URL absolue en dur — jamais d'appel réseau vers l'extérieur.
 */
export const environment = {
  production: false,
  apiBaseUrl: '/api',
};

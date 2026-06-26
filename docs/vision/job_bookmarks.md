# Bookmarks d'offres

Les bookmarks d'offres sont le premier cas d'usage du centre de veille
candidature. Ils permettent de sauvegarder une offre consultée par l'utilisateur
dans son navigateur, sans scraper le job board et sans recopier le contenu
complet de l'annonce.

## Principe

L'utilisateur consulte une offre, puis clique sur le bouton de l'extension :

> Envoyer à la forge

L'extension envoie uniquement des métadonnées minimales à l'API locale de
CVForge. L'offre devient alors un item de type `offer` dans le centre de veille.

## Métadonnées stockées

```json
{
  "url": "https://example.com/job/123",
  "title": "Développeur Full Stack Laravel Angular",
  "company": "Entreprise exemple",
  "source": "hellowork",
  "captured_at": "2026-05-04T14:30:00",
  "status": "bookmarked"
}
```

`source` peut être envoyée par l'extension ou déduite de l'URL pour les sources
connues : Hellowork, Indeed, APEC, Welcome to the Jungle, LinkedIn et France
Travail.

## API locale

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

### Lister les offres

```http
GET /api/bookmarks
GET /api/bookmarks?source=hellowork
GET /api/bookmarks?status=bookmarked
```

### Ajouter ou mettre à jour une offre

```http
POST /api/bookmarks
Content-Type: application/json

{
  "url": "https://www.hellowork.com/fr-fr/emplois/123456.html",
  "title": "Développeur Full Stack Laravel Angular",
  "company": "Entreprise exemple",
  "source": "hellowork",
  "captured_at": "2026-05-04T14:30:00",
  "status": "bookmarked"
}
```

Le centre de veille général est documenté dans `docs/watch_center.md`.

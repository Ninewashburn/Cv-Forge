# Centre de veille candidature

Le centre de veille candidature est le cockpit personnel de CVForge. Il
centralise les ressources que l'utilisateur choisit de suivre pendant sa
recherche, sans remplacer les job boards et sans recopier les contenus externes.

## Ressources suivies

- offres d'emploi sauvegardées ;
- formations utiles ;
- news et veille métier ;
- événements ;
- candidatures en cours.

Chaque ressource est stockée comme un marque-page enrichi avec des métadonnées
minimales :

```json
{
  "url": "https://example.com/resource/123",
  "title": "Développeur Full Stack Laravel Angular",
  "source": "hellowork",
  "item_type": "offer",
  "captured_at": "2026-05-05T10:30:00",
  "status": "bookmarked",
  "company": "Entreprise exemple",
  "tags": ["laravel", "angular"],
  "related_skill": "Angular"
}
```

## Sources autorisées en V1

- ajout manuel ;
- extension navigateur “Envoyer à la forge” ;
- import URL ;
- flux RSS pour news ou formations si disponibles ;
- APIs publiques plus tard.

## Sources à éviter en V1

- scraping massif ;
- crawling automatique des job boards ;
- contournement de CAPTCHA ;
- extraction derrière login ;
- duplication complète des annonces ;
- stockage automatique de données personnelles non nécessaires.

## API locale

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

### Lister les ressources

```http
GET /api/watch-items
GET /api/watch-items?source=apec
GET /api/watch-items?item_type=training
GET /api/watch-items?status=bookmarked
```

### Ajouter ou mettre à jour une ressource

```http
POST /api/watch-items
Content-Type: application/json

{
  "url": "https://openclassrooms.com/fr/courses/angular",
  "title": "Approfondir Angular moderne",
  "item_type": "training",
  "tags": ["angular", "frontend"],
  "related_skill": "Angular"
}
```

Si une ressource existe déjà avec la même URL, elle est remplacée par la nouvelle
version. Cette règle évite les doublons quand l'utilisateur renvoie plusieurs
fois le même élément à CVForge.

## Compatibilité bookmark d'offres

`POST /api/bookmarks` reste disponible pour l'extension navigateur centrée sur
les offres d'emploi. Cet endpoint crée en interne un item de type `offer` dans
le centre de veille.

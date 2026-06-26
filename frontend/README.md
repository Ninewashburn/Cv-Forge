CVForge Frontend
================

Ce dossier accueille l'interface utilisateur de CVForge. Il utilise une
structure Angular récente, basée sur une application standalone plutôt que sur
un `NgModule` racine.

Structure
---------

```
frontend/
├── angular.json
├── package.json
├── tsconfig.json
├── tsconfig.app.json
└── src/
    ├── index.html
    ├── main.ts
    └── app/
        ├── app.config.ts
        ├── app.ts
        ├── app.html
        └── app.css
```

La convention suit le style Angular récent : les fichiers de vue racine sont
nommés `app.ts`, `app.html` et `app.css`, sans suffixe de type.

Commandes
---------

```bash
npm install
npm start
npm run build
```

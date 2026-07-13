import { Routes } from '@angular/router';

/** Routes à chargement paresseux (une feature = un chunk). Le `title` alimente
 *  l'onglet du navigateur (TitleStrategy par défaut d'Angular). */
export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    title: 'CVForge - candidater par la preuve',
    loadComponent: () => import('./features/home/home').then((m) => m.Home),
  },
  {
    path: 'atelier',
    title: 'Atelier - CVForge',
    loadComponent: () => import('./features/wizard/wizard').then((m) => m.Wizard),
  },
  {
    path: 'profil',
    title: 'Profil & Preuves - CVForge',
    loadComponent: () => import('./features/profile/profile-page').then((m) => m.ProfilePage),
  },
  { path: '**', redirectTo: '' },
];

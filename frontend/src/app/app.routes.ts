import { Routes } from '@angular/router';

/** Routes à chargement paresseux (une feature = un chunk). */
export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () => import('./features/home/home').then((m) => m.Home),
  },
  {
    path: 'atelier',
    loadComponent: () => import('./features/wizard/wizard').then((m) => m.Wizard),
  },
  {
    path: 'profil',
    loadComponent: () => import('./features/profile/profile-page').then((m) => m.ProfilePage),
  },
  { path: '**', redirectTo: '' },
];

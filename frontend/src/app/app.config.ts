import { ApplicationConfig, ErrorHandler, provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { provideRouter, withComponentInputBinding } from '@angular/router';

import { routes } from './app.routes';
import { healthInterceptor, VisibleErrorHandler } from './core/app-status';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(),
    provideRouter(routes, withComponentInputBinding()),
    // Intercepteur : détecte un serveur local arrêté. ErrorHandler : aucune
    // erreur ne reste enfouie dans la console (bandeau visible).
    provideHttpClient(withFetch(), withInterceptors([healthInterceptor])),
    { provide: ErrorHandler, useClass: VisibleErrorHandler },
  ],
};

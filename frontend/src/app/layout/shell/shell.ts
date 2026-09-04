import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AppStatus } from '../../core/app-status';

/** Layout de l'application : masthead + navigation + zone de contenu routée,
 *  et le bandeau d'alerte global (serveur arrêté, erreur non prévue). */
@Component({
  selector: 'cvforge-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './shell.html',
  styleUrl: './shell.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Shell {
  protected readonly status = inject(AppStatus);
}

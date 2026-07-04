import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

import { ProfileService } from '../../core/api';
import { MasterProfile } from '../../core/models';

type ConnectionState = 'loading' | 'connected' | 'error';

/**
 * Accueil V1 — sert de preuve de câblage : au chargement, on interroge l'API
 * (profil maître) via le proxy. Le vrai parcours guidé arrive en Phase 4.
 */
@Component({
  selector: 'cvforge-home',
  imports: [RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Home {
  private readonly profileService = inject(ProfileService);
  private readonly destroyRef = inject(DestroyRef);

  readonly state = signal<ConnectionState>('loading');
  readonly profile = signal<MasterProfile | null>(null);

  constructor() {
    this.profileService
      .get()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (profile) => {
          this.profile.set(profile);
          this.state.set('connected');
        },
        error: () => this.state.set('error'),
      });
  }
}

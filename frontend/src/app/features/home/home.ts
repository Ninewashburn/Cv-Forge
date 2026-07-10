import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

import { BackupService, ProfileService } from '../../core/api';
import { MasterProfile } from '../../core/models';

type ConnectionState = 'loading' | 'connected' | 'error';

/** Accueil V1 : état de connexion locale + sauvegarde des données (export/import ZIP). */
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
  protected readonly backup = inject(BackupService);

  readonly state = signal<ConnectionState>('loading');
  readonly profile = signal<MasterProfile | null>(null);
  protected readonly backupHint = signal('');
  protected readonly restoring = signal(false);

  constructor() {
    this.loadProfile();
  }

  protected onRestoreFile(input: HTMLInputElement): void {
    const file = input.files?.[0];
    input.value = ''; // permet de resélectionner le même fichier
    if (!file || this.restoring()) return;
    if (!window.confirm(
      'Restaurer ce backup ? TOUTES les données actuelles seront remplacées par celles de l’archive.',
    )) {
      return;
    }
    this.restoring.set(true);
    this.backupHint.set('');
    this.backup
      .import(file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.restoring.set(false);
          this.backupHint.set('Backup restauré — tes données ont été remplacées.');
          this.loadProfile();
        },
        error: (err: { error?: { detail?: string } }) => {
          this.restoring.set(false);
          this.backupHint.set(err.error?.detail ?? 'Restauration impossible.');
        },
      });
  }

  private loadProfile(): void {
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

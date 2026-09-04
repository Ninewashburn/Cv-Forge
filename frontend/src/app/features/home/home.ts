import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { ApplicationService, BackupService, OfferService, ProfileService } from '../../core/api';
import { describeError } from '../../core/api/errors';
import { downloadBlob } from '../../core/download';
import { Application, ApplicationStatus, fail, MasterProfile, Notice, ok } from '../../core/models';

type ConnectionState = 'loading' | 'connected' | 'error';

/** Une candidature suivie, avec le titre de son offre (jointure côté écran). */
interface TrackedApplication {
  readonly application: Application;
  readonly title: string;
}

// Messages de repli, sans jargon : le backend fournit le sien quand il a mieux.
const LOAD_FALLBACK = "CVForge n'a pas pu lire tes données.";
const EXPORT_FALLBACK = "La sauvegarde n'a pas pu être créée. Réessaie.";
const RESTORE_FALLBACK = "La sauvegarde n'a pas pu être restaurée. Vérifie le fichier choisi.";
const APPLICATIONS_FALLBACK = "Tes candidatures n'ont pas pu être chargées.";
const TRACK_FALLBACK = "Le statut n'a pas pu être enregistré. Réessaie.";

/** Accueil V1 : état de l'application, suivi des candidatures, sauvegarde (export/import ZIP). */
@Component({
  selector: 'cvforge-home',
  imports: [RouterLink, DatePipe],
  templateUrl: './home.html',
  styleUrl: './home.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Home {
  private readonly profileService = inject(ProfileService);
  private readonly applicationService = inject(ApplicationService);
  private readonly offerService = inject(OfferService);
  private readonly backup = inject(BackupService);
  private readonly destroyRef = inject(DestroyRef);

  readonly state = signal<ConnectionState>('loading');
  readonly profile = signal<MasterProfile | null>(null);
  protected readonly loadError = signal('');
  protected readonly backupNotice = signal<Notice | null>(null);
  protected readonly restoring = signal(false);
  protected readonly exporting = signal(false);

  /** Micro-suivi : toutes les candidatures exportées, modifiables ici à tout moment. */
  protected readonly applications = signal<TrackedApplication[]>([]);
  protected readonly applicationsNotice = signal<Notice | null>(null);
  protected readonly statuses: readonly { value: ApplicationStatus; label: string }[] = [
    { value: 'envoyee', label: 'Envoyée' },
    { value: 'reponse', label: 'Réponse reçue' },
    { value: 'entretien', label: 'Entretien obtenu' },
    { value: 'refus', label: 'Refus' },
  ];

  constructor() {
    this.loadProfile();
    this.loadApplications();
  }

  /** Sauvegarde ZIP reçue comme un fichier : on peut dire si ça a marché. Avant,
   *  un simple lien vers l'API laissait le navigateur afficher une erreur brute. */
  protected exportBackup(): void {
    if (this.exporting()) return;
    this.exporting.set(true);
    this.backupNotice.set(null);
    this.backup
      .export()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (blob) => {
          const stamp = new Date().toISOString().slice(0, 10);
          downloadBlob(blob, `cvforge-sauvegarde-${stamp}.zip`);
          this.exporting.set(false);
          this.backupNotice.set(
            ok('Sauvegarde téléchargée - garde ce fichier en lieu sûr (clé USB, disque externe).'),
          );
        },
        error: (err: unknown) => {
          this.exporting.set(false);
          this.backupNotice.set(fail(describeError(err, EXPORT_FALLBACK)));
        },
      });
  }

  protected onRestoreFile(input: HTMLInputElement): void {
    const file = input.files?.[0];
    input.value = ''; // permet de resélectionner le même fichier
    if (!file || this.restoring()) return;
    if (
      !window.confirm(
        'Restaurer cette sauvegarde ? TOUTES les données actuelles seront remplacées par celles du fichier.',
      )
    ) {
      return;
    }
    this.restoring.set(true);
    this.backupNotice.set(null);
    this.backup
      .import(file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.restoring.set(false);
          this.backupNotice.set(ok('Sauvegarde restaurée - tes données ont été remplacées.'));
          this.loadProfile();
          this.loadApplications();
        },
        error: (err: unknown) => {
          this.restoring.set(false);
          this.backupNotice.set(fail(describeError(err, RESTORE_FALLBACK)));
        },
      });
  }

  /** Changement de statut : validé contre la liste (pas de cast) ; en cas
   *  d'échec le sélecteur revient à la valeur précédente. */
  protected onStatusChange(tracked: TrackedApplication, select: HTMLSelectElement): void {
    const previous = tracked.application.status;
    const next = this.statuses.find((s) => s.value === select.value)?.value;
    if (!next || next === previous) return;
    this.applicationsNotice.set(null);
    this.applicationService
      .update(tracked.application.id, { status: next })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.applications.update((list) =>
            list.map((t) => (t.application.id === updated.id ? { ...t, application: updated } : t)),
          );
          this.applicationsNotice.set(ok('Suivi enregistré.'));
        },
        error: (err: unknown) => {
          select.value = previous;
          this.applicationsNotice.set(fail(describeError(err, TRACK_FALLBACK)));
        },
      });
  }

  protected loadProfile(): void {
    this.state.set('loading');
    this.loadError.set('');
    this.profileService
      .get()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (profile) => {
          this.profile.set(profile);
          this.state.set('connected');
        },
        error: (err: unknown) => {
          this.loadError.set(describeError(err, LOAD_FALLBACK));
          this.state.set('error');
        },
      });
  }

  private loadApplications(): void {
    forkJoin({ applications: this.applicationService.list(), offers: this.offerService.list() })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ applications, offers }) => {
          const titles = new Map(offers.map((o) => [o.id, o.title]));
          this.applications.set(
            applications.map((application) => ({
              application,
              title: titles.get(application.offer_id) ?? 'Offre',
            })),
          );
        },
        error: (err: unknown) =>
          this.applicationsNotice.set(fail(describeError(err, APPLICATIONS_FALLBACK))),
      });
  }
}

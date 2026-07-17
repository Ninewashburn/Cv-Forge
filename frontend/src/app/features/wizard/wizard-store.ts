import { computed, DestroyRef, effect, inject, Injectable, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EMPTY, forkJoin, map, Observable, of, switchMap, tap } from 'rxjs';

import { ApplicationService, OfferService, VariantService } from '../../core/api';
import {
  AdaptResult,
  Application,
  ApplicationStatus,
  CopilotPrompt,
  CvVariant,
  MatchingResult,
  Offer,
  PromptKind,
} from '../../core/models';
import { SampleKind, SAMPLES } from './samples';

/** Case d'un mot-clé de l'offre : sur le CV / révélé par LinkedIn / nulle part. */
export type Bucket = 'cv' | 'linkedin' | 'none';

export interface AnalysedKeyword {
  keyword: string;
  frequency: number;
  bucket: Bucket;
}

export interface Analysis {
  scoreCv: number;
  /** Potentiel CV + LinkedIn (null si aucun profil LinkedIn fourni). Jamais envoyé. */
  scorePotential: number | null;
  hasLinkedin: boolean;
  keywords: AnalysedKeyword[];
}

const MIN_CHARS = 40;

/**
 * État partagé du parcours. Fourni à la racine : un détour par une autre page
 * (Profil & Preuves...) ne perd plus le travail en cours - avant, quitter
 * l'Atelier détruisait tout silencieusement. « Recommencer » redonne une page
 * blanche. Toute la logique sans IA passe par l'API.
 */
@Injectable({ providedIn: 'root' })
export class WizardStore {
  private readonly offers = inject(OfferService);
  private readonly variants = inject(VariantService);
  private readonly applications = inject(ApplicationService);
  private readonly destroyRef = inject(DestroyRef);

  constructor() {
    // Toute modification des textes invalide la porte d'export : il faudra
    // repasser par l'Avant/Après (on n'exporte jamais un diff périmé).
    effect(() => {
      this.cvText();
      this.adaptedText();
      this.exportReady.set(false);
    });
  }

  readonly step = signal(1);
  readonly offerText = signal('');
  readonly cvText = signal('');
  readonly linkedinText = signal('');

  readonly offer = signal<Offer | null>(null);
  readonly analysis = signal<Analysis | null>(null);
  readonly busy = signal(false);
  readonly error = signal<string | null>(null);

  /** Texte « après » - édité à la main ou collé depuis l'IA de l'utilisateur. */
  readonly adaptedText = signal('');
  /** Index des passages ajoutés confirmés « vrai et prouvable » (étape Avant/Après). */
  readonly confirmedAdditions = signal<ReadonlySet<number>>(new Set());

  /** Vrai quand l'Avant/Après a été validé en entier - condition d'accès à l'Export. */
  readonly exportReady = signal(false);
  readonly variant = signal<CvVariant | null>(null);
  readonly application = signal<Application | null>(null);
  readonly exportBusy = signal(false);
  readonly exportError = signal<string | null>(null);

  private offerId: string | null = null;
  private diffSignature: string | null = null;
  /** Texte adapté au moment où la variante a été persistée (détection d'obsolescence). */
  private variantText: string | null = null;

  readonly canAnalyse = computed(
    () => this.offerText().trim().length >= MIN_CHARS && this.cvText().trim().length >= MIN_CHARS,
  );

  /** Du contenu est en jeu et rien n'a été exporté : prévenir avant de fermer l'onglet. */
  readonly hasUnsavedWork = computed(
    () =>
      (this.offerText().trim().length > 0 || this.cvText().trim().length > 0) &&
      this.application() === null,
  );

  goTo(step: number): void {
    // L'Analyse et l'Adaptation exigent un premier calcul ; l'Avant/Après, un
    // texte adapté ; l'Export, un Avant/Après validé en entier.
    if ((step === 2 || step === 3) && !this.analysis()) return;
    if (step === 4 && !this.adaptedText().trim()) return;
    if (step === 5 && !this.exportReady()) return;
    if (step === 3 && !this.adaptedText().trim()) this.adaptedText.set(this.cvText());
    this.setStep(step);
  }

  /** Page blanche : efface tout le parcours en mémoire (les données déjà
   *  enregistrées en base - offres, candidatures - ne bougent pas). */
  reset(): void {
    this.offerText.set('');
    this.cvText.set('');
    this.linkedinText.set('');
    this.offer.set(null);
    this.analysis.set(null);
    this.busy.set(false);
    this.error.set(null);
    this.adaptedText.set('');
    this.confirmedAdditions.set(new Set());
    this.exportReady.set(false);
    this.variant.set(null);
    this.application.set(null);
    this.exportBusy.set(false);
    this.exportError.set(null);
    this.offerId = null;
    this.diffSignature = null;
    this.variantText = null;
    this.setStep(1);
  }

  /** Changement d'étape : toujours repartir du haut (sinon on atterrit au milieu
   *  de la nouvelle étape, à la position de scroll de l'ancienne). */
  private setStep(step: number): void {
    this.step.set(step);
    window.scrollTo({ top: 0 });
  }

  /** Export : persiste la variante validée, télécharge le PDF, ouvre le micro-suivi. */
  downloadPdf(): void {
    const offer = this.offer();
    if (!offer || this.exportBusy() || !this.exportReady()) return;
    this.exportBusy.set(true);
    this.exportError.set(null);

    const adapted = this.adaptedText();
    const existing = this.variant();
    const variant$: Observable<CvVariant> =
      existing && this.variantText === adapted
        ? of(existing)
        : existing
          ? this.variants.update(existing.id, { adapted_text: adapted, status: 'validated' })
          : this.offers.generateVariant(offer.id, { adapted_text: adapted });

    variant$
      .pipe(
        tap((variant) => {
          this.variant.set(variant);
          this.variantText = adapted;
        }),
        switchMap((variant) =>
          this.variants.pdf(variant.id).pipe(map((blob) => ({ variant, blob }))),
        ),
        switchMap(({ variant, blob }) => {
          this.triggerDownload(blob, offer.title);
          const known = this.application();
          return known
            ? of(known)
            : this.applications.create({ offer_id: offer.id, variant_id: variant.id });
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (application) => {
          this.application.set(application);
          this.exportBusy.set(false);
        },
        error: () => {
          this.exportError.set('Export impossible - le backend est-il lancé sur :8000 ?');
          this.exportBusy.set(false);
        },
      });
  }

  setApplicationStatus(status: ApplicationStatus): void {
    const application = this.application();
    if (!application) return;
    this.applications
      .update(application.id, { status })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((updated) => this.application.set(updated));
  }

  private triggerDownload(blob: Blob, offerTitle: string): void {
    const slug =
      offerTitle
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^A-Za-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
        .slice(0, 60) || 'offre';
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `cv-adapte-${slug}.pdf`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  /** Matching du texte en cours d'adaptation (recalcul en direct, sans IA). */
  liveMatch(text: string): Observable<MatchingResult> {
    if (!this.offerId) return EMPTY;
    return this.offers.matching(this.offerId, { text });
  }

  /** Prompt verrouillé : le CV envoyé est TOUJOURS l'original (source de vérité). */
  buildPrompt(kind: PromptKind): Observable<CopilotPrompt> {
    if (!this.offerId) return EMPTY;
    return this.offers.copilotPrompt(this.offerId, { text: this.cvText(), kind });
  }

  /** Niveau clé API : même contrat que le copilote (CV original, mêmes intentions),
   *  mais l'appel part directement chez le fournisseur avec la clé de l'utilisateur. */
  adaptWithApi(kind: PromptKind): Observable<AdaptResult> {
    if (!this.offerId) return EMPTY;
    return this.offers.adapt(this.offerId, { text: this.cvText(), kind });
  }

  /** À l'entrée dans l'Avant/Après : si le couple (original, adapté) a changé,
   *  toutes les confirmations retombent - on ne valide jamais un diff périmé. */
  syncDiffSignature(): void {
    const signature = `${this.cvText()}\u0000${this.adaptedText()}`;
    if (signature !== this.diffSignature) {
      this.diffSignature = signature;
      this.confirmedAdditions.set(new Set());
    }
  }

  toggleConfirmation(index: number): void {
    const next = new Set(this.confirmedAdditions());
    if (next.has(index)) {
      next.delete(index);
    } else {
      next.add(index);
    }
    this.confirmedAdditions.set(next);
  }

  loadSample(kind: SampleKind): void {
    const sample = SAMPLES[kind];
    this.offerText.set(sample.offer);
    this.cvText.set(sample.cv);
    this.linkedinText.set(sample.linkedin);
  }

  analyse(): void {
    if (!this.canAnalyse() || this.busy()) return;
    this.busy.set(true);
    this.error.set(null);

    const offer$ = this.offerId
      ? this.offers.update(this.offerId, { raw_text: this.offerText() })
      : this.offers.create({ raw_text: this.offerText() });

    offer$
      .pipe(
        switchMap((offer) => {
          this.offerId = offer.id;
          this.offer.set(offer);
          const linkedin = this.linkedinText().trim();
          return forkJoin({
            cv: this.offers.matching(offer.id, { text: this.cvText() }),
            linkedin: linkedin ? this.offers.matching(offer.id, { text: linkedin }) : of(null),
          });
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: ({ cv, linkedin }) => {
          this.analysis.set(this.combine(cv, linkedin));
          this.busy.set(false);
          this.setStep(2);
        },
        error: () => {
          this.error.set('Analyse impossible - le backend est-il lancé sur :8000 ?');
          this.busy.set(false);
        },
      });
  }

  /** Combine la couverture CV et LinkedIn en un tri à 3 cases + double score. */
  private combine(cv: MatchingResult, linkedin: MatchingResult | null): Analysis {
    const revealed = new Set(
      (linkedin?.keywords ?? []).filter((k) => k.covered).map((k) => k.keyword),
    );
    const keywords: AnalysedKeyword[] = cv.keywords.map((k) => ({
      keyword: k.keyword,
      frequency: k.frequency,
      bucket: k.covered ? 'cv' : revealed.has(k.keyword) ? 'linkedin' : 'none',
    }));

    let scorePotential: number | null = null;
    if (linkedin) {
      const total = keywords.reduce((sum, k) => sum + k.frequency, 0);
      const covered = keywords
        .filter((k) => k.bucket !== 'none')
        .reduce((sum, k) => sum + k.frequency, 0);
      scorePotential = total ? Math.round((100 * covered) / total) : 0;
    }

    return { scoreCv: cv.score, scorePotential, hasLinkedin: linkedin !== null, keywords };
  }
}

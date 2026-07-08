import { computed, DestroyRef, inject, Injectable, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EMPTY, forkJoin, Observable, of, switchMap } from 'rxjs';

import { OfferService } from '../../core/api';
import { CopilotPrompt, MatchingResult, Offer, PromptKind } from '../../core/models';
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
 * État partagé du parcours (scopé au composant Wizard, donc réinitialisé à
 * chaque entrée dans l'Atelier). Toute la logique sans IA passe par l'API.
 */
@Injectable()
export class WizardStore {
  private readonly offers = inject(OfferService);
  private readonly destroyRef = inject(DestroyRef);

  readonly step = signal(1);
  readonly offerText = signal('');
  readonly cvText = signal('');
  readonly linkedinText = signal('');

  readonly offer = signal<Offer | null>(null);
  readonly analysis = signal<Analysis | null>(null);
  readonly busy = signal(false);
  readonly error = signal<string | null>(null);

  /** Texte « après » — édité à la main ou collé depuis l'IA de l'utilisateur. */
  readonly adaptedText = signal('');
  /** Index des passages ajoutés confirmés « vrai et prouvable » (étape Avant/Après). */
  readonly confirmedAdditions = signal<ReadonlySet<number>>(new Set());

  private offerId: string | null = null;
  private diffSignature: string | null = null;

  readonly canAnalyse = computed(
    () => this.offerText().trim().length >= MIN_CHARS && this.cvText().trim().length >= MIN_CHARS,
  );

  goTo(step: number): void {
    // L'Analyse et l'Adaptation exigent un premier calcul ; l'Avant/Après, un texte adapté.
    if ((step === 2 || step === 3) && !this.analysis()) return;
    if (step === 4 && !this.adaptedText().trim()) return;
    if (step === 5) return; // Export : Bloc 3
    if (step === 3 && !this.adaptedText().trim()) this.adaptedText.set(this.cvText());
    this.step.set(step);
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

  /** À l'entrée dans l'Avant/Après : si le couple (original, adapté) a changé,
   *  toutes les confirmations retombent — on ne valide jamais un diff périmé. */
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
          this.step.set(2);
        },
        error: () => {
          this.error.set('Analyse impossible — le backend est-il lancé sur :8000 ?');
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

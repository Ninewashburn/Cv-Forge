import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';

import { AnalysedKeyword, WizardStore } from '../wizard-store';

/** Étape 2 : état des lieux - matching mots-clés (sans IA), tri à 3 cases + double score. */
@Component({
  selector: 'cvforge-analyse',
  templateUrl: './analyse.html',
  styleUrl: './analyse.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AnalyseStep {
  protected readonly store = inject(WizardStore);
  protected readonly analysis = this.store.analysis;

  protected readonly onCv = computed(() => this.byBucket('cv'));
  protected readonly onLinkedin = computed(() => this.byBucket('linkedin'));
  protected readonly nowhere = computed(() => this.byBucket('none'));

  protected verdict(score: number): string {
    if (score >= 75) return "Bonne couverture - l'adaptation servira surtout à prioriser.";
    if (score >= 50) return 'Couverture partielle - vérifie les manquants un par un.';
    return 'Couverture faible - cette offre est-elle vraiment la bonne cible ?';
  }

  private byBucket(bucket: AnalysedKeyword['bucket']): AnalysedKeyword[] {
    return this.analysis()?.keywords.filter((k) => k.bucket === bucket) ?? [];
  }
}

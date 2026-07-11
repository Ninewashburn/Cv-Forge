import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ExtractService, FactService, ProfileService, ProofService } from '../../core/api';
import { Fact, FactType, Proof, ProofType } from '../../core/models';

type PageState = 'loading' | 'ready' | 'error';

/** Étiquettes UI en français — les valeurs restent les enums de l'API. */
const FACT_TYPES: readonly { value: FactType; label: string }[] = [
  { value: 'experience', label: 'Expérience' },
  { value: 'skill', label: 'Compétence' },
  { value: 'project', label: 'Projet' },
  { value: 'education', label: 'Formation' },
  { value: 'achievement', label: 'Réussite' },
];

const PROOF_TYPES: readonly { value: ProofType; label: string }[] = [
  { value: 'note', label: 'Note' },
  { value: 'link', label: 'Lien' },
  { value: 'document', label: 'Document' },
];

/** Profil maître + banque de preuves : la source de vérité que le wizard adapte ensuite. */
@Component({
  selector: 'cvforge-profile-page',
  templateUrl: './profile-page.html',
  styleUrl: './profile-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfilePage {
  private readonly profileService = inject(ProfileService);
  private readonly factService = inject(FactService);
  private readonly proofService = inject(ProofService);
  private readonly extractService = inject(ExtractService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly factTypes = FACT_TYPES;
  protected readonly proofTypes = PROOF_TYPES;

  protected readonly state = signal<PageState>('loading');
  protected readonly facts = signal<Fact[]>([]);
  protected readonly proofs = signal<Proof[]>([]);

  // --- Profil maître (un signal par champ, comme l'étape Sources) --------
  protected readonly fullName = signal('');
  protected readonly headline = signal('');
  protected readonly email = signal('');
  protected readonly phone = signal('');
  protected readonly location = signal('');
  /** Un lien par ligne (GitHub, portfolio, LinkedIn…). */
  protected readonly linksText = signal('');
  protected readonly summary = signal('');
  /** CV complet importé/collé — le matching et le copilote s'en servent automatiquement. */
  protected readonly rawImportText = signal('');
  protected readonly profileHint = signal('');
  protected readonly savingProfile = signal(false);
  protected readonly importingCv = signal(false);

  // --- Formulaire fait ----------------------------------------------------
  protected readonly factType = signal<FactType>('experience');
  protected readonly factTitle = signal('');
  protected readonly factContent = signal('');
  protected readonly factTags = signal('');
  protected readonly editingFactId = signal<string | null>(null);
  protected readonly factHint = signal('');

  // --- Formulaire preuve --------------------------------------------------
  protected readonly proofType = signal<ProofType>('note');
  protected readonly proofTitle = signal('');
  protected readonly proofContent = signal('');
  protected readonly proofFactIds = signal<string[]>([]);
  protected readonly editingProofId = signal<string | null>(null);
  protected readonly proofHint = signal('');
  protected readonly attachingId = signal<string | null>(null);

  private readonly factById = computed(() => new Map(this.facts().map((f) => [f.id, f])));

  constructor() {
    this.loadAll();
  }

  // ------------------------------------------------------------- chargement

  protected loadAll(): void {
    this.state.set('loading');
    this.profileService
      .get()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (p) => {
          this.fullName.set(p.full_name);
          this.headline.set(p.headline);
          this.email.set(p.email);
          this.phone.set(p.phone);
          this.location.set(p.location);
          this.linksText.set(p.links.join('\n'));
          this.summary.set(p.summary);
          this.rawImportText.set(p.raw_import_text ?? '');
          this.state.set('ready');
        },
        error: () => this.state.set('error'),
      });
    this.reloadFacts();
    this.reloadProofs();
  }

  private reloadFacts(): void {
    this.factService
      .list()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((facts) => this.facts.set(facts));
  }

  private reloadProofs(): void {
    this.proofService
      .list()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((proofs) => this.proofs.set(proofs));
  }

  // ------------------------------------------------------------ profil

  protected saveProfile(): void {
    if (this.savingProfile()) return;
    this.savingProfile.set(true);
    this.profileHint.set('');
    this.profileService
      .update({
        full_name: this.fullName().trim(),
        headline: this.headline().trim(),
        email: this.email().trim(),
        phone: this.phone().trim(),
        location: this.location().trim(),
        links: this.linksText()
          .split(/\r?\n/)
          .map((l) => l.trim())
          .filter(Boolean),
        summary: this.summary().trim(),
        raw_import_text: this.rawImportText().trim() || null,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.savingProfile.set(false);
          this.profileHint.set('Profil enregistré — sur ta machine, nulle part ailleurs.');
        },
        error: () => {
          this.savingProfile.set(false);
          this.profileHint.set('Enregistrement impossible — l’API locale répond-elle ?');
        },
      });
  }

  /** « Importer un fichier » : le texte extrait reste éditable, l'enregistrement est un geste à part. */
  protected onImportCv(input: HTMLInputElement): void {
    const file = input.files?.[0];
    input.value = ''; // permet de resélectionner le même fichier
    if (!file || this.importingCv()) return;
    this.importingCv.set(true);
    this.profileHint.set('');
    this.extractService
      .extract(file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ text }) => {
          this.importingCv.set(false);
          this.rawImportText.set(text);
          this.profileHint.set('Texte extrait — vérifie-le puis enregistre le profil.');
        },
        error: (err: { error?: { detail?: string } }) => {
          this.importingCv.set(false);
          this.profileHint.set(
            err.error?.detail ?? 'Lecture du fichier impossible. Le copier-coller reste toujours possible.',
          );
        },
      });
  }

  // ------------------------------------------------------------ faits

  protected typeLabel(value: FactType): string {
    return FACT_TYPES.find((t) => t.value === value)?.label ?? value;
  }

  protected proofCountOf(fact: Fact): number {
    return this.proofs().filter((p) => p.fact_ids.includes(fact.id)).length;
  }

  protected submitFact(): void {
    const title = this.factTitle().trim();
    if (title.length < 3) {
      this.factHint.set('Donne un titre au fait (3 caractères minimum).');
      return;
    }
    const payload = {
      type: this.factType(),
      title,
      content: this.factContent().trim(),
      tags: this.factTags()
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean),
    };
    const editing = this.editingFactId();
    const request$ = editing
      ? this.factService.update(editing, payload)
      : this.factService.create(payload);
    request$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.cancelFactEdit();
        this.factHint.set(editing ? 'Fait mis à jour.' : 'Fait ajouté.');
        this.reloadFacts();
      },
      error: () => this.factHint.set('Enregistrement du fait impossible.'),
    });
  }

  protected startFactEdit(fact: Fact): void {
    this.editingFactId.set(fact.id);
    this.factType.set(fact.type);
    this.factTitle.set(fact.title);
    this.factContent.set(fact.content);
    this.factTags.set(fact.tags.join(', '));
    this.factHint.set('');
  }

  protected cancelFactEdit(): void {
    this.editingFactId.set(null);
    this.factType.set('experience');
    this.factTitle.set('');
    this.factContent.set('');
    this.factTags.set('');
    this.factHint.set('');
  }

  protected toggleValidated(fact: Fact): void {
    this.factService
      .update(fact.id, { validated: !fact.validated })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.reloadFacts());
  }

  protected removeFact(fact: Fact): void {
    if (!window.confirm(`Supprimer le fait « ${fact.title} » ?`)) return;
    this.factService
      .remove(fact.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        if (this.editingFactId() === fact.id) this.cancelFactEdit();
        this.reloadFacts();
        this.reloadProofs(); // les liaisons preuve → fait ont pu changer
      });
  }

  // ------------------------------------------------------------ preuves

  protected proofTypeLabel(value: ProofType): string {
    return PROOF_TYPES.find((t) => t.value === value)?.label ?? value;
  }

  protected factTitleOf(factId: string): string {
    return this.factById().get(factId)?.title ?? '(fait supprimé)';
  }

  protected fileUrl(proof: Proof): string {
    return this.proofService.fileUrl(proof.id);
  }

  protected attachedName(proof: Proof): string {
    const name = proof.file_name ?? '';
    return name.split('--').slice(1).join('--') || name;
  }

  protected toggleProofFact(factId: string): void {
    const current = this.proofFactIds();
    this.proofFactIds.set(
      current.includes(factId) ? current.filter((id) => id !== factId) : [...current, factId],
    );
  }

  protected submitProof(): void {
    const title = this.proofTitle().trim();
    if (title.length < 3) {
      this.proofHint.set('Donne un titre à la preuve (3 caractères minimum).');
      return;
    }
    const payload = {
      type: this.proofType(),
      title,
      content: this.proofContent().trim(),
      fact_ids: this.proofFactIds(),
    };
    const editing = this.editingProofId();
    const request$ = editing
      ? this.proofService.update(editing, payload)
      : this.proofService.create(payload);
    request$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.cancelProofEdit();
        this.proofHint.set(editing ? 'Preuve mise à jour.' : 'Preuve ajoutée.');
        this.reloadProofs();
      },
      error: () => this.proofHint.set('Enregistrement de la preuve impossible.'),
    });
  }

  protected startProofEdit(proof: Proof): void {
    this.editingProofId.set(proof.id);
    this.proofType.set(proof.type);
    this.proofTitle.set(proof.title);
    this.proofContent.set(proof.content);
    this.proofFactIds.set([...proof.fact_ids]);
    this.proofHint.set('');
  }

  protected cancelProofEdit(): void {
    this.editingProofId.set(null);
    this.proofType.set('note');
    this.proofTitle.set('');
    this.proofContent.set('');
    this.proofFactIds.set([]);
    this.proofHint.set('');
  }

  protected removeProof(proof: Proof): void {
    if (!window.confirm(`Supprimer la preuve « ${proof.title} » ?`)) return;
    this.proofService
      .remove(proof.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        if (this.editingProofId() === proof.id) this.cancelProofEdit();
        this.reloadProofs();
        this.reloadFacts(); // les compteurs de preuves des faits changent
      });
  }

  protected onAttachFile(proof: Proof, input: HTMLInputElement): void {
    const file = input.files?.[0];
    input.value = ''; // permet de resélectionner le même fichier
    if (!file || this.attachingId()) return;
    this.attachingId.set(proof.id);
    this.proofHint.set('');
    this.proofService
      .attachFile(proof.id, file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.attachingId.set(null);
          this.reloadProofs();
        },
        error: (err: { error?: { detail?: string } }) => {
          this.attachingId.set(null);
          this.proofHint.set(err.error?.detail ?? 'Pièce jointe impossible.');
        },
      });
  }
}

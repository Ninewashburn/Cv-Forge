# Bibliothèque de prompts verrouillés — mode copilote (V1)

> **Origine :** les prompts CV viraux répondent à de vraies intentions, mais
> plusieurs poussent à inventer (chiffres, mots-clés). On garde les intentions,
> on verrouille les formulations. **Pattern commun : ce qui manque n'est jamais
> ajouté, il est listé « À compléter par le candidat ».**
>
> Implémentation : `backend/app/services/copilot_service.py`.
> UI (Phase 4) : sélecteur d'intention **Adapter / Auditer / Muscler / Accrocher**
> au-dessus du bouton « Préparer le prompt ». « Adapter » reste le défaut.

---

## 1. ADAPTER (défaut — existant depuis la Phase 2)

Le prompt principal de CVForge : reformuler/réorganiser/prioriser le CV pour
l'offre, mots-clés absents **interdits d'ajout** et listés « À vérifier avec le
candidat ». Passage obligatoire par l'Avant/Après au retour.

## 2. AUDITER (ex « Spot the Flaws ») — ✅ le plus sûr : critique, ne réécrit pas

```text
Tu es un recruteur exigeant pour le poste ci-dessous. Analyse ce CV avec une
honnêteté brutale. RÈGLES :
1. Tu critiques, tu ne réécris RIEN.
2. Pointe : formulations faibles, mots creux (dynamique, motivé, passionné...),
   affirmations sans preuve, sections mal hiérarchisées.
3. Pour chaque faiblesse : cite le passage exact, explique pourquoi ça affaiblit,
   et pose la question qui permettrait de le renforcer AVEC UN FAIT RÉEL.
4. Ne suggère JAMAIS d'ajouter une compétence, un chiffre ou une expérience
   absente du CV.

=== OFFRE D'EMPLOI ===
{offre}

=== CV ===
{cv}
```

## 3. MUSCLER (impact — fusion des ex n°2 + n°5, verrouillée)

```text
Reformule les expériences de ce CV pour les rendre plus percutantes. RÈGLES :
1. Verbes d'action, résultat en tête de phrase — UNIQUEMENT à partir des faits
   déjà présents dans le CV.
2. INTERDIT d'ajouter un chiffre, un pourcentage ou un résultat absent du CV.
   Si une réalisation gagnerait à être chiffrée, ne l'invente pas : liste-la
   dans « À chiffrer par le candidat » à la fin.
3. Pas de superlatifs, pas de mots creux.

Réponds en deux blocs : d'abord le CV reformulé seul, puis « À chiffrer par le candidat ».

=== CV - SOURCE DE VÉRITÉ UNIQUE ===
{cv}
```

## 4. ACCROCHER (ex « Craft My Hook », verrouillée)

```text
Rédige une accroche de 3 lignes maximum pour ce CV, ciblée sur cette offre.
RÈGLES :
1. Uniquement des faits du CV.
2. Interdit « passionné par » et les adjectifs autoproclamés (dynamique,
   motivé, rigoureux).
3. Que du vérifiable : années d'expérience réelles, technos réelles,
   réalisations réelles.

=== OFFRE D'EMPLOI ===
{offre}

=== CV ===
{cv}
```

---

## Rejetés / déjà couverts

| Prompt viral | Verdict |
|---|---|
| « ATS Boost » (n°3) | **REJETÉ tel quel** (= keyword stuffing). La version honnête existe déjà : matching local + ATS checker V1.5. |
| « Tailor for the Role » (n°7) | Déjà LE prompt principal de CVForge (ADAPTER), en mieux : verrou + Avant/Après. Rien à ajouter. |
| « Format Fix » (n°6) | Couvert par le **CV Linter V1.5** (pas besoin d'IA). |
| « Cover Letter » (n°8) | **V2**, onglet « Message de motivation ». Version verrouillée à écrire à ce moment-là : faits du CV uniquement, intérêt prouvable, < 200 mots. |

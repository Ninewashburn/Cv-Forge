"""Moteur de mots-clés sans LLM — porté du prototype CVForge Lite (app.js).

Fonctions pures (aucune DB, aucun réseau) : extraction de mots-clés pondérés
par fréquence (unigrammes + bigrammes), et couverture d'un texte par rapport
à ces mots-clés. Le français est géré par normalisation (accents, œ/æ) et un
stemming volontairement minimal (pluriels, -euse/-eur, -trice/-teur).
"""

from __future__ import annotations

import re
import unicodedata

Keyword = tuple[str, int]  # (mot-clé, fréquence dans l'offre)

STOP_WORDS = frozenset(
    "le la les un une des du de d l au aux a et ou en dans sur sous pour par avec "
    "sans chez vers entre vos votre nos notre mes mon ma ses son sa leur leurs ce "
    "cet cette ces qui que quoi dont si mais donc or ni car ne pas plus moins tres "
    "bien tout tous toute toutes autre autres comme aussi ainsi afin alors nous "
    "vous ils elles il elle on je tu y est sont sera serez etes etre avoir avez ont "
    "aura fait faire travail emploi offre poste postes mission missions profil "
    "profils experience experiences annee annees ans an entreprise societe pme "
    "equipe equipes secteur recherche recherchons recrute recrutons candidat "
    "candidate candidats environnement contexte rejoindre rejoignez renforcer "
    "integrer integre integrerez maitrise maitrisez maitriser connaissance "
    "connaissances connaissez minimum souhaite souhaitee souhaitez idealement "
    "notamment egalement plusieurs nouvelles nouvelle nouveaux forte fortes fort "
    "bon bonne bonnes premiere premier exigee exige h f hf cdi cdd temps plein "
    "partiel salaire remuneration avantages lieu type date description justifiez "
    "disposez possedez savez travaillez travaillerez assurez assurerez participez "
    "participerez contribuez contribuerez realisez realiserez developpez "
    "developperez developper concevez concevoir garantissez intervenez "
    "interviendrez evoluez evoluerez ecrivez ecrire utilisez utiliserez serez "
    "aurez competences competence requises requis qualites atouts exigences "
    "criteres niveau formation diplome bac titulaire capacite capacites sein "
    "cadre rigueur autonomie esprit sens coeur deja outil outils".split()
)

_TOKEN_RE = re.compile(r"[a-z0-9+#.]{2,}")
_NUMERIC_RE = re.compile(r"^[0-9.]+$")


def normalize(text: str) -> str:
    text = text.lower().replace("œ", "oe").replace("æ", "ae")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def tokenize(text: str) -> list[str]:
    tokens = []
    for word in _TOKEN_RE.findall(normalize(text)):
        word = word.rstrip(".")
        if len(word) >= 2 and not _NUMERIC_RE.match(word):
            tokens.append(word)
    return tokens


def stem(word: str) -> str:
    s = word
    if len(s) > 3 and s.endswith("s"):
        s = s[:-1]
    if len(s) > 5 and s.endswith("euse"):
        s = s[:-4] + "eur"
    elif len(s) > 6 and s.endswith("trice"):
        s = s[:-5] + "teur"
    elif len(s) > 4 and s.endswith("ee"):
        s = s[:-1]
    return s


def extract_keywords(text: str, limit: int = 16) -> list[Keyword]:
    """Mots-clés pondérés par fréquence. Les bigrammes répétés (≥ 2) priment
    sur leurs composants, dont la fréquence est décomptée d'autant."""
    words = tokenize(text)
    unigrams: dict[str, int] = {}
    bigrams: dict[str, int] = {}
    for i, word in enumerate(words):
        keep = word not in STOP_WORDS
        if keep:
            unigrams[word] = unigrams.get(word, 0) + 1
        if i < len(words) - 1 and keep and words[i + 1] not in STOP_WORDS:
            pair = f"{word} {words[i + 1]}"
            bigrams[pair] = bigrams.get(pair, 0) + 1

    candidates = sorted(
        (item for item in bigrams.items() if item[1] >= 2), key=lambda kv: -kv[1]
    )
    used: set[str] = set()
    kept_bigrams: list[Keyword] = []
    for pair, count in candidates:
        left, right = pair.split(" ")
        if left not in used and right not in used:
            kept_bigrams.append((pair, count))
            used.update((left, right))
            unigrams[left] = unigrams.get(left, 0) - count
            unigrams[right] = unigrams.get(right, 0) - count

    merged = kept_bigrams + [item for item in unigrams.items() if item[1] >= 1]
    return sorted(merged, key=lambda kv: -kv[1])[:limit]


def coverage(keywords: list[Keyword], text: str) -> dict:
    """Couverture pondérée : chaque mot-clé est-il présent dans ``text`` ?

    Retourne ``{"results": [{keyword, frequency, covered}], "score": 0-100}``.
    """
    flat = re.sub(r"\s+", " ", normalize(text))
    stems = {stem(w) for w in tokenize(text)}
    results = []
    for keyword, frequency in keywords:
        if " " in keyword:
            covered = keyword in flat or all(
                stem(part) in stems for part in keyword.split(" ")
            )
        else:
            covered = stem(keyword) in stems
        results.append(
            {"keyword": keyword, "frequency": frequency, "covered": covered}
        )
    total = sum(r["frequency"] for r in results)
    hit = sum(r["frequency"] for r in results if r["covered"])
    score = int(100 * hit / total + 0.5) if total else 0
    return {"results": results, "score": score}


_ACTION_VERBS = (
    "développer", "develop", "concevoir", "design", "maintenir", "maintain",
    "optimiser", "analyser", "analyze", "déployer", "écrire", "participer",
)


def extract_responsibilities(text: str) -> list[str]:
    """Phrases de mission : celles qui contiennent un verbe d'action."""
    sentences = re.split(r"[.!?\n]+", text)
    return [
        sentence.strip()
        for sentence in sentences
        if any(verb in sentence.lower() for verb in _ACTION_VERBS) and sentence.strip()
    ]

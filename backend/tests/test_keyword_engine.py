"""Tests du moteur de mots-clés (fonctions pures, portées du prototype Lite)."""

from app.services.keyword_engine import (
    coverage,
    extract_keywords,
    extract_responsibilities,
    normalize,
    stem,
    tokenize,
)

OFFER = """Développeur Fullstack Angular / Spring Boot (H/F) - CDI, Caen
Nous recherchons un développeur fullstack pour renforcer notre équipe produit.

Vos missions :
- Développer de nouvelles fonctionnalités en Angular et TypeScript
- Concevoir des API en Spring Boot avec PostgreSQL
- Écrire des tests unitaires et participer aux revues de code
- Déployer avec Docker, Kubernetes et GitLab CI

Profil :
- Vous maîtrisez Angular, Spring Boot et PostgreSQL
- Vous connaissez Docker ; Kubernetes est un plus
- Vous travaillez en méthode agile Scrum
Angular et Spring Boot sont au coeur de notre stack."""

CV = """Lina Carvalho - Développeuse Fullstack
- Développement d'un dashboard de supervision en Angular et TypeScript
- API REST en Spring Boot, base PostgreSQL, conteneurisation Docker
- Tests unitaires (JUnit, Jasmine), revues de code, méthode Scrum"""


def test_normalize_strips_accents_and_ligatures():
    assert normalize("Développeur au cœur") == "developpeur au coeur"


def test_tokenize_filters_short_and_numeric():
    # Les purs nombres tombent ; les stop-words restent (filtrés plus tard
    # par extract_keywords) ; seuls les points FINAUX sont retirés (.net garde le sien).
    assert tokenize("C# et .NET 2024, ok!") == ["c#", "et", ".net", "ok"]


def test_stem_handles_french_feminines_and_plurals():
    # Le stem opère sur des tokens normalisés (sans accents), cf. tokenize().
    assert stem("developpeuses") == "developpeur"
    assert stem("developpeuse") == "developpeur"
    assert stem("tests") == "test"
    assert stem("administratrice") == "administrateur"


def test_extract_keywords_finds_repeated_bigram():
    keywords = dict(extract_keywords(OFFER))
    assert "spring boot" in keywords
    assert keywords["spring boot"] >= 2
    # Les stop-words métier ne remontent jamais.
    assert "missions" not in keywords
    assert "vous" not in keywords


def test_extract_keywords_caps_at_limit():
    assert len(extract_keywords(OFFER, limit=5)) == 5


def test_coverage_full_when_text_contains_everything():
    keywords = [("angular", 3), ("docker", 1)]
    result = coverage(keywords, "Angular et Docker au quotidien")
    assert result["score"] == 100
    assert all(r["covered"] for r in result["results"])


def test_coverage_weighted_by_frequency():
    keywords = [("angular", 3), ("kubernetes", 1)]
    result = coverage(keywords, "Angular uniquement")
    assert result["score"] == 75  # 3 / 4 pondéré


def test_coverage_feminine_matches_masculine_keyword():
    result = coverage([("developpeur", 1)], "Développeuse fullstack")
    assert result["results"][0]["covered"] is True


def test_coverage_realistic_cv_vs_offer():
    result = coverage(extract_keywords(OFFER), CV)
    assert 0 < result["score"] < 100
    missing = {r["keyword"] for r in result["results"] if not r["covered"]}
    # Kubernetes est absent du CV — ici sous forme de bigramme « docker
    # kubernetes » (répété 2× dans l'offre, il absorbe ses composants).
    assert any("kubernetes" in keyword for keyword in missing)


def test_responsibilities_detected_by_action_verbs():
    missions = extract_responsibilities(OFFER)
    assert any("Développer" in m for m in missions)
    assert any("Concevoir" in m for m in missions)

(function () {
  "use strict";

  /* Le fichier est la sauvegarde : capture du gabarit vierge */
  const PRISTINE = "<!doctype html>\n" + document.documentElement.outerHTML;
  let dirty = false, fileHandle = null, startStep = 1;

  /* État */
  const S = {
    step: 1, offre: "", cv: "", linkedin: "", adapted: "", kws: null, matching: null,
    diffSig: null, segs: [], confirmed: new Set(), exports: []
  };

  /* Données d'exemple */
  const SAMPLES = {
    "cv-dev":
      `Lina Carvalho - Développeuse Fullstack
Caen · lina.carvalho@mail.fr · github.com/linacarvalho

EXPÉRIENCE
Développeuse fullstack - Atelier Numérique (2023–2026)
- Développement d'un dashboard de supervision en Angular et TypeScript
- API REST en Spring Boot, base PostgreSQL, conteneurisation Docker
- Tests unitaires (JUnit, Jasmine), revues de code, méthode Scrum

Développeuse junior - WebFabrik (2022–2023)
- Sites e-commerce, intégration responsive, corrections de bugs

PROJETS
- Application de réservation : Angular, Spring Boot, PostgreSQL (GitHub)
- Portfolio personnel déployé en ligne

FORMATION
Titre professionnel Concepteur Développeur d'Applications (2022)`,

    "cv-gestion":
      `Karim Bensaïd - Assistant de gestion
Rouen · k.bensaid@mail.fr

EXPÉRIENCE
Assistant de gestion - Transports Lemaire (2021–2026)
- Facturation clients et fournisseurs, établissement des devis
- Relances clients et suivi des règlements
- Saisie comptable dans l'ERP Sage, rapprochements bancaires
- Accueil téléphonique et gestion du courrier

Employé administratif - Mairie de Rouen (2019–2021)
- Gestion des dossiers, archivage, mise à jour des tableaux Excel

FORMATION
BTS Gestion de la PME (2019)`,

    "offre-dev":
      `Développeur Fullstack Angular / Spring Boot (H/F) - CDI, Caen
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
Angular et Spring Boot sont au coeur de notre stack.`,

    "offre-gestion":
      `Assistant administratif et commercial (H/F) - CDI, Rouen
PME du secteur logistique, nous recherchons un assistant polyvalent.

Vos missions :
- Facturation et établissement des devis clients
- Relances des impayés et suivi des règlements
- Mise à jour du CRM et des tableaux de bord Excel (tableaux croisés dynamiques)
- Accueil téléphonique, gestion des plannings

Profil :
- Vous maîtrisez Excel et les tableaux croisés dynamiques
- Une première expérience en facturation est exigée
- La connaissance d'un CRM et d'un ERP est un plus`,

    "linkedin-dev":
      `Lina Carvalho
Développeuse Fullstack · Caen · linkedin.com/in/linacarvalho

À propos
Développeuse fullstack qui aime livrer des produits fiables et bien testés.

Expérience
Développeuse fullstack - Atelier Numérique (2023 - aujourd'hui)
Angular, TypeScript, Spring Boot et PostgreSQL au quotidien. J'ai mis en place le
déploiement continu avec GitLab CI/CD et l'orchestration des conteneurs sous Kubernetes.
Suivi des métriques applicatives avec Grafana.

Développeuse junior - WebFabrik (2022 - 2023)
Intégration responsive, sites e-commerce.

Compétences
Angular · TypeScript · Spring Boot · PostgreSQL · Docker · Kubernetes · GitLab CI/CD · Scrum · Grafana

Bénévolat
Mentore dans une association d'initiation au code.`,

    "linkedin-gestion":
      `Karim Bensaïd
Assistant de gestion · Rouen · linkedin.com/in/karimbensaid

À propos
Rigoureux et organisé, j'aime fluidifier la gestion administrative et commerciale.

Expérience
Assistant de gestion - Transports Lemaire (2021 - aujourd'hui)
Facturation, devis et relances clients. Gestion d'un CRM (HubSpot) pour le suivi
commercial. Reporting via tableaux croisés dynamiques sous Excel. Élaboration des
plannings de tournées.

Employé administratif - Mairie de Rouen (2019 - 2021)
Archivage et mise à jour de tableaux Excel.

Compétences
Facturation · Devis · Relances · Sage · CRM HubSpot · Excel · Tableaux croisés dynamiques · Plannings

Centres d'intérêt
Bénévolat dans une association locale.`
  };

  /* Utilitaires */
  const $ = id => document.getElementById(id);
  const esc = s => s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
  const touch = () => { dirty = true; const h = $("saveHint"); if (h) h.textContent = "modifications non enregistrées"; };

  /* Mots-clés sans LLM */
  const STOP = new Set(("le la les un une des du de d l au aux a et ou en dans sur sous pour par avec sans chez vers entre vos votre nos notre mes mon ma ses son sa leur leurs ce cet cette ces qui que quoi dont si mais donc or ni car ne pas plus moins tres bien tout tous toute toutes autre autres comme aussi ainsi afin alors nous vous ils elles il elle on je tu y est sont sera serez etes etre avoir avez ont aura fait faire travail emploi offre poste postes mission missions profil profils experience experiences annee annees ans an entreprise societe pme equipe equipes secteur recherche recherchons recrute recrutons candidat candidate candidats environnement contexte rejoindre rejoignez renforcer integrer integre integrerez maitrise maitrisez maitriser connaissance connaissances connaissez minimum souhaite souhaitee souhaitez idealement notamment egalement plusieurs nouvelles nouvelle nouveaux forte fortes fort bon bonne bonnes premiere premier exigee exige h f hf cdi cdd temps plein partiel salaire remuneration avantages lieu type date description justifiez disposez possedez savez travaillez travaillerez assurez assurerez participez participerez contribuez contribuerez realisez realiserez developpez developperez developper concevez concevoir garantissez intervenez interviendrez evoluez evoluerez ecrivez ecrire utilisez utiliserez serez aurez competences competence requises requis qualites atouts exigences criteres niveau formation diplome bac titulaire capacite capacites sein cadre rigueur autonomie esprit sens coeur deja outil outils").split(/\s+/));
  const norm = s => s.toLowerCase().replace(/œ/g, "oe").replace(/æ/g, "ae")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const tok = t => (norm(t).match(/[a-z0-9+#.]{2,}/g) || [])
    .map(w => w.replace(/[.]+$/, "")).filter(w => w.length >= 2 && !/^[0-9.]+$/.test(w));
  const stem = w => {
    let s = w;
    if (s.length > 3 && s.endsWith("s")) s = s.slice(0, -1);
    if (s.length > 5 && s.endsWith("euse")) s = s.slice(0, -4) + "eur";
    else if (s.length > 6 && s.endsWith("trice")) s = s.slice(0, -5) + "teur";
    else if (s.length > 4 && s.endsWith("ee")) s = s.slice(0, -1);
    return s;
  };

  function keywords(offre) {
    const ws = tok(offre), ok = w => !STOP.has(w);
    const uni = new Map(), bi = new Map();
    for (let i = 0; i < ws.length; i++) {
      if (ok(ws[i])) uni.set(ws[i], (uni.get(ws[i]) || 0) + 1);
      if (i < ws.length - 1 && ok(ws[i]) && ok(ws[i + 1])) {
        const b = ws[i] + " " + ws[i + 1]; bi.set(b, (bi.get(b) || 0) + 1);
      }
    }
    const cand = [...bi].filter(([, c]) => c >= 2).sort((a, b) => b[1] - a[1]);
    const used = new Set(), bigrams = [];
    for (const [b, c] of cand) {
      const [x, y] = b.split(" ");
      if (!used.has(x) && !used.has(y)) {
        bigrams.push([b, c]); used.add(x); used.add(y);
        uni.set(x, (uni.get(x) || 0) - c); uni.set(y, (uni.get(y) || 0) - c);
      }
    }
    return [...bigrams, ...[...uni].filter(([, c]) => c >= 1)]
      .sort((p, q) => q[1] - p[1]).slice(0, 16);
  }
  function coverage(kws, text) {
    const tn = norm(text).replace(/\s+/g, " ");
    const stems = new Set(tok(text).map(stem));
    const res = kws.map(([k, f]) => {
      let hit;
      if (k.includes(" ")) hit = tn.includes(k) || k.split(" ").every(p => stems.has(stem(p)));
      else hit = stems.has(stem(k));
      return { k, f, hit };
    });
    const tot = res.reduce((s, r) => s + r.f, 0);
    const cov = res.filter(r => r.hit).reduce((s, r) => s + r.f, 0);
    return { res, score: tot ? Math.round(100 * cov / tot) : 0 };
  }

  /* Diff LCS mot-a-mot */
  const tokensOf = t => t.replace(/\r\n?/g, "\n").split(/(\n)|[ \t]+/).filter(x => x !== undefined && x !== "");
  function lcsDiff(A, B) {
    const n = A.length, m = B.length;
    if (n * m > 4000000) return null;
    const dp = Array.from({ length: n + 1 }, () => new Int32Array(m + 1));
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--)
      dp[i][j] = A[i] === B[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    const ops = []; let i = 0, j = 0;
    while (i < n && j < m) {
      if (A[i] === B[j]) { ops.push(["=", A[i]]); i++; j++; }
      else if (dp[i + 1][j] >= dp[i][j + 1]) { ops.push(["-", A[i]]); i++; }
      else { ops.push(["+", B[j]]); j++; }
    }
    while (i < n) ops.push(["-", A[i++]]);
    while (j < m) ops.push(["+", B[j++]]);
    return ops;
  }

  /* Persistance */
  function payload() {
    return {
      v: 1, step: S.step, offre: S.offre, cv: S.cv, linkedin: S.linkedin, adapted: S.adapted,
      exports: S.exports, diffSig: S.diffSig, confirmed: [...S.confirmed]
    };
  }
  function serialize() {
    const json = JSON.stringify(payload()).replace(/<\//g, "<\\/");
    return PRISTINE.replace(
      /(<script type="application\/json" id="cvforge-data">)[\s\S]*?(<\/script>)/,
      function (_, a, b) { return a + json + b; }
    );
  }
  function fileName() {
    try { return decodeURIComponent(location.pathname.split("/").pop()) || "cvforge-lite.html"; }
    catch (e) { return "cvforge-lite.html"; }
  }
  async function save() {
    const html = serialize();
    if (window.showSaveFilePicker) {
      try {
        if (!fileHandle) {
          fileHandle = await window.showSaveFilePicker({
            suggestedName: fileName(),
            types: [{ description: "CVForge Lite", accept: { "text/html": [".html", ".htm"] } }]
          });
        }
        const w = await fileHandle.createWritable();
        await w.write(html); await w.close();
        dirty = false; $("saveHint").textContent = "Enregistré dans le fichier ✓";
        return;
      } catch (err) {
        if (err && err.name === "AbortError") return;
        fileHandle = null;
      }
    }
    const blob = new Blob([html], { type: "text/html" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = fileName();
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    dirty = false; $("saveHint").textContent = "Téléchargé - remplace l'ancien fichier ✓";
  }
  function hydrate() {
    const el = $("cvforge-data");
    if (!el) return;
    let d = null;
    try { d = JSON.parse(el.textContent); } catch (e) { }
    if (!d || typeof d !== "object") return;
    S.offre = d.offre || ""; S.cv = d.cv || ""; S.adapted = d.adapted || "";
    S.linkedin = d.linkedin || "";
    S.exports = Array.isArray(d.exports) ? d.exports : [];
    S.diffSig = ("diffSig" in d) ? d.diffSig : null;
    S.confirmed = new Set(Array.isArray(d.confirmed) ? d.confirmed : []);
    $("offreInput").value = S.offre;
    $("cvInput").value = S.cv;
    $("linkedinInput").value = S.linkedin;
    if (S.linkedin) { const r = $("revealLi"); if (r) r.open = true; }
    syncAnalyserBtn();
    renderTracking();
    if (d.step && canEnter(d.step)) startStep = d.step;
    $("saveHint").textContent = "Données restaurées depuis le fichier";
  }
  window.addEventListener("beforeunload", e => {
    if (dirty) { e.preventDefault(); e.returnValue = ""; }
  });

  /* Navigation */
  function canEnter(n) {
    if (n <= 1) return true;
    if (n === 2 || n === 3) return S.offre.trim().length >= 40 && S.cv.trim().length >= 40;
    if (n === 4) return canEnter(3) && S.adapted.trim().length > 0;
    return false;
  }
  function go(n) {
    if (!canEnter(n)) return;
    S.step = n;
    if (n === 2) renderAnalyse();
    if (n === 3) enterAdaptation();
    if (n === 4) renderDiff();
    document.querySelectorAll("section[data-step]").forEach(s =>
      s.classList.toggle("active", +s.dataset.step === n));
    document.querySelectorAll(".steps .step").forEach(b => {
      const k = +b.dataset.go;
      b.toggleAttribute("disabled", !canEnter(k));
      if (k === n) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
      b.classList.toggle("done", k < n);
    });
    window.scrollTo({ top: 0 });
  }
  function refreshNav() {
    document.querySelectorAll(".steps .step").forEach(b =>
      b.toggleAttribute("disabled", !canEnter(+b.dataset.go)));
  }

  /* Step 1 - sources */
  function syncAnalyserBtn() {
    $("btnAnalyse").disabled = !(S.offre.trim().length >= 40 && S.cv.trim().length >= 40);
  }
  $("offreInput").addEventListener("input", e => {
    S.offre = e.target.value; S.kws = null; touch(); syncAnalyserBtn(); refreshNav();
  });
  $("cvInput").addEventListener("input", e => {
    S.cv = e.target.value; touch(); syncAnalyserBtn(); refreshNav();
  });
  $("linkedinInput").addEventListener("input", e => {
    S.linkedin = e.target.value; touch(); if (S.step === 2) renderAnalyse();
  });
  $("btnAnalyse").addEventListener("click", () => go(2));
  const SAMPLE_TARGET = { cv: "cvInput", offre: "offreInput", linkedin: "linkedinInput" };
  document.querySelectorAll("[data-sample]").forEach(b => {
    b.addEventListener("click", () => {
      const key = b.dataset.sample;
      const ta = $(SAMPLE_TARGET[key.split("-")[0]] || "offreInput");
      ta.value = SAMPLES[key];
      ta.dispatchEvent(new Event("input"));
    });
  });

  /* Step 2 - analyse */
  function ensureKws() { if (!S.kws) S.kws = keywords(S.offre); return S.kws; }
  function renderAnalyse() {
    const kws = ensureKws();
    const cvCov = coverage(kws, S.cv);
    S.matching = cvCov;
    const hasLi = S.linkedin.trim().length > 0;
    const liCov = hasLi ? coverage(kws, S.linkedin) : null;
    const liHit = {};
    if (liCov) liCov.res.forEach(r => { liHit[r.k] = r.hit; });

    const score = cvCov.score;
    $("scoreVal").textContent = score;
    $("scoreFill").style.width = score + "%";
    $("scoreVerdict").textContent =
      score >= 75 ? "Bonne couverture - l'adaptation servira surtout à prioriser." :
        score >= 50 ? "Couverture partielle - vérifie les manquants un par un." :
          "Couverture faible - cette offre est-elle vraiment la bonne cible ?";

    const onCv = [], onLi = [], nowhere = [];
    cvCov.res.forEach(r => {
      if (r.hit) onCv.push(r);
      else if (liHit[r.k]) onLi.push(r);
      else nowhere.push(r);
    });
    const chip = (r, cls, icon) => `<span class="chip ${cls}">${icon} ${esc(r.k)} <span class="f">×${r.f}</span></span>`;

    $("chipsOk").innerHTML = onCv.length ? onCv.map(r => chip(r, "chip-ok", "✓")).join("") : '<span class="hint">Aucun mot-clé couvert.</span>';

    $("groupLi").hidden = !hasLi;
    if (hasLi) {
      $("chipsLi").innerHTML = onLi.length
        ? onLi.map(r => chip(r, "chip-li", "↗")).join("")
        : '<span class="hint">Rien de plus à révéler depuis ton LinkedIn.</span>';
    }

    $("missTitle").textContent = hasLi ? "? ABSENT DU CV ET DE LINKEDIN - NE PAS INVENTER" : "? ABSENT DE TON CV";
    const missList = hasLi ? nowhere : cvCov.res.filter(r => !r.hit);
    const missCls = hasLi ? "chip-none" : "chip-miss";
    $("chipsMiss").innerHTML = missList.length
      ? missList.map(r => chip(r, missCls, "?")).join("")
      : '<span class="hint">Rien ne manque - couverture totale.</span>';

    if (hasLi) {
      const tot = cvCov.res.reduce((s, r) => s + r.f, 0);
      const cov = cvCov.res.reduce((s, r) => s + ((r.hit || liHit[r.k]) ? r.f : 0), 0);
      const potential = tot ? Math.round(100 * cov / tot) : 0;
      $("scorePotential").hidden = false;
      $("scorePotential").innerHTML =
        `CV seul : <span class="hl">${score}%</span> · CV + ce que tu peux légitimement ajouter depuis LinkedIn : <span class="hl">${potential}%</span> <span class="li-note">(potentiel - jamais un score envoyé)</span>`;
    } else {
      $("scorePotential").hidden = true;
    }
  }

  /* Step 3 - adaptation + matching live */
  function enterAdaptation() {
    $("cvOriginalView").value = S.cv;
    if (!S.adapted.trim()) { S.adapted = S.cv; }
    $("adaptedInput").value = S.adapted;
    renderLive();
  }
  function renderLive() {
    const m = coverage(ensureKws(), S.adapted || "");
    $("liveScore").textContent = m.score;
    $("liveFill").style.width = m.score + "%";
    const ok = m.res.filter(r => r.hit), miss = m.res.filter(r => !r.hit);
    $("liveOkCount").textContent = ok.length + " couvert" + (ok.length > 1 ? "s" : "");
    $("liveMissCount").textContent = miss.length + " manquant" + (miss.length > 1 ? "s" : "");
    $("liveMiss").innerHTML = miss.length
      ? miss.map(r => `<span class="chip chip-miss">? ${esc(r.k)} <span class="f">×${r.f}</span></span>`).join("")
      : '<span class="live-done">✓ Couverture totale des mots-clés.</span>';
  }
  const liveDebounced = debounce(renderLive, 250);
  $("adaptedInput").addEventListener("input", e => {
    S.adapted = e.target.value; touch(); refreshNav(); liveDebounced();
  });
  $("btnResetAdapted").addEventListener("click", () => {
    S.adapted = S.cv; $("adaptedInput").value = S.cv; touch(); renderLive();
  });

  function buildPrompt() {
    const missing = coverage(ensureKws(), S.adapted || S.cv).res.filter(r => !r.hit).map(r => r.k);
    return `Tu es un assistant de candidature. RÈGLES ABSOLUES, sans exception :
1. Tu n'inventes JAMAIS : aucune compétence, expérience, diplôme, certification, technologie ou chiffre absent du CV ci-dessous.
2. Tu peux uniquement reformuler, réorganiser, prioriser et résumer le contenu du CV.
3. Les mots-clés listés en bas sont ABSENTS du CV : ne les ajoute PAS. Liste-les à la fin sous le titre « À vérifier avec le candidat ».
4. Conserve la langue, le ton factuel et la structure générale du CV.
5. Mets en avant en priorité ce qui correspond à l'offre.

Réponds en deux blocs : d'abord le CV adapté seul, puis la liste « À vérifier avec le candidat ».

=== OFFRE D'EMPLOI ===
${S.offre}

=== CV - SOURCE DE VÉRITÉ UNIQUE ===
${S.cv}

=== MOTS-CLÉS DE L'OFFRE ABSENTS DU CV (NE PAS AJOUTER) ===
${missing.length ? missing.join(", ") : "(aucun)"}`;
  }
  $("btnPrompt").addEventListener("click", () => {
    $("promptText").value = buildPrompt();
    $("promptOut").hidden = false;
    $("btnCopy").hidden = false;
    $("copyHint").textContent = "";
  });
  $("btnCopy").addEventListener("click", async () => {
    const t = $("promptText");
    try { await navigator.clipboard.writeText(t.value); }
    catch (e) { t.focus(); t.select(); document.execCommand("copy"); }
    $("copyHint").textContent = "Copié - colle-le dans ton IA.";
  });

  /* Step 4 - diff, confirmations, export */
  function renderDiff() {
    const ops = lcsDiff(tokensOf(S.cv), tokensOf(S.adapted));
    const sig = S.cv + " " + S.adapted;
    if (sig !== S.diffSig) { S.confirmed = new Set(); S.diffSig = sig; }

    if (!ops) {
      $("diffLeft").innerHTML = $("diffRight").innerHTML =
        '<span class="hint">Texte trop long pour le diff de la version Lite (limite mémoire).</span>';
      S.segs = []; renderSegs(); return;
    }
    const html = side => ops.map(([t, w]) => {
      if (w === "\n") return (side === "L" ? t !== "+" : t !== "-") ? "<br>" : "";
      if (t === "=") return esc(w) + " ";
      if (t === "-" && side === "L") return '<span class="d-del">' + esc(w) + "</span> ";
      if (t === "+" && side === "R") return '<span class="d-ins">' + esc(w) + "</span> ";
      return "";
    }).join("");
    $("diffLeft").innerHTML = html("L");
    $("diffRight").innerHTML = html("R");

    const nIns = ops.filter(o => o[0] === "+" && o[1] !== "\n").length;
    const nDel = ops.filter(o => o[0] === "-" && o[1] !== "\n").length;
    $("diffStats").innerHTML =
      `<span class="ins">+ ${nIns} mot${nIns > 1 ? "s" : ""} ajouté${nIns > 1 ? "s" : ""}</span>` +
      `<span class="del">- ${nDel} mot${nDel > 1 ? "s" : ""} supprimé${nDel > 1 ? "s" : ""}</span>` +
      (nIns + nDel === 0 ? "<span>Aucune modification.</span>" : "");

    const segs = []; let cur = [];
    for (const [t, w] of ops) {
      if (t === "+" && w !== "\n") cur.push(w);
      else if (cur.length) { segs.push(cur.join(" ")); cur = []; }
    }
    if (cur.length) segs.push(cur.join(" "));
    S.segs = segs;
    renderSegs();
  }
  function renderSegs() {
    const list = $("segsList"); list.innerHTML = "";
    const has = S.segs.length > 0;
    $("segsBlock").style.display = has ? "" : "none";
    $("noAdds").hidden = has;
    S.segs.forEach((txt, i) => {
      const row = document.createElement("div"); row.className = "seg";
      const p = document.createElement("div"); p.className = "seg-text";
      p.innerHTML = "<mark>" + esc(txt) + "</mark>";
      const b = document.createElement("button"); b.type = "button"; b.className = "confirm";
      const paint = () => {
        const on = S.confirmed.has(i);
        b.classList.toggle("on", on);
        b.textContent = on ? "✓ CONFIRMÉ - VRAI ET PROUVABLE" : "CONFIRMER - VRAI ET PROUVABLE ?";
        b.setAttribute("aria-pressed", on);
      };
      b.addEventListener("click", () => {
        S.confirmed.has(i) ? S.confirmed.delete(i) : S.confirmed.add(i);
        touch(); paint(); gate();
      });
      paint();
      row.append(p, b); list.append(row);
    });
    gate();
  }
  function gate() {
    const total = S.segs.length, done = S.confirmed.size;
    const ok = done >= total;
    $("gateCount").textContent = total ? `${done}/${total} ajout${total > 1 ? "s" : ""} confirmé${done > 1 ? "s" : ""}` : "";
    $("gateCount").classList.toggle("ok", ok && total > 0);
    $("btnExport").disabled = !ok;
  }
  $("btnExport").addEventListener("click", () => {
    $("printable").textContent = S.adapted;
    window.print();
    addTracking();
  });

  /* Micro-tracking */
  function addTracking() {
    const title = (S.offre.trim().split("\n")[0] || "Offre sans titre").slice(0, 70);
    S.exports.push({ title, date: new Date().toLocaleDateString("fr-FR"), status: "envoyee" });
    touch();
    renderTracking();
  }
  function renderTracking() {
    $("trackBlock").hidden = S.exports.length === 0;
    const wrap = $("trackList"); wrap.innerHTML = "";
    S.exports.forEach((e, i) => {
      const row = document.createElement("div"); row.className = "track-item";
      const meta = document.createElement("div"); meta.className = "meta";
      meta.textContent = e.date + " - " + e.title;
      const sel = document.createElement("select");
      [["envoyee", "Envoyée"], ["reponse", "Réponse reçue"], ["entretien", "Entretien obtenu"], ["refus", "Refus"]]
        .forEach(([v, l]) => {
          const o = document.createElement("option"); o.value = v; o.textContent = l;
          if (e.status === v) o.selected = true; sel.append(o);
        });
      sel.addEventListener("change", () => { S.exports[i].status = sel.value; touch(); });
      sel.setAttribute("aria-label", "Statut de la candidature");
      row.append(meta, sel); wrap.append(row);
    });
  }

  /* Actions globales */
  $("btnSave").addEventListener("click", save);
  $("btnReset").addEventListener("click", () => {
    if (!confirm("Recharger le fichier ? Les modifications non enregistrées seront perdues - tu reviendras à la dernière sauvegarde.")) return;
    dirty = false;
    location.reload();
  });
  document.querySelectorAll("[data-go]").forEach(b => {
    if (!b.classList.contains("step")) b.addEventListener("click", () => go(+b.dataset.go));
  });
  document.querySelectorAll(".steps .step").forEach(b =>
    b.addEventListener("click", () => go(+b.dataset.go)));

  /* Visite guidée - lancée au clic, interruptible à tout moment */
  (function tour() {
    const btn = $("btnTour");
    if (!btn) return;
    const STEPS = [
      { n: 1, fill: true, title: "Les deux matières premières", text: "On a chargé un exemple : une offre d'emploi et un CV. Tout reste éditable à la main." },
      { n: 2, title: "Matching offre / CV", text: "La couverture des mots-clés de l'offre est calculée localement, sans IA." },
      { n: 3, title: "Adaptation en direct", text: "Tu modifies le CV au centre ; le score se recalcule à chaque frappe, dans le panneau de droite." },
      { n: 4, title: "Avant / après — tu vois tout, tu valides tout", text: "Chaque ajout est tracé. Tu confirmes qu'il est vrai et prouvable avant d'exporter." },
    ];
    let i = -1, box = null;

    function fillSample() {
      ["offre", "cv"].forEach(k => {
        const ta = $(k === "offre" ? "offreInput" : "cvInput");
        ta.value = SAMPLES[k === "offre" ? "offre-dev" : "cv-dev"];
        ta.dispatchEvent(new Event("input"));
      });
    }
    function show(idx) {
      i = idx;
      const s = STEPS[i], last = i === STEPS.length - 1;
      if (s.fill) fillSample();
      go(s.n);
      box.innerHTML =
        `<div class="tour-step">Étape ${i + 1} / ${STEPS.length}</div>
         <h4>${s.title}</h4>
         <p>${s.text}</p>
         <div class="tour-actions">
           <button type="button" class="tour-skip">Passer</button>
           <button type="button" class="tour-next">${last ? "Terminer" : "Suivant →"}</button>
         </div>`;
      box.querySelector(".tour-skip").addEventListener("click", end);
      box.querySelector(".tour-next").addEventListener("click", () => last ? end() : show(i + 1));
      box.querySelector(".tour-next").focus();
    }
    function start() {
      if (!box) { box = document.createElement("div"); box.className = "tour-pop";
        box.setAttribute("role", "dialog"); box.setAttribute("aria-live", "polite");
        document.body.appendChild(box); }
      box.hidden = false; show(0);
    }
    function end() { if (box) box.hidden = true; btn.focus(); }
    btn.addEventListener("click", start);
    document.addEventListener("keydown", e => { if (e.key === "Escape" && box && !box.hidden) end(); });
  })();

  /* Démarrage */
  hydrate();
  go(startStep);
})();

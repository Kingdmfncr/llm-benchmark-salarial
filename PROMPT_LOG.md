# PROMPT_LOG — Benchmark Salarial IA

*Trace transparente de la méthode IA utilisée pour construire ce projet*

---

## Objectif

Construire un outil qui transforme des offres d'emploi en texte brut en données structurées
exploitables pour un benchmark C&B — sans scraping, sans base de données externe.

---

## Prompt principal (extraction structurée)

**Modèle utilisé :** `claude-haiku-4-5-20251001` (rapide, < 0.01€/offre)

**Prompt :**
```
Tu es un expert C&B (Compensation & Benefits) et analyste RH.
Analyse cette offre d'emploi et extrais les informations structurées suivantes en JSON.

OFFRE :
{texte_offre}

Retourne UNIQUEMENT un objet JSON valide avec ces clés exactes :
{
  "titre_poste": "string",
  "entreprise": "string ou null",
  "secteur": "string",
  "localisation": "string",
  "teletravail": "Oui / Non / Partiel / Non précisé",
  "type_contrat": "CDI / CDD / Freelance / Mission / Alternance",
  "salaire_min": number ou null (en € annuel brut, convertir TJM × 220 si freelance),
  "salaire_max": number ou null,
  "devise": "EUR",
  "tjm_min": number ou null (si freelance/mission),
  "tjm_max": number ou null,
  "experience_min_ans": number ou null,
  "experience_max_ans": number ou null,
  "niveau_seniorite": "Junior / Confirmé / Senior / Expert",
  "competences_cles": ["liste", "de", "compétences"],
  "sirh_cites": ["liste", "des", "SIRH/outils", "cités"],
  "avantages": ["liste", "des", "avantages"],
  "statut_cadre": true ou false,
  "score_attractivite": number entre 0 et 100,
  "resume_analyse": "2 phrases max sur le profil recherché et points saillants"
}
```

**Décisions de prompt engineering :**
- Persona expert C&B explicite → meilleure interprétation des nuances salariales
- Conversion TJM → annuel dans le prompt (TJM × 220 jours) → comparabilité directe CDI vs freelance
- JSON strict imposé → parsing fiable sans post-traitement complexe
- Score d'attractivité calculé par le modèle (pas par règles hardcodées) → contextuel au marché

---

## Décisions d'architecture

| Décision | Raison |
|----------|--------|
| Claude Haiku (pas Sonnet) | Coût ×5 moins cher, qualité suffisante pour extraction structurée |
| Mode démo sans API key | Portfolio public — le visiteur peut tester sans coût pour Gisèle |
| BYOK (Bring Your Own Key) | Pas de coût API côté hébergement, scalable à 0€ |
| JSON parsé avec regex fallback | Haiku parfois entoure le JSON de ``` — le regex extrait quand même |
| Export CSV avec BOM UTF-8 | Compatible Excel français sans problème d'encodage |

---

## Limites connues

- Le score d'attractivité est subjectif (calculé par le LLM, pas par règles fixes)
- Les salaires non mentionnés dans l'offre sont null — l'IA n'invente pas
- Mode démo = résultats pré-calculés sur 4 offres exemples (pas de vrai appel API)

---

*Projet construit avec Claude Code (Anthropic) · Gisèle Metouck · 2026*

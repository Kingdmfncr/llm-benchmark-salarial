# 🧠 Benchmark Salarial IA

**Transformez des offres d'emploi brutes en benchmark C&B structuré — en 30 secondes**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://llm-benchmark-salarial.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)](https://python.org)
[![Claude API](https://img.shields.io/badge/Claude-Haiku-00ff88?style=flat-square)](https://anthropic.com)

---

## Ce que ça fait

Collez du texte brut d'offres d'emploi (LinkedIn, Indeed, Welcome to the Jungle...).
L'IA extrait automatiquement :

- Fourchettes salariales (CDI et TJM freelance normalisés en annuel)
- Compétences et SIRH les plus demandés
- Score d'attractivité par offre
- Benchmark visuel comparatif

**Export CSV compatible Excel** pour intégration directe dans vos outils C&B.

---

## Démo immédiate

👉 **[Ouvrir l'app](https://llm-benchmark-salarial.streamlit.app)**

Mode démo disponible sans clé API — 4 offres réelles pré-chargées (Pharma, BTP, Énergie, Tech RH).

---

## Utiliser avec votre propre clé API

1. Obtenez une clé sur [console.anthropic.com](https://console.anthropic.com)
2. Entrez-la dans la sidebar de l'app
3. Analysez vos propres offres — ~0.01€ par offre (Claude Haiku)

---

## Cas d'usage C&B

- Benchmark marché avant une revue salariale annuelle
- Veille package concurrentielle (salaire, télétravail, avantages)
- Cartographie des compétences SIRH les plus demandées dans votre secteur
- Préparation d'une grille de classification interne

---

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Interface | Streamlit |
| Extraction IA | Claude Haiku (Anthropic API) |
| Traitement données | Pandas |
| Visualisations | Plotly |
| Export | CSV UTF-8 BOM (compatible Excel FR) |

---

## Méthode IA

Voir [`PROMPT_LOG.md`](PROMPT_LOG.md) — trace complète des prompts, décisions d'architecture, et limites.

---

## Adapter à votre contexte

Ce projet est open source. Pour l'adapter à votre secteur ou vos critères :

1. Modifiez le schéma JSON dans le prompt (`app.py` ligne ~60)
2. Ajoutez vos propres offres d'exemple dans `EXEMPLES`
3. Ajustez les critères du score d'attractivité selon vos priorités

---

## Playbook

Guide opératoire complet (Définitions/Process/Documentation/Templates) : [`PLAYBOOK.md`](PLAYBOOK.md).

## Freelance

Je livre ce type d'outil en **2-3 semaines** pour votre contexte spécifique :
benchmark sectoriel, revue salariale automatisée, veille compétences SIRH.

📩 metouck.gisele@gmail.com

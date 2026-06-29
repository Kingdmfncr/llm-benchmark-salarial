import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Benchmark Salarial IA | Gisèle Metouck",
    page_icon="🧠",
    layout="wide",
)

# ─── Design System ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0a0a0a; color: #ffffff; }
  [data-testid="stSidebar"] { background: #16213e; }
  [data-testid="stSidebar"] * { color: #ffffff !important; }
  h1 { color: #ffffff; font-size: 2rem; font-weight: bold; }
  h2 { color: #00ff88; font-size: 1.4rem; }
  h3 { color: #ffffff; font-size: 1.1rem; }
  .stTabs [data-baseweb="tab"] { color: #888888; }
  .stTabs [aria-selected="true"] { color: #00ff88 !important; border-bottom: 2px solid #00ff88; }
  .stTextArea textarea { background: #1a1a2e; color: #ffffff; border: 1px solid rgba(0,255,136,0.3); }
  .stTextInput input { background: #1a1a2e; color: #ffffff; border: 1px solid rgba(0,255,136,0.3); }
  div[data-testid="metric-container"] {
    background: #1a1a2e; border-radius: 8px; padding: 16px;
    border-left: 3px solid #00ff88;
  }
  .kpi-card {
    background: #1a1a2e; border-radius: 8px; padding: 16px;
    border-left: 3px solid #00ff88; margin: 4px 0;
  }
  .alert-warning {
    background: #3d2f00; border-left: 4px solid #ffd700;
    border-radius: 4px; padding: 10px 16px; margin: 4px 0;
    color: #ffffff;
  }
  .alert-ok {
    background: #003d1a; border-left: 4px solid #00ff88;
    border-radius: 4px; padding: 10px 16px; margin: 4px 0;
    color: #ffffff;
  }
  .tag {
    display: inline-block; background: #003d1a; color: #00ff88;
    border: 1px solid #00ff88; border-radius: 4px;
    padding: 2px 8px; margin: 2px; font-size: 0.8rem;
  }
  .footer-caption { color: #888888; font-size: 0.8rem; text-align: center; margin-top: 32px; }
</style>
""", unsafe_allow_html=True)

# ─── Chart defaults ──────────────────────────────────────────────────────────
CHART_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#1a1a2e",
    font_color="#ffffff",
    font_family="sans-serif",
    title_font_color="#00ff88",
    title_font_size=16,
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="white")),
    margin=dict(l=20, r=20, t=40, b=20),
)

PALETTE = ["#00ff88", "#ffd700", "#4ecdc4", "#ff4444", "#a855f7"]

# ─── Exemples pré-chargés ────────────────────────────────────────────────────
EXEMPLES = [
    {
        "titre": "Chargé C&B — Pharma (MAYOLY)",
        "texte": """Chargé de Compensation & Benefits H/F - CDI Paris 15e
Rémunération : 42 000 - 50 000 € brut annuel
Secteur : Industrie pharmaceutique, 500 salariés
Compétences requises : Excel avancé, Workday, Power BI, connaissance SIRH
Niveau d'expérience : 3-5 ans en C&B
Avantages : Télétravail 2j/semaine, mutuelle, intéressement
Type de contrat : CDI, statut cadre"""
    },
    {
        "titre": "Responsable Reporting Social — BTP (VINCI)",
        "texte": """Responsable Reporting Social & Bilan Social H/F - CDI Rueil-Malmaison
Package : 55 000 - 65 000 € selon profil
Secteur : BTP, Grands Groupes, 10 000+ salariés
Compétences : SAP HR, Excel, SQL, maîtrise bilan social légal, Index H/F
Expérience : 5+ ans reporting RH grands groupes
Avantages : RTT, participation, télétravail 3j/sem
Contrat : CDI Cadre"""
    },
    {
        "titre": "Data Analyst RH — Énergie (TotalEnergies)",
        "texte": """Data Analyst RH H/F - Mission 6 mois renouvelable - La Défense
TJM : 450-550 € / jour
Secteur : Énergie, groupe international
Compétences : SQL avancé, Python, Power BI, Tableau, dbt
Expérience : 4+ ans analyse de données RH
Contexte : Projet migration SIRH, consolidation KPIs groupe
Localisation : Présentiel requis 3j/semaine"""
    },
    {
        "titre": "Product Owner SIRH — Startups",
        "texte": """Product Owner SIRH H/F - CDI Lyon ou Remote
Salaire : 48 000 - 58 000 € + BSPCE
Secteur : SaaS RH, scale-up 100-300 salariés
Compétences : Agile/Scrum, rédaction User Stories, Notion, Jira, intégrations API
Expérience : 3 ans minimum Product Owner ou Business Analyst
Avantages : Full remote, stock-options, carte Swile
Contrat : CDI"""
    },
]

# ─── Parser Claude (via API) ──────────────────────────────────────────────────
def parse_with_claude(texte_offre: str, api_key: str) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Tu es un expert C&B (Compensation & Benefits) et analyste RH.
Analyse cette offre d'emploi et extrais les informations structurées suivantes en JSON.

OFFRE :
{texte_offre}

Retourne UNIQUEMENT un objet JSON valide avec ces clés exactes :
{{
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
}}

Règles :
- salaire_min/max toujours en € annuel brut (TJM × 220 jours si mission)
- score_attractivite : basé sur salaire, télétravail, avantages, stabilité contrat
- Ne retourne que le JSON, pas de texte avant ou après"""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        # Extraire le JSON même si entouré de ```
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(raw)
    except ImportError:
        st.error("Package 'anthropic' manquant. Ajoutez-le à requirements.txt.")
        return None
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None


# ─── Parser sans API (démo) ──────────────────────────────────────────────────
DEMO_RESULTS = {
    EXEMPLES[0]["titre"]: {
        "titre_poste": "Chargé C&B", "entreprise": "MAYOLY", "secteur": "Pharma",
        "localisation": "Paris 15e", "teletravail": "Partiel", "type_contrat": "CDI",
        "salaire_min": 42000, "salaire_max": 50000, "devise": "EUR",
        "tjm_min": None, "tjm_max": None,
        "experience_min_ans": 3, "experience_max_ans": 5, "niveau_seniorite": "Confirmé",
        "competences_cles": ["Excel avancé", "Workday", "Power BI", "SIRH"],
        "sirh_cites": ["Workday"], "avantages": ["Télétravail 2j/sem", "Mutuelle", "Intéressement"],
        "statut_cadre": True, "score_attractivite": 72,
        "resume_analyse": "Poste C&B classique pharma, bon package. Workday requis est un filtre fort.",
    },
    EXEMPLES[1]["titre"]: {
        "titre_poste": "Responsable Reporting Social", "entreprise": "VINCI", "secteur": "BTP",
        "localisation": "Rueil-Malmaison", "teletravail": "Partiel", "type_contrat": "CDI",
        "salaire_min": 55000, "salaire_max": 65000, "devise": "EUR",
        "tjm_min": None, "tjm_max": None,
        "experience_min_ans": 5, "experience_max_ans": None, "niveau_seniorite": "Senior",
        "competences_cles": ["SAP HR", "Excel", "SQL", "Bilan Social", "Index H/F"],
        "sirh_cites": ["SAP HR"], "avantages": ["RTT", "Participation", "Télétravail 3j/sem"],
        "statut_cadre": True, "score_attractivite": 85,
        "resume_analyse": "Poste très attractif — package élevé, télétravail généreux, légal RH exigeant.",
    },
    EXEMPLES[2]["titre"]: {
        "titre_poste": "Data Analyst RH", "entreprise": "TotalEnergies", "secteur": "Énergie",
        "localisation": "La Défense", "teletravail": "Partiel", "type_contrat": "Mission",
        "salaire_min": 99000, "salaire_max": 121000, "devise": "EUR",
        "tjm_min": 450, "tjm_max": 550,
        "experience_min_ans": 4, "experience_max_ans": None, "niveau_seniorite": "Confirmé",
        "competences_cles": ["SQL", "Python", "Power BI", "Tableau", "dbt"],
        "sirh_cites": [], "avantages": ["TJM attractif", "Mission renouvelable"],
        "statut_cadre": False, "score_attractivite": 78,
        "resume_analyse": "Mission technique pure, profil data engineer RH. Présentiel 3j contraignant.",
    },
    EXEMPLES[3]["titre"]: {
        "titre_poste": "Product Owner SIRH", "entreprise": "Scale-up SaaS RH", "secteur": "Tech RH",
        "localisation": "Lyon / Remote", "teletravail": "Oui", "type_contrat": "CDI",
        "salaire_min": 48000, "salaire_max": 58000, "devise": "EUR",
        "tjm_min": None, "tjm_max": None,
        "experience_min_ans": 3, "experience_max_ans": None, "niveau_seniorite": "Confirmé",
        "competences_cles": ["Agile", "User Stories", "Notion", "Jira", "API"],
        "sirh_cites": ["Notion", "Jira"], "avantages": ["Full remote", "BSPCE", "Carte Swile"],
        "statut_cadre": False, "score_attractivite": 80,
        "resume_analyse": "Full remote + equity = très attractif pour profil PO expérimenté.",
    },
}


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Benchmark Salarial IA")
    st.markdown("*Extrait des données structurées depuis des offres d'emploi brutes*")
    st.divider()

    mode = st.radio("Mode", ["🎯 Démo (sans API)", "🔑 Avec ma clé Claude API"], index=0)

    api_key = None
    if mode == "🔑 Avec ma clé Claude API":
        api_key = st.text_input("Clé API Anthropic", type="password", placeholder="sk-ant-...")
        st.caption("Votre clé n'est jamais stockée. [Obtenir une clé](https://console.anthropic.com)")

    st.divider()
    st.caption("Coût estimé : ~0.01€ par offre analysée (Claude Haiku)")
    st.divider()
    st.caption("🔗 [GitHub](https://github.com/Kingdmfncr/market-tension-radar) · Gisèle Metouck")


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("# 🧠 Benchmark Salarial IA")
st.markdown("**Analysez des offres d'emploi avec Claude · Extrayez salaires, compétences, attractivité**")
st.divider()

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📥 Analyser des offres", "📊 Benchmark & Comparaison", "📋 Export & Méthode"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Saisie et analyse
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## Saisir vos offres")

    use_exemples = st.checkbox("Charger les 4 offres d'exemple (Pharma, BTP, Énergie, Tech)", value=True)

    if use_exemples:
        offres_input = EXEMPLES.copy()
        st.markdown(
            '<div class="alert-ok">✅ 4 offres pré-chargées — cliquez <b>Analyser</b> pour lancer</div>',
            unsafe_allow_html=True
        )
        for ex in EXEMPLES:
            with st.expander(f"📄 {ex['titre']}"):
                st.text(ex["texte"])
    else:
        st.markdown("Collez une ou plusieurs offres d'emploi (texte libre) :")
        offres_input = []
        n = st.number_input("Nombre d'offres à analyser", min_value=1, max_value=10, value=2)
        for i in range(n):
            with st.expander(f"Offre {i+1}", expanded=(i == 0)):
                titre = st.text_input(f"Titre court (référence)", key=f"titre_{i}", placeholder="ex: Chargé C&B Pharma CDI")
                texte = st.text_area(f"Texte de l'offre", key=f"texte_{i}", height=150,
                                     placeholder="Copiez-collez le texte brut de l'offre...")
                if titre and texte:
                    offres_input.append({"titre": titre, "texte": texte})

    st.divider()

    if st.button("🚀 Analyser avec l'IA", type="primary", use_container_width=True):
        if not offres_input:
            st.warning("Ajoutez au moins une offre.")
        else:
            resultats = {}
            progress = st.progress(0, text="Analyse en cours...")

            for idx, offre in enumerate(offres_input):
                progress.progress((idx) / len(offres_input), text=f"Analyse : {offre['titre']}...")

                if mode == "🎯 Démo (sans API)":
                    # Résultats démo pré-calculés
                    res = DEMO_RESULTS.get(offre["titre"])
                    if not res:
                        # Génère un résultat générique si offre personnalisée
                        res = {
                            "titre_poste": offre["titre"], "entreprise": "N/A", "secteur": "N/A",
                            "localisation": "N/A", "teletravail": "Non précisé", "type_contrat": "CDI",
                            "salaire_min": 40000, "salaire_max": 55000, "devise": "EUR",
                            "tjm_min": None, "tjm_max": None,
                            "experience_min_ans": 3, "experience_max_ans": 5,
                            "niveau_seniorite": "Confirmé",
                            "competences_cles": ["Excel", "SIRH", "Reporting"],
                            "sirh_cites": [], "avantages": ["À préciser"],
                            "statut_cadre": True, "score_attractivite": 65,
                            "resume_analyse": "Résultat démo. Activez la clé API pour une vraie analyse.",
                        }
                    resultats[offre["titre"]] = res
                else:
                    if not api_key:
                        st.error("Entrez votre clé API dans la sidebar.")
                        break
                    res = parse_with_claude(offre["texte"], api_key)
                    if res:
                        resultats[offre["titre"]] = res

            progress.progress(1.0, text="✅ Analyse terminée")
            st.session_state["resultats"] = resultats
            st.success(f"✅ {len(resultats)} offre(s) analysée(s)")

    # Aperçu rapide si résultats en session
    if "resultats" in st.session_state and st.session_state["resultats"]:
        st.divider()
        st.markdown("## Résultats par offre")
        for titre, r in st.session_state["resultats"].items():
            score = r.get("score_attractivite", 0)
            color = "#00ff88" if score >= 70 else "#ffd700" if score >= 45 else "#ff4444"
            with st.expander(f"{'🟢' if score >= 70 else '🟡' if score >= 45 else '🔴'} {titre} — Score {score}/100"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Salaire min", f"{r.get('salaire_min', 'N/A'):,} €" if r.get('salaire_min') else "N/A")
                c2.metric("Salaire max", f"{r.get('salaire_max', 'N/A'):,} €" if r.get('salaire_max') else "N/A")
                c3.metric("Expérience", f"{r.get('experience_min_ans', '?')} ans min")
                c4.metric("Contrat", r.get("type_contrat", "N/A"))

                if r.get("competences_cles"):
                    tags = " ".join([f'<span class="tag">{c}</span>' for c in r["competences_cles"]])
                    st.markdown(f"**Compétences :** {tags}", unsafe_allow_html=True)

                if r.get("resume_analyse"):
                    st.markdown(f'<div class="alert-ok">💡 {r["resume_analyse"]}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Benchmark
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    if "resultats" not in st.session_state or not st.session_state["resultats"]:
        st.info("Lancez d'abord une analyse dans l'onglet **Analyser des offres**.")
    else:
        resultats = st.session_state["resultats"]
        df = pd.DataFrame([
            {
                "Offre": titre,
                "Poste": r.get("titre_poste", titre),
                "Secteur": r.get("secteur", "N/A"),
                "Contrat": r.get("type_contrat", "N/A"),
                "Salaire min (€)": r.get("salaire_min"),
                "Salaire max (€)": r.get("salaire_max"),
                "Salaire médian (€)": int((r.get("salaire_min", 0) + r.get("salaire_max", 0)) / 2)
                    if r.get("salaire_min") and r.get("salaire_max") else None,
                "TJM min (€)": r.get("tjm_min"),
                "TJM max (€)": r.get("tjm_max"),
                "Expérience min (ans)": r.get("experience_min_ans"),
                "Séniorité": r.get("niveau_seniorite", "N/A"),
                "Télétravail": r.get("teletravail", "N/A"),
                "Score attractivité": r.get("score_attractivite", 0),
            }
            for titre, r in resultats.items()
        ])

        st.markdown("## Benchmark comparatif")

        # KPIs globaux
        salaires = df["Salaire médian (€)"].dropna()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Offres analysées", len(df))
        c2.metric("Salaire médian marché", f"{int(salaires.median()):,} €" if len(salaires) else "N/A")
        c3.metric("Fourchette marché",
                  f"{int(salaires.min()):,} – {int(salaires.max()):,} €" if len(salaires) > 1 else "N/A")
        c4.metric("Score attractivité moyen", f"{int(df['Score attractivité'].mean())}/100")

        st.divider()

        # Graphique salaires
        df_sal = df[df["Salaire min (€)"].notna()].copy()
        if not df_sal.empty:
            fig_sal = go.Figure()
            fig_sal.add_trace(go.Bar(
                x=df_sal["Offre"], y=df_sal["Salaire min (€)"],
                name="Min", marker_color="#4ecdc4"
            ))
            fig_sal.add_trace(go.Bar(
                x=df_sal["Offre"], y=df_sal["Salaire max (€)"],
                name="Max", marker_color="#00ff88"
            ))
            fig_sal.update_layout(
                **CHART_DEFAULTS,
                title="Fourchettes salariales (€ brut annuel)",
                barmode="group",
                xaxis_tickangle=-20,
            )
            st.plotly_chart(fig_sal, use_container_width=True, key="chart_salaires")

        col1, col2 = st.columns(2)

        with col1:
            # Score attractivité
            fig_score = px.bar(
                df.sort_values("Score attractivité", ascending=True),
                x="Score attractivité", y="Offre", orientation="h",
                color="Score attractivité",
                color_continuous_scale=["#ff4444", "#ffd700", "#00ff88"],
                range_color=[0, 100],
                title="Score d'attractivité",
            )
            fig_score.update_layout(**CHART_DEFAULTS)
            fig_score.update_coloraxes(showscale=False)
            st.plotly_chart(fig_score, use_container_width=True, key="chart_score")

        with col2:
            # Répartition télétravail
            teletravail_counts = df["Télétravail"].value_counts().reset_index()
            teletravail_counts.columns = ["Télétravail", "count"]
            fig_tt = px.pie(
                teletravail_counts, values="count", names="Télétravail",
                title="Répartition télétravail",
                color_discrete_sequence=PALETTE,
                hole=0.4,
            )
            fig_tt.update_layout(**CHART_DEFAULTS)
            st.plotly_chart(fig_tt, use_container_width=True, key="chart_teletravail")

        st.divider()
        st.markdown("## Tableau complet")
        st.dataframe(
            df[["Offre", "Secteur", "Contrat", "Salaire min (€)", "Salaire max (€)",
                "Séniorité", "Télétravail", "Score attractivité"]],
            use_container_width=True,
            hide_index=True,
        )

        # Compétences les plus demandées
        st.divider()
        st.markdown("## Compétences les plus demandées")
        all_skills = []
        for r in resultats.values():
            all_skills.extend(r.get("competences_cles", []))
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts().head(12).reset_index()
            skill_counts.columns = ["Compétence", "Fréquence"]
            fig_sk = px.bar(
                skill_counts, x="Fréquence", y="Compétence", orientation="h",
                color="Fréquence", color_continuous_scale=["#4ecdc4", "#00ff88"],
                title="Compétences citées dans les offres",
            )
            fig_sk.update_layout(**CHART_DEFAULTS)
            fig_sk.update_coloraxes(showscale=False)
            st.plotly_chart(fig_sk, use_container_width=True, key="chart_skills")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Export & Méthode
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## Export des données")

    if "resultats" in st.session_state and st.session_state["resultats"]:
        resultats = st.session_state["resultats"]
        df_export = pd.DataFrame([
            {
                "Offre": titre,
                "Poste": r.get("titre_poste"), "Entreprise": r.get("entreprise"),
                "Secteur": r.get("secteur"), "Localisation": r.get("localisation"),
                "Contrat": r.get("type_contrat"), "Télétravail": r.get("teletravail"),
                "Salaire min": r.get("salaire_min"), "Salaire max": r.get("salaire_max"),
                "TJM min": r.get("tjm_min"), "TJM max": r.get("tjm_max"),
                "Expérience min (ans)": r.get("experience_min_ans"),
                "Séniorité": r.get("niveau_seniorite"),
                "Compétences": ", ".join(r.get("competences_cles", [])),
                "SIRH cités": ", ".join(r.get("sirh_cites", [])),
                "Avantages": ", ".join(r.get("avantages", [])),
                "Score attractivité": r.get("score_attractivite"),
                "Analyse IA": r.get("resume_analyse"),
            }
            for titre, r in resultats.items()
        ])

        csv = df_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            "⬇️ Télécharger le benchmark (CSV)",
            data=csv,
            file_name="benchmark_salarial_ia.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("Encodage UTF-8 BOM — compatible Excel français")
    else:
        st.info("Lancez d'abord une analyse pour générer l'export.")

    st.divider()
    st.markdown("## Comment ça marche")

    st.markdown("""
**Étape 1 — Collecte**
Vous collez du texte brut d'offres d'emploi (copié depuis LinkedIn, Indeed, Welcome to the Jungle, etc.).

**Étape 2 — Extraction IA**
Claude Haiku (le modèle le plus rapide d'Anthropic) reçoit chaque offre avec un prompt structuré.
Il extrait : salaire, compétences, SIRH, séniorité, télétravail, avantages, score d'attractivité.

**Étape 3 — Structuration**
Le résultat JSON est transformé en DataFrame Pandas pour comparaison et visualisation.

**Étape 4 — Export**
Un CSV compatible Excel est généré pour usage dans vos outils C&B habituels.

---
**Cas d'usage C&B :**
- Benchmark marché avant une revue salariale
- Veille concurrentielle sur les packages proposés
- Identification des SIRH les plus demandés dans votre secteur
- Cartographie des compétences rares vs. communes
""")

    st.divider()
    st.markdown(
        '<div class="footer-caption">Construit avec l\'IA · Gisèle Metouck · '
        '<a href="https://github.com/Kingdmfncr" style="color:#00ff88">GitHub</a></div>',
        unsafe_allow_html=True
    )

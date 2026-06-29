import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import io

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Benchmark Salarial IA | Gisèle Metouck",
    page_icon="🧠",
    layout="wide",
)

# ─── Design System ────────────────────────────────────────────────────────────
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
  .alert-warning {
    background: #3d2f00; border-left: 4px solid #ffd700;
    border-radius: 4px; padding: 10px 16px; margin: 4px 0; color: #ffffff;
  }
  .alert-ok {
    background: #003d1a; border-left: 4px solid #00ff88;
    border-radius: 4px; padding: 10px 16px; margin: 4px 0; color: #ffffff;
  }
  .alert-danger {
    background: #3d0000; border-left: 4px solid #ff4444;
    border-radius: 4px; padding: 10px 16px; margin: 4px 0; color: #ffffff;
  }
  .tag {
    display: inline-block; background: #003d1a; color: #00ff88;
    border: 1px solid #00ff88; border-radius: 4px;
    padding: 2px 8px; margin: 2px; font-size: 0.8rem;
  }
  .tag-match {
    display: inline-block; background: #003d1a; color: #00ff88;
    border: 1px solid #00ff88; border-radius: 4px;
    padding: 2px 8px; margin: 2px; font-size: 0.8rem; font-weight: bold;
  }
  .tag-miss {
    display: inline-block; background: #3d0000; color: #ff8888;
    border: 1px solid #ff4444; border-radius: 4px;
    padding: 2px 8px; margin: 2px; font-size: 0.8rem;
  }
  .fit-card {
    background: #1a1a2e; border-radius: 8px; padding: 16px;
    margin: 8px 0; border: 1px solid rgba(0,255,136,0.2);
  }
  .footer-caption { color: #888888; font-size: 0.8rem; text-align: center; margin-top: 32px; }
  .export-info {
    background: #1a1a2e; border-radius: 8px; padding: 12px 16px;
    border: 1px solid rgba(0,255,136,0.3); margin: 8px 0; font-size: 0.9rem;
  }
</style>
""", unsafe_allow_html=True)

# ─── Chart defaults ───────────────────────────────────────────────────────────
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

# ─── Exemples pré-chargés ─────────────────────────────────────────────────────
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

# ─── Résultats démo ───────────────────────────────────────────────────────────
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

# ─── Scoring fit profil ───────────────────────────────────────────────────────
def compute_fit(offre: dict, profil: dict) -> dict:
    score = 0
    details = []

    # 1. Salaire
    sal_min_offre = offre.get("salaire_min") or 0
    sal_cible = profil["salaire_cible"]
    if sal_min_offre >= sal_cible:
        score += 30
        details.append(("✅", "Salaire", f"{sal_min_offre:,} € ≥ cible {sal_cible:,} €"))
    elif sal_min_offre >= sal_cible * 0.85:
        score += 15
        details.append(("🟡", "Salaire", f"{sal_min_offre:,} € — proche de la cible ({sal_cible:,} €)"))
    else:
        details.append(("❌", "Salaire", f"{sal_min_offre:,} € < cible {sal_cible:,} €"))

    # 2. Contrat
    contrats_acceptes = profil["contrats_acceptes"]
    contrat_offre = offre.get("type_contrat", "")
    if any(c.lower() in contrat_offre.lower() for c in contrats_acceptes):
        score += 25
        details.append(("✅", "Contrat", contrat_offre))
    else:
        details.append(("❌", "Contrat", f"{contrat_offre} — non dans {contrats_acceptes}"))

    # 3. Télétravail
    tt_offre = offre.get("teletravail", "Non précisé")
    tt_pref = profil["teletravail_min"]
    tt_map = {"Oui": 3, "Partiel": 2, "Non précisé": 1, "Non": 0}
    tt_pref_map = {"Full remote": 3, "Partiel accepté": 2, "Pas de contrainte": 1}
    if tt_map.get(tt_offre, 0) >= tt_pref_map.get(tt_pref, 1):
        score += 20
        details.append(("✅", "Télétravail", tt_offre))
    else:
        score += 5
        details.append(("🟡", "Télétravail", f"{tt_offre} — préférence : {tt_pref}"))

    # 4. Compétences
    skills_profil = [s.lower() for s in profil["competences"]]
    skills_offre = [s.lower() for s in offre.get("competences_cles", [])]
    matches = [s for s in skills_offre if any(p in s or s in p for p in skills_profil)]
    ratio = len(matches) / len(skills_offre) if skills_offre else 0
    skill_score = int(ratio * 25)
    score += skill_score
    details.append(("✅" if ratio >= 0.5 else "🟡", "Compétences",
                    f"{len(matches)}/{len(skills_offre)} compétences matchées ({int(ratio*100)}%)"))

    return {
        "score_fit": min(score, 100),
        "details": details,
        "skills_match": matches,
        "skills_miss": [s for s in skills_offre if s not in matches],
    }


# ─── Parser Claude ────────────────────────────────────────────────────────────
def parse_with_claude(texte_offre: str, api_key: str) -> dict | None:
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
  "salaire_min": number ou null,
  "salaire_max": number ou null,
  "devise": "EUR",
  "tjm_min": number ou null,
  "tjm_max": number ou null,
  "experience_min_ans": number ou null,
  "experience_max_ans": number ou null,
  "niveau_seniorite": "Junior / Confirmé / Senior / Expert",
  "competences_cles": ["liste"],
  "sirh_cites": ["liste"],
  "avantages": ["liste"],
  "statut_cadre": true ou false,
  "score_attractivite": number entre 0 et 100,
  "resume_analyse": "2 phrases max"
}}
Règles : salaire_min/max toujours en € annuel brut (TJM × 220 si mission).
Ne retourne que le JSON."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group() if match else raw)
    except ImportError:
        st.error("Package 'anthropic' manquant.")
        return None
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None


# ─── Parser fichier batch ─────────────────────────────────────────────────────
def parse_batch_file(uploaded_file) -> list[dict]:
    """Parse un fichier .txt (offres séparées par ---) ou .csv (colonnes titre,texte)."""
    content = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(content), sep=None, engine="python", encoding="utf-8-sig")
            # Cherche colonnes titre et texte (insensible à la casse)
            col_map = {c.lower(): c for c in df.columns}
            titre_col = col_map.get("titre") or col_map.get("title") or df.columns[0]
            texte_col = col_map.get("texte") or col_map.get("text") or col_map.get("description") or df.columns[1]
            return [
                {"titre": str(row[titre_col]), "texte": str(row[texte_col])}
                for _, row in df.iterrows()
                if pd.notna(row[titre_col]) and pd.notna(row[texte_col])
            ]
        except Exception as e:
            st.error(f"Erreur lecture CSV : {e}")
            return []
    else:
        # .txt — offres séparées par ---
        text = content.decode("utf-8", errors="ignore")
        blocs = [b.strip() for b in re.split(r'\n---+\n', text) if b.strip()]
        offres = []
        for bloc in blocs:
            lines = bloc.split("\n")
            titre = lines[0].strip("# ").strip() if lines else "Offre sans titre"
            texte = "\n".join(lines[1:]).strip() if len(lines) > 1 else bloc
            offres.append({"titre": titre, "texte": texte})
        return offres


# ─── Export MTR ───────────────────────────────────────────────────────────────
def build_mtr_csv(resultats: dict) -> str:
    """Génère un CSV au format attendu par Market Tension Radar (offres_emploi.csv)."""
    rows = []
    for i, (titre, r) in enumerate(resultats.items(), 1):
        sal_min = r.get("salaire_min") or 0
        sal_max = r.get("salaire_max") or sal_min
        tt = r.get("teletravail", "Non précisé")
        tt_bool = "true" if tt in ["Oui", "Partiel"] else "false"
        rows.append({
            "id": f"mtr_{i:03d}",
            "titre": r.get("titre_poste", titre),
            "entreprise": r.get("entreprise", "N/A"),
            "secteur": r.get("secteur", "N/A"),
            "lieu": r.get("localisation", "N/A"),
            "teletravail": tt_bool,
            "salaire_min": sal_min,
            "salaire_max": sal_max,
            "hard_skills": "|".join(r.get("competences_cles", [])),
            "skills_bloquants": "|".join(r.get("sirh_cites", [])),
            "rare_skill_recherche": "",
            "autonomie_score": min(int(r.get("score_attractivite", 50) * 0.8), 100),
            "progression_score": 70,
            "avantages": "|".join(r.get("avantages", [])),
            "type_contrat": r.get("type_contrat", "CDI"),
            "secteur_accessible": "true",
            "fit_transformation": "true",
            "source": "Benchmark IA",
            "date_publication": pd.Timestamp.now().strftime("%Y-%m-%d"),
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False, encoding="utf-8-sig")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧠 Benchmark Salarial IA")
    st.markdown("*Extrait · Compare · Exporte vers MTR*")
    st.divider()

    # Mode API
    mode = st.radio("Mode", ["🎯 Démo (sans API)", "🔑 Avec ma clé Claude API"], index=0)
    api_key = None
    if mode == "🔑 Avec ma clé Claude API":
        api_key = st.text_input("Clé API Anthropic", type="password", placeholder="sk-ant-...")
        st.caption("Clé non stockée. ~0.01€/offre.")

    st.divider()

    # Profil candidat
    st.markdown("### 👤 Mon profil")
    st.caption("Utilisé pour le score de fit par offre")

    salaire_cible = st.number_input("Salaire cible (€ brut/an)", value=48000, step=1000)
    contrats_acceptes = st.multiselect(
        "Contrats acceptés",
        ["CDI", "CDD", "Mission", "Freelance"],
        default=["CDI", "Mission"],
    )
    teletravail_min = st.selectbox(
        "Télétravail minimum",
        ["Pas de contrainte", "Partiel accepté", "Full remote"],
        index=1,
    )
    competences_profil = st.text_area(
        "Mes compétences (une par ligne)",
        value="Excel\nAirtable\nNotion\nGestion de projet\nReporting RH\nUser Stories\nAgile\nPython\nStreamlit",
        height=150,
    )

    profil = {
        "salaire_cible": salaire_cible,
        "contrats_acceptes": contrats_acceptes,
        "teletravail_min": teletravail_min,
        "competences": [c.strip() for c in competences_profil.split("\n") if c.strip()],
    }

    st.divider()
    st.caption("🔗 [GitHub](https://github.com/Kingdmfncr) · Gisèle Metouck")


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 🧠 Benchmark Salarial IA")
st.markdown("**Analysez des offres · Scorez le fit avec votre profil · Exportez vers Market Tension Radar**")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Saisir des offres",
    "📊 Benchmark marché",
    "🎯 Fit avec mon profil",
    "📋 Export",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Saisie
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## Sources d'offres")

    source = st.radio(
        "Comment ajouter des offres ?",
        ["📋 Exemples pré-chargés", "✏️ Coller du texte", "📁 Importer un fichier (.txt / .csv)"],
        horizontal=True,
    )

    offres_input = []

    if source == "📋 Exemples pré-chargés":
        offres_input = EXEMPLES.copy()
        st.markdown('<div class="alert-ok">✅ 4 offres pré-chargées (Pharma, BTP, Énergie, Tech)</div>',
                    unsafe_allow_html=True)
        for ex in EXEMPLES:
            with st.expander(f"📄 {ex['titre']}"):
                st.text(ex["texte"])

    elif source == "✏️ Coller du texte":
        n = st.number_input("Nombre d'offres", min_value=1, max_value=10, value=2)
        for i in range(n):
            with st.expander(f"Offre {i+1}", expanded=(i == 0)):
                titre = st.text_input("Titre court", key=f"titre_{i}",
                                      placeholder="ex: Chargé C&B Pharma CDI")
                texte = st.text_area("Texte de l'offre", key=f"texte_{i}", height=150,
                                     placeholder="Collez le texte brut de l'offre...")
                if titre and texte:
                    offres_input.append({"titre": titre, "texte": texte})

    else:
        st.markdown("""
<div class="export-info">
<b>Format .txt</b> — Une offre par bloc, séparées par <code>---</code>.<br>
La première ligne de chaque bloc = titre de l'offre.<br><br>
<b>Format .csv</b> — Colonnes <code>titre</code> et <code>texte</code> (séparateur auto-détecté).
</div>
""", unsafe_allow_html=True)

        uploaded = st.file_uploader("Choisir un fichier", type=["txt", "csv"])
        if uploaded:
            offres_input = parse_batch_file(uploaded)
            if offres_input:
                st.success(f"✅ {len(offres_input)} offre(s) chargée(s)")
                for o in offres_input:
                    with st.expander(f"📄 {o['titre']}"):
                        st.text(o["texte"][:500] + ("..." if len(o["texte"]) > 500 else ""))

    # Template à télécharger
    with st.expander("📎 Télécharger un template CSV"):
        template_csv = "titre;texte\nChargé C&B CDI Paris;[Collez ici le texte de l'offre]\nData Analyst RH Mission;[Collez ici le texte de l'offre]"
        st.download_button("⬇️ Template CSV", data=template_csv.encode("utf-8-sig"),
                           file_name="template_offres.csv", mime="text/csv")

    st.divider()

    if st.button("🚀 Analyser avec l'IA", type="primary", use_container_width=True):
        if not offres_input:
            st.warning("Ajoutez au moins une offre.")
        else:
            resultats = {}
            progress = st.progress(0, text="Analyse en cours...")

            for idx, offre in enumerate(offres_input):
                progress.progress(idx / len(offres_input), text=f"Analyse : {offre['titre']}...")

                if mode == "🎯 Démo (sans API)":
                    res = DEMO_RESULTS.get(offre["titre"], {
                        "titre_poste": offre["titre"], "entreprise": "N/A", "secteur": "N/A",
                        "localisation": "N/A", "teletravail": "Non précisé", "type_contrat": "CDI",
                        "salaire_min": 40000, "salaire_max": 55000, "devise": "EUR",
                        "tjm_min": None, "tjm_max": None,
                        "experience_min_ans": 3, "experience_max_ans": 5, "niveau_seniorite": "Confirmé",
                        "competences_cles": ["Excel", "SIRH", "Reporting"],
                        "sirh_cites": [], "avantages": ["À préciser"],
                        "statut_cadre": True, "score_attractivite": 65,
                        "resume_analyse": "Mode démo — activez la clé API pour une analyse réelle.",
                    })
                    resultats[offre["titre"]] = res
                else:
                    if not api_key:
                        st.error("Entrez votre clé API dans la sidebar.")
                        break
                    res = parse_with_claude(offre["texte"], api_key)
                    if res:
                        resultats[offre["titre"]] = res

            progress.progress(1.0, text="✅ Terminé")
            st.session_state["resultats"] = resultats
            # Calcul fit pour chaque offre
            st.session_state["fits"] = {
                titre: compute_fit(r, profil)
                for titre, r in resultats.items()
            }
            st.success(f"✅ {len(resultats)} offre(s) analysée(s) — consultez les onglets Benchmark et Fit")

    # Aperçu rapide
    if "resultats" in st.session_state:
        st.divider()
        st.markdown("## Aperçu rapide")
        for titre, r in st.session_state["resultats"].items():
            score_att = r.get("score_attractivite", 0)
            fit = st.session_state.get("fits", {}).get(titre, {})
            score_fit = fit.get("score_fit", 0)
            icon = "🟢" if score_att >= 70 else "🟡" if score_att >= 45 else "🔴"
            with st.expander(f"{icon} {titre} — Attractivité {score_att}/100 · Fit {score_fit}/100"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Salaire min", f"{r.get('salaire_min', 0):,} €" if r.get('salaire_min') else "N/A")
                c2.metric("Salaire max", f"{r.get('salaire_max', 0):,} €" if r.get('salaire_max') else "N/A")
                c3.metric("Contrat", r.get("type_contrat", "N/A"))
                c4.metric("Score fit", f"{score_fit}/100")
                if r.get("competences_cles"):
                    tags = " ".join([f'<span class="tag">{c}</span>' for c in r["competences_cles"]])
                    st.markdown(f"**Compétences :** {tags}", unsafe_allow_html=True)
                if r.get("resume_analyse"):
                    st.markdown(f'<div class="alert-ok">💡 {r["resume_analyse"]}</div>',
                                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Benchmark marché
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if "resultats" not in st.session_state or not st.session_state["resultats"]:
        st.info("Lancez d'abord une analyse dans **Saisir des offres**.")
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
                "TJM min": r.get("tjm_min"),
                "TJM max": r.get("tjm_max"),
                "Expérience min": r.get("experience_min_ans"),
                "Séniorité": r.get("niveau_seniorite", "N/A"),
                "Télétravail": r.get("teletravail", "N/A"),
                "Score attractivité": r.get("score_attractivite", 0),
            }
            for titre, r in resultats.items()
        ])

        st.markdown("## Benchmark comparatif")
        salaires = df["Salaire médian (€)"].dropna()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Offres analysées", len(df))
        c2.metric("Salaire médian marché",
                  f"{int(salaires.median()):,} €" if len(salaires) else "N/A")
        c3.metric("Fourchette marché",
                  f"{int(salaires.min()):,} – {int(salaires.max()):,} €" if len(salaires) > 1 else "N/A")
        c4.metric("Score attractivité moyen", f"{int(df['Score attractivité'].mean())}/100")

        st.divider()

        df_sal = df[df["Salaire min (€)"].notna()].copy()
        if not df_sal.empty:
            fig_sal = go.Figure()
            fig_sal.add_trace(go.Bar(x=df_sal["Offre"], y=df_sal["Salaire min (€)"],
                                     name="Min", marker_color="#4ecdc4"))
            fig_sal.add_trace(go.Bar(x=df_sal["Offre"], y=df_sal["Salaire max (€)"],
                                     name="Max", marker_color="#00ff88"))
            fig_sal.update_layout(**CHART_DEFAULTS, title="Fourchettes salariales (€ brut annuel)",
                                  barmode="group", xaxis_tickangle=-20)
            st.plotly_chart(fig_sal, use_container_width=True, key="chart_salaires")

        col1, col2 = st.columns(2)
        with col1:
            fig_score = px.bar(df.sort_values("Score attractivité", ascending=True),
                               x="Score attractivité", y="Offre", orientation="h",
                               color="Score attractivité",
                               color_continuous_scale=["#ff4444", "#ffd700", "#00ff88"],
                               range_color=[0, 100], title="Score d'attractivité")
            fig_score.update_layout(**CHART_DEFAULTS)
            fig_score.update_coloraxes(showscale=False)
            st.plotly_chart(fig_score, use_container_width=True, key="chart_score")

        with col2:
            tt_counts = df["Télétravail"].value_counts().reset_index()
            tt_counts.columns = ["Télétravail", "count"]
            fig_tt = px.pie(tt_counts, values="count", names="Télétravail",
                            title="Répartition télétravail",
                            color_discrete_sequence=PALETTE, hole=0.4)
            fig_tt.update_layout(**CHART_DEFAULTS)
            st.plotly_chart(fig_tt, use_container_width=True, key="chart_teletravail")

        st.divider()
        st.markdown("## Tableau complet")
        st.dataframe(
            df[["Offre", "Secteur", "Contrat", "Salaire min (€)", "Salaire max (€)",
                "Séniorité", "Télétravail", "Score attractivité"]],
            use_container_width=True, hide_index=True,
        )

        st.divider()
        st.markdown("## Compétences les plus demandées")
        all_skills = []
        for r in resultats.values():
            all_skills.extend(r.get("competences_cles", []))
        if all_skills:
            sc = pd.Series(all_skills).value_counts().head(12).reset_index()
            sc.columns = ["Compétence", "Fréquence"]
            fig_sk = px.bar(sc, x="Fréquence", y="Compétence", orientation="h",
                            color="Fréquence", color_continuous_scale=["#4ecdc4", "#00ff88"],
                            title="Compétences citées dans les offres")
            fig_sk.update_layout(**CHART_DEFAULTS)
            fig_sk.update_coloraxes(showscale=False)
            st.plotly_chart(fig_sk, use_container_width=True, key="chart_skills")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Fit profil
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if "fits" not in st.session_state or not st.session_state["fits"]:
        st.info("Lancez d'abord une analyse dans **Saisir des offres**.")
    else:
        fits = st.session_state["fits"]
        resultats = st.session_state["resultats"]

        st.markdown("## Score de fit avec votre profil")
        st.caption(f"Salaire cible : {profil['salaire_cible']:,} € · "
                   f"Contrats : {', '.join(profil['contrats_acceptes'])} · "
                   f"Télétravail : {profil['teletravail_min']}")

        # Classement
        df_fit = pd.DataFrame([
            {
                "Offre": titre,
                "Score fit": fit["score_fit"],
                "Score attractivité": resultats[titre].get("score_attractivite", 0),
            }
            for titre, fit in fits.items()
        ]).sort_values("Score fit", ascending=False)

        fig_fit = px.bar(
            df_fit, x="Score fit", y="Offre", orientation="h",
            color="Score fit",
            color_continuous_scale=["#ff4444", "#ffd700", "#00ff88"],
            range_color=[0, 100],
            title="Classement des offres par fit avec votre profil",
        )
        fig_fit.update_layout(**CHART_DEFAULTS)
        fig_fit.update_coloraxes(showscale=False)
        st.plotly_chart(fig_fit, use_container_width=True, key="chart_fit")

        st.divider()
        st.markdown("## Détail par offre")

        for titre in df_fit["Offre"]:
            fit = fits[titre]
            r = resultats[titre]
            score = fit["score_fit"]
            icon = "🟢" if score >= 70 else "🟡" if score >= 45 else "🔴"

            with st.expander(f"{icon} {titre} — Fit {score}/100"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Critères évalués**")
                    for emoji, critere, detail in fit["details"]:
                        st.markdown(f"{emoji} **{critere}** — {detail}")
                with c2:
                    st.markdown("**Compétences matchées**")
                    if fit["skills_match"]:
                        tags_match = " ".join([f'<span class="tag-match">✓ {s}</span>'
                                               for s in fit["skills_match"]])
                        st.markdown(tags_match, unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-warning">⚠️ Aucune compétence matchée</div>',
                                    unsafe_allow_html=True)

                    if fit["skills_miss"]:
                        st.markdown("**Compétences non maîtrisées**")
                        tags_miss = " ".join([f'<span class="tag-miss">✗ {s}</span>'
                                              for s in fit["skills_miss"]])
                        st.markdown(tags_miss, unsafe_allow_html=True)

                if score >= 70:
                    st.markdown('<div class="alert-ok">✅ Offre fortement recommandée — postulez en priorité</div>',
                                unsafe_allow_html=True)
                elif score >= 45:
                    st.markdown('<div class="alert-warning">🟡 Offre intéressante — quelques points à travailler</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-danger">❌ Faible compatibilité — à déprioritiser</div>',
                                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Export
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    if "resultats" not in st.session_state or not st.session_state["resultats"]:
        st.info("Lancez d'abord une analyse.")
    else:
        resultats = st.session_state["resultats"]
        fits = st.session_state.get("fits", {})

        st.markdown("## Exports disponibles")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Benchmark complet (CSV)")
            st.caption("Toutes les offres avec leurs données extraites + score fit. Compatible Excel français.")
            df_export = pd.DataFrame([
                {
                    "Offre": titre,
                    "Poste": r.get("titre_poste"), "Entreprise": r.get("entreprise"),
                    "Secteur": r.get("secteur"), "Localisation": r.get("localisation"),
                    "Contrat": r.get("type_contrat"), "Télétravail": r.get("teletravail"),
                    "Salaire min (€)": r.get("salaire_min"), "Salaire max (€)": r.get("salaire_max"),
                    "TJM min (€)": r.get("tjm_min"), "TJM max (€)": r.get("tjm_max"),
                    "Expérience min (ans)": r.get("experience_min_ans"),
                    "Séniorité": r.get("niveau_seniorite"),
                    "Compétences": ", ".join(r.get("competences_cles", [])),
                    "SIRH cités": ", ".join(r.get("sirh_cites", [])),
                    "Avantages": ", ".join(r.get("avantages", [])),
                    "Score attractivité": r.get("score_attractivite"),
                    "Score fit profil": fits.get(titre, {}).get("score_fit"),
                    "Analyse IA": r.get("resume_analyse"),
                }
                for titre, r in resultats.items()
            ])
            csv_bench = df_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button("⬇️ Télécharger le benchmark", data=csv_bench,
                               file_name="benchmark_salarial_ia.csv", mime="text/csv",
                               use_container_width=True)

        with col2:
            st.markdown("### 🎯 Export pour Market Tension Radar (CSV)")
            st.caption("Format direct pour importer ces offres dans l'app Market Tension Radar.")
            mtr_csv = build_mtr_csv(resultats)
            st.download_button("⬇️ Export → Market Tension Radar", data=mtr_csv.encode("utf-8-sig"),
                               file_name="offres_pour_mtr.csv", mime="text/csv",
                               use_container_width=True)
            st.markdown("""
<div class="export-info">
📌 <b>Comment utiliser :</b><br>
1. Téléchargez ce fichier<br>
2. Ouvrez <a href="https://market-tension-radar.streamlit.app" style="color:#00ff88">Market Tension Radar</a><br>
3. Activez le mode "Charger mes propres offres"<br>
4. Importez le fichier CSV
</div>
""", unsafe_allow_html=True)

        st.divider()
        st.markdown("## Comment ça marche")
        st.markdown("""
**Étape 1 — Collecte** : Texte collé, fichier .txt (blocs séparés par `---`) ou .csv (`titre;texte`).

**Étape 2 — Extraction IA** : Claude Haiku analyse chaque offre et retourne un JSON structuré
(salaire, compétences, SIRH, télétravail, score d'attractivité).

**Étape 3 — Scoring fit** : Votre profil (sidebar) est comparé à chaque offre sur 4 critères :
salaire, contrat, télétravail, compétences matchées.

**Étape 4 — Export** : CSV benchmark pour vos outils C&B + CSV compatible Market Tension Radar.
""")

    st.divider()
    st.markdown(
        '<div class="footer-caption">Construit avec l\'IA · Gisèle Metouck · '
        '<a href="https://github.com/Kingdmfncr" style="color:#00ff88">GitHub</a></div>',
        unsafe_allow_html=True,
    )

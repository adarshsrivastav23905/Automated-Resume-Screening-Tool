import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from src.audit_store import get_run, list_runs, save_run
from src.screening import score_resumes


st.set_page_config(
    page_title="HireLens | Screening Intelligence",
    page_icon=":material/monitoring:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #f4f7fb; }
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e6ebf2; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e6ebf2;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(30, 54, 88, 0.04);
    }
    [data-testid="stMetricLabel"] { color: #667085 !important; font-size: 0.82rem; }
    [data-testid="stMetricValue"] { color: #17223b !important; }
    .brand-row { display:flex; align-items:center; gap:10px; margin: 4px 0 18px; }
    .brand-mark { width:34px; height:34px; border-radius:9px; background:#315efb; color:white; display:flex; align-items:center; justify-content:center; font-weight:800; }
    .brand-name { color:#17223b; font-weight:800; letter-spacing:-0.02em; }
    .page-eyebrow { color:#315efb; font-size:.78rem; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }
    .page-title { color:#17223b; font-size:2rem; font-weight:760; letter-spacing:-0.035em; margin:2px 0 4px; }
    .page-subtitle { color:#667085; margin:0 0 18px; }
    .pipeline { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin-bottom:18px; }
    .pipeline div { background:#ffffff; border:1px solid #e6ebf2; border-radius:10px; color:#667085; padding:10px 8px; text-align:center; font-size:.78rem; }
    .pipeline b { color:#315efb; margin-right:5px; }
    .stTabs [data-baseweb="tab-list"] { background:#eef2f7; border-radius:10px; padding:4px; gap:2px; }
    .stTabs [data-baseweb="tab"] { border:0; border-radius:7px; padding:8px 14px; color:#667085; }
    .stTabs [aria-selected="true"] { background:#ffffff; color:#17223b; box-shadow:0 1px 4px rgba(30,54,88,.08); }
    .block-container { padding-top:1.25rem; padding-bottom:2rem; max-width:1480px; }
    [data-testid="stFileUploader"] section { background:#ffffff; border:1px dashed #b9c5d8; border-radius:12px; }
    .stButton button, .stDownloadButton button { border-radius:9px; font-weight:700; min-height:42px; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "ranking_results" not in st.session_state:
    st.session_state.ranking_results = None

with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
          <div class="brand-mark">HL</div>
          <div>
            <div class="brand-name">HireLens</div>
            <div style="color:#98a2b3;font-size:.74rem;">Recruitment Intelligence</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### Screening settings")
    st.caption("Configure how candidates are evaluated.")
    st.space("small")
    minimum_years = st.number_input(
        "Minimum experience",
        0.0, 30.0, 2.0, 0.5,
        help="Minimum relevant experience in years",
    )
    threshold = st.slider("Shortlist threshold", 0.0, 100.0, 50.0, 1.0)
    must_have_text = st.text_area(
        "Must-have skills",
        "python, sql, pandas, machine learning",
        height=90,
        help="Separate skills with commas",
    )
    nice_to_have_text = st.text_area(
        "Nice-to-have skills",
        "scikit-learn, tableau, docker",
        height=70,
        help="Optional skills that add a small ranking bonus",
    )
    with st.expander("Advanced score weights", icon=":material/tune:"):
        similarity_weight = st.slider("Similarity", 0, 100, 55)
        skill_weight = st.slider("Must-have skills", 0, 100, 35)
        experience_weight = st.slider("Experience", 0, 100, 10)
        if similarity_weight + skill_weight + experience_weight == 0:
            st.warning("At least one score weight must be greater than zero.")
    st.space("small")
    st.caption("Model: TF-IDF Hybrid  •  v2.2")

st.markdown(
    """
    <div class="page-eyebrow">Talent operations</div>
    <div class="page-title">Candidate ranking workspace</div>
    <p class="page-subtitle">Compare resume evidence against role requirements and review a clear, explainable shortlist.</p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pipeline">
      <div><b>01</b>Extract</div>
      <div><b>02</b>Normalize</div>
      <div><b>03</b>Match skills</div>
      <div><b>04</b>Compute score</div>
      <div><b>05</b>Rank candidates</div>
    </div>
    """,
    unsafe_allow_html=True,
)

default_job = ""
job_path = Path("data/job_description.txt")
if job_path.exists():
    default_job = job_path.read_text(encoding="utf-8")

with st.form("screening_form"):
    input_col, upload_col = st.columns([1.55, 1], gap="large")
    with input_col:
        st.subheader("Job requirements")
        job_description = st.text_area(
            "Job description",
            value=default_job,
            height=260,
            label_visibility="collapsed",
            placeholder="Paste the role description and required skills here...",
        )
    with upload_col:
        st.subheader("Candidate inputs")
        uploaded_files = st.file_uploader(
            "Upload resumes",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            help="TXT, PDF, and DOCX files are supported",
        )
        if uploaded_files:
            st.success(f"{len(uploaded_files)} resume(s) ready", icon=":material/upload_file:")
        else:
            st.caption("No resume files selected.")

    submitted = st.form_submit_button(
        "Run screening analysis",
        icon=":material/rocket_launch:",
        type="primary",
        width="stretch",
    )

if submitted:
    if not job_description.strip():
        st.error("Add a job description before running the analysis.", icon=":material/error:")
    elif not uploaded_files:
        st.warning("Upload at least one resume.", icon=":material/upload:")
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            for uploaded in uploaded_files:
                (temp_path / uploaded.name).write_bytes(uploaded.getvalue())

            must_have = [skill.strip() for skill in must_have_text.split(",") if skill.strip()]
            nice_to_have = [
                skill.strip()
                for skill in nice_to_have_text.split(",")
                if skill.strip()
            ]
            weight_total = similarity_weight + skill_weight + experience_weight
            if weight_total == 0:
                st.error("Configure at least one score weight.")
                st.stop()

            status = st.status("Running screening pipeline", expanded=True)
            status.write("Extracting resume content...")
            status.write("Cleaning text and identifying skills...")
            results = score_resumes(
                resume_directory=str(temp_path),
                job_description=job_description,
                must_have_skills=must_have,
                minimum_years=minimum_years,
                shortlist_threshold=threshold,
                nice_to_have_skills=nice_to_have,
                weights={
                    "similarity": similarity_weight,
                    "skills": skill_weight,
                    "experience": experience_weight,
                },
            )
            status.write("Calculating weighted ranks...")
            status.update(label="Screening complete", state="complete", expanded=False)

        st.session_state.ranking_results = results
        run_id = save_run(
            results,
            job_description,
            must_have,
            minimum_years,
            threshold,
        )
        st.toast("Candidate ranking generated", icon=":material/check_circle:")

results = st.session_state.ranking_results
if results is not None:
    st.space("medium")
    total = len(results)
    shortlisted = int((results["decision"] == "Shortlist").sum())
    review = int((results["decision"] == "Review").sum())
    rejected = int((results["decision"] == "Reject").sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Candidates analyzed", total, border=True)
    col2.metric("Shortlisted", shortlisted, border=True)
    col3.metric("Needs review", review, border=True)
    col4.metric("Rejected", rejected, border=True)

    ranking_tab, analytics_tab, history_tab = st.tabs([
        "Ranking report",
        "Score analytics",
        "Run history",
    ])

    with ranking_tab:
        display = results.copy()
        filter_col, search_col = st.columns([1, 2])
        with filter_col:
            decision_filter = st.segmented_control(
                "Decision",
                ["All", "Shortlist", "Review", "Reject"],
                default="All",
            )
        with search_col:
            candidate_search = st.text_input(
                "Search candidate",
                placeholder="Candidate name or resume file",
            )
        if decision_filter != "All":
            display = display[display["decision"] == decision_filter]
        if candidate_search.strip():
            query = candidate_search.strip().lower()
            display = display[
                display["candidate"].str.lower().str.contains(query, regex=False)
                | display["resume_file"].str.lower().str.contains(query, regex=False)
            ]
        table_selection = st.dataframe(
            display,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="ranking_table",
            column_config={
                "match_score": st.column_config.ProgressColumn(
                    "Match score",
                    min_value=0,
                    max_value=100,
                    format="%.2f",
                ),
                "experience_years": st.column_config.NumberColumn("Experience", format="%.1f yrs"),
                "experience_gap": st.column_config.NumberColumn("Experience gap", format="%.1f yrs"),
                "decision": st.column_config.TextColumn("Decision"),
            },
        )

        selected_rows = table_selection.selection.rows
        if selected_rows:
            candidate = display.iloc[selected_rows[0]]
            with st.expander("Candidate evidence", icon=":material/person_search:", expanded=True):
                left, right = st.columns(2)
                left.write(f"**Matched skills:** {candidate['matched_skills'] or 'None identified'}")
                right.write(f"**Missing must-have:** {candidate['missing_must_have'] or 'None'}")

        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export CSV report",
            csv,
            file_name="ranking_report.csv",
            mime="text/csv",
            icon=":material/download:",
        )
        json_report = results.to_json(orient="records", indent=2).encode("utf-8")
        st.download_button(
            "Export JSON report",
            json_report,
            file_name="ranking_report.json",
            mime="application/json",
            icon=":material/code:",
        )

    with analytics_tab:
        chart_data = results.sort_values("match_score", ascending=True)
        st.bar_chart(
            chart_data,
            x="candidate",
            y="match_score",
            horizontal=True,
            x_label="Candidate",
            y_label="Match score",
        )
        component_chart = results.set_index("candidate")[
            ["similarity_score", "skill_coverage", "experience_score"]
        ]
        st.bar_chart(
            component_chart,
            horizontal=True,
            stack=False,
        )
        st.caption("The first chart shows final ranks; the second separates score components.")

    with history_tab:
        history = list_runs()
        if history.empty:
            st.caption("No completed screening runs yet.")
        else:
            selected_run = st.selectbox(
                "Saved screening run",
                history["id"].tolist(),
                format_func=lambda run_id: (
                    f"Run #{run_id} • "
                    f"{history.loc[history['id'] == run_id, 'candidate_count'].iloc[0]} candidates"
                ),
            )
            selected_history = get_run(int(selected_run))
            st.dataframe(
                selected_history,
                hide_index=True,
                column_config={
                    "match_score": st.column_config.ProgressColumn(
                        "Match score",
                        min_value=0,
                        max_value=100,
                        format="%.2f",
                    ),
                },
            )

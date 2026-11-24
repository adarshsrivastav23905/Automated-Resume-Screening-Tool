import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
from backend.app.audit_store import get_run, list_runs, save_run
from backend.app.screening import score_resumes


st.set_page_config(
    page_title="HireLens | Screening Intelligence",
    page_icon=":material/analytics:",
    layout="wide",
)

if "ranking_results" not in st.session_state:
    st.session_state.ranking_results = None

with st.sidebar:
    st.markdown(":material/track_changes: **HireLens**")
    st.caption("Recruitment intelligence")
    st.subheader("Screening settings")
    st.write("Configure how candidates are evaluated.")
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
    st.badge("TF-IDF hybrid · v2.2", icon=":material/verified:", color="blue")

st.badge("HIRELENS · TALENT INTELLIGENCE", icon=":material/auto_awesome:", color="green")
st.title("Talent decisions, backed by evidence.")
st.write(
    "A clear, human-led workspace for comparing role requirements with candidate experience."
)
st.info(
    "Scores support recruiter judgment. Candidates missing must-have skills are flagged for review.",
    icon=":material/verified_user:",
)

workflow_cols = st.columns(3)
workflow_steps = [
    ("green", ":material/edit_document:", "01 · ROLE PROFILE", "Define the role", "Add the role brief and key skills."),
    ("blue", ":material/description:", "02 · CANDIDATE POOL", "Review candidates", "Bring resumes together in one workspace."),
    ("orange", ":material/insights:", "03 · EVIDENCE REVIEW", "Compare evidence", "Explore fit, skill matches, and gaps."),
]
for column, (accent, icon, step, title, description) in zip(workflow_cols, workflow_steps):
    with column.container(border=True):
        st.badge(step, color=accent)
        st.markdown(f":{accent}[{icon}] **{title}**")
        st.write(description)

default_job = ""
job_path = project_root / "data" / "job_description.txt"
if job_path.exists():
    default_job = job_path.read_text(encoding="utf-8")

with st.form("screening_form"):
    input_col, upload_col = st.columns([1.55, 1], gap="large")
    with input_col:
        with st.container(border=True):
            st.subheader("Job requirements", divider="green")
            st.write("Use the role description to provide context for candidate matching.")
            job_description = st.text_area(
                "Job description",
                value=default_job,
                height=260,
                placeholder="Paste the role description and required skills here...",
            )
    with upload_col:
        with st.container(border=True):
            st.subheader("Candidate resumes", divider="blue")
            st.write("Add one or more files to compare against the role.")
            uploaded_files = st.file_uploader(
                "Upload resumes",
                type=["txt", "pdf", "docx"],
                accept_multiple_files=True,
                help="TXT, PDF, and DOCX files are supported",
            )
            if uploaded_files:
                st.badge(
                    f"{len(uploaded_files)} resume(s) ready",
                    icon=":material/check_circle:",
                    color="green",
                )
            else:
                st.write("No resumes selected yet.")

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
    col1.metric(
        ":blue[:material/groups: Candidates analyzed]",
        total,
        border=True,
        help="Total resumes in this screening run.",
    )
    col2.metric(":green[:material/check_circle: Shortlisted]", shortlisted, border=True)
    col3.metric(":orange[:material/visibility: Needs review]", review, border=True)
    col4.metric(":red[:material/block: Rejected]", rejected, border=True)

    ranking_tab, analytics_tab, history_tab = st.tabs([
        ":material/table_chart: Ranking report",
        ":material/analytics: Score analytics",
        ":material/history: Run history",
    ])

    with ranking_tab:
        st.subheader("Candidate results")
        st.write("Select a candidate row to inspect matched and missing requirements.")
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
        st.subheader("Score analytics")
        st.write("Compare overall fit and the components behind each candidate score.")
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
        st.write("The first chart shows final ranks; the second separates score components.")

    with history_tab:
        st.subheader("Previous screening runs")
        st.write("Review saved results from earlier analyses.")
        history = list_runs()
        if history.empty:
            st.write("No completed screening runs yet.")
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

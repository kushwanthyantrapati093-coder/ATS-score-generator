import streamlit as st
import pandas as pd
from database import engine, cv_table
from extract_text import extract_pdf, extract_docx, extract_txt
from skills import extract_skills, calculate_score
from sqlalchemy import insert

# ---- Page Configuration ----
st.set_page_config(
    page_title="ATS Score Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Header (Black/Charcoal & White) ----
st.markdown(
    """
    <div style="background-color:#2F2F2F; padding:25px; border-radius:10px; text-align:center;">
        <h1 style="color:white; font-family:Arial, Helvetica, sans-serif; font-weight:bold;">
            Applicant Tracking System Score Generator
        </h1>
        <p style="color:#FFFFFF; font-size:18px; font-family:Arial, Helvetica, sans-serif;">
            Upload CVs and Job Descriptions to analyze skills and generate match scores professionally
        </p>
    </div>
    """, unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ---- Tabs ----
tab1, tab2 = st.tabs(["📝 Analyze CV vs JD", "📊 View All Scores"])

# ------------------ TAB 1: Analyze ------------------ #
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        cv_file = st.file_uploader("📄 Upload CV", type=['pdf', 'docx'])

    with col2:
        jd_file = st.file_uploader("📝 Upload JD File (Optional)", type=['pdf', 'docx', 'txt'])
        st.markdown("**OR Type JD Text Below:**")
        jd_text_input = st.text_area("Enter Job Description Here", height=200)

    # Initialize session state
    if "cv_text" not in st.session_state: st.session_state.cv_text = ""
    if "jd_text" not in st.session_state: st.session_state.jd_text = ""
    if "cv_skills" not in st.session_state: st.session_state.cv_skills = []
    if "jd_skills" not in st.session_state: st.session_state.jd_skills = []
    if "score" not in st.session_state: st.session_state.score = None

    if cv_file and (jd_file or jd_text_input):
        if st.button("✅ Finalize Analysis"):
            # Extract CV
            if cv_file.type == "application/pdf":
                st.session_state.cv_text = extract_pdf(cv_file)
            else:
                st.session_state.cv_text = extract_docx(cv_file)

            # Use JD file if uploaded, else typed text
            if jd_file:
                if jd_file.type == "application/pdf":
                    st.session_state.jd_text = extract_pdf(jd_file)
                elif jd_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    st.session_state.jd_text = extract_docx(jd_file)
                else:
                    st.session_state.jd_text = extract_txt(jd_file)
            else:
                st.session_state.jd_text = jd_text_input

            # Extract skills
            st.session_state.cv_skills = extract_skills(st.session_state.cv_text)
            st.session_state.jd_skills = extract_skills(st.session_state.jd_text)

            # Calculate score
            st.session_state.score = calculate_score(st.session_state.cv_skills, st.session_state.jd_skills)

    # Display results
    if st.session_state.score is not None:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#2F2F2F; text-align:center;'>Analysis Result</h2>", unsafe_allow_html=True)

        result_col1, result_col2, result_col3 = st.columns([1,1,1])

        # CV Skills Card
        with result_col1:
            st.markdown(f"""
            <div style="background-color:#000000; padding:20px; border-radius:10px; color:white; text-align:center; height:200px;">
                <h3>CV Skills</h3>
                <p>{', '.join(st.session_state.cv_skills)}</p>
            </div>
            """, unsafe_allow_html=True)

        # JD Skills Card
        with result_col2:
            st.markdown(f"""
            <div style="background-color:#333333; padding:20px; border-radius:10px; color:white; text-align:center; height:200px;">
                <h3>JD Skills</h3>
                <p>{', '.join(st.session_state.jd_skills)}</p>
            </div>
            """, unsafe_allow_html=True)

        # Match Score Card
        with result_col3:
            st.markdown(f"""
            <div style="background-color:#555555; padding:30px; border-radius:10px; color:white; text-align:center; height:200px;">
                <h2>Match Score</h2>
                <h1>{st.session_state.score}%</h1>
            </div>
            """, unsafe_allow_html=True)

        # Save Section
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#2F2F2F;'>Save Analysis to Database</h3>", unsafe_allow_html=True)
        candidate_name = st.text_input("Enter Candidate Name")
        if st.button("💾 Save to Database") and candidate_name:
            try:
                with engine.begin() as conn:  # ensures commit
                    stmt = insert(cv_table).values(
                        candidate_name=candidate_name,
                        cv_text=st.session_state.cv_text,
                        jd_text=st.session_state.jd_text,
                        score=st.session_state.score
                    )
                    conn.execute(stmt)
                st.success("✅ Data saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving data: {e}")

# ------------------ TAB 2: Dashboard ------------------ #
with tab2:
    st.markdown("<h2 style='color:#2F2F2F;'>All Saved CV vs JD Scores</h2>", unsafe_allow_html=True)

    # Fetch all records
    with engine.connect() as conn:
        result = conn.execute(cv_table.select()).fetchall()

    if result:
        df = pd.DataFrame(result, columns=['ID','Candidate Name','CV Text','JD Text','Score'])

        # Sidebar: Show all saved candidates
        st.sidebar.markdown("## 📋 Saved Candidates List")
        candidate_list = df[['Candidate Name', 'Score']].values.tolist()
        for name, score in candidate_list:
            st.sidebar.markdown(f"**{name}** → Score: {score}%")

        # Select candidate filter
        selected_candidate = st.sidebar.selectbox(
            "Select Candidate to Filter Table",
            ["All"] + df['Candidate Name'].tolist()
        )

        # Filter table if a candidate is selected
        if selected_candidate != "All":
            df = df[df['Candidate Name'] == selected_candidate]

        # Highlight scores
        def highlight_score(val):
            if val >= 80: return 'background-color: #32CD32; color: white'
            elif val >= 50: return 'background-color: #FFD700; color: black'
            else: return 'background-color: #FF6347; color: white'

        st.dataframe(df.style.applymap(highlight_score, subset=['Score']), use_container_width=True)

    else:
        st.info("No records found. Add some analysis first.")

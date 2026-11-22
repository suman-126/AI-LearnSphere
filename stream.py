import streamlit as st
import time
from datetime import date,datetime, timezone
from zoneinfo import ZoneInfo
from modules.ai_tutor.tutor import ask_tutor
from modules.quiz_generator.quiz import (
    generate_quiz,
    evaluate_quiz,
    generate_quiz_result
)
from modules.knowledge_evaluator.evaluator import (
    generate_assessment,
    evaluate_knowledge
)
from modules.document_intelligence.document_manager import (
    upload_document,
    remove_document
)
from modules.document_intelligence.document_qa import (
    answer_document_question
)
from modules.practice_arena.practice import (
    create_practice_session,
    evaluate_practice_session
)
from modules.practice_arena.coding_challenges import (
    get_coding_challenges,
    get_coding_challenge_by_id
)

from modules.practice_arena.code_evaluator import (
    evaluate_code_submission
)
from services.storage_manager import (
    save_quiz_result,
    save_learning_history,
    get_quiz_results,
    get_learning_history,
    save_topic_progress,
    get_topic_progress,
    get_registered_documents
)
from services.learning_goals.goals import (
    create_goal,
    update_goal,
    delete_goal
)

from services.learning_goals.progress import (
    get_all_goal_progress
)
from services.learning_insights.insights_analyzer import (
    get_performance_analysis
)

from services.learning_insights.trend_analyzer import (
    analyze_learning_trends
)

from services.learning_insights.recommendation_engine import (
    generate_recommendations
)

from services.learning_insights.ai_report import (
    generate_ai_learning_report,
    classify_performance
)
from services.preferences_manager import (
    load_preferences,
    save_preferences,
    reset_preferences
)
from services.llm_service import (
    check_ollama_connection,
    get_available_models
)

def format_ist_time(timestamp):
    """Convert a database UTC timestamp into Indian Standard Time."""

    if not timestamp:
        return "Time unavailable"

    try:
        utc_time = datetime.strptime(
            timestamp,
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        ist_time = utc_time.astimezone(
            ZoneInfo("Asia/Kolkata")
        )

        return ist_time.strftime("%d-%m-%Y %I:%M:%S %p")

    except (ValueError, TypeError):
        return timestamp
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI LearnSphere",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# USER PREFERENCES
# --------------------------------------------------

if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = load_preferences()

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

current_theme = st.session_state.user_preferences.get(
    "theme", "Light"
)

if current_theme == "Dark":

    main_bg = "#202B3C"
    hero_bg = "linear-gradient(120deg, #263B60, #44385F)"
    hero_heading = "#FFFFFF"
    hero_text = "#CBD5E1"

    card_bg = "#2B394D"
    card_border = "#46566D"
    card_heading = "#FFFFFF"
    card_text = "#CBD5E1"

    text_color = "#E2E8F0"
    label_color = "#F1F5F9"
    input_bg = "#2B394D"
    input_border = "#64748B"
    placeholder_color = "#AAB8CA"
    sidebar_bg = "#253247"

else:

    main_bg = "#F7F8FC"
    hero_bg = "linear-gradient(120deg, #E8EAFE, #F2EAFE)"
    hero_heading = "#303B75"
    hero_text = "#555B78"

    card_bg = "#FFFFFF"
    card_border = "#E8EAF2"
    card_heading = "#303B75"
    card_text = "#62677A"

    text_color = "#303B75"
    label_color = "#303B75"
    input_bg = "#FFFFFF"
    input_border = "#CBD5E1"
    placeholder_color = "#858B9C"
    sidebar_bg = "#FFFFFF"


# --------------------------------------------------
# APPLY GLOBAL STYLING
# --------------------------------------------------

st.markdown(
    f"""
    <style>

        /* --------------------------------
           APPLICATION BACKGROUND AND TEXT
        -------------------------------- */

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {{
            background-color: {main_bg} !important;
            color: {text_color} !important;
        }}

        .main {{
            background-color: {main_bg} !important;
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}

        /* --------------------------------
           GENERAL MARKDOWN TEXT
        -------------------------------- */

        .main [data-testid="stMarkdownContainer"] p,
        .main [data-testid="stMarkdownContainer"] li,
        .main [data-testid="stMarkdownContainer"] strong,
        .main [data-testid="stMarkdownContainer"] em,
        .main [data-testid="stMarkdownContainer"] blockquote {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}

        .main h1,
        .main h2,
        .main h3,
        .main h4,
        .main h5,
        .main h6 {{
            color: {card_heading} !important;
            -webkit-text-fill-color: {card_heading} !important;
        }}

        /* --------------------------------
           ALL STREAMLIT WIDGET LABELS
        -------------------------------- */

        .main [data-testid="stWidgetLabel"],
        .main [data-testid="stWidgetLabel"] *,
        .main [data-testid="stWidgetLabel"] p,
        .main label,
        .main label * {{
            color: {label_color} !important;
            -webkit-text-fill-color: {label_color} !important;
            opacity: 1 !important;
        }}

        /* Radio and checkbox labels */

        .main [data-testid="stRadio"] label,
        .main [data-testid="stRadio"] label *,
        .main [data-testid="stCheckbox"] label,
        .main [data-testid="stCheckbox"] label * {{
            color: {label_color} !important;
            -webkit-text-fill-color: {label_color} !important;
            opacity: 1 !important;
        }}

        /* --------------------------------
           INPUT FIELDS AND TEXT AREAS
        -------------------------------- */

        div[data-baseweb="input"],
        div[data-baseweb="textarea"],
        div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            border-color: {input_border} !important;
        }}

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        [data-testid="stTextArea"] textarea {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            caret-color: {text_color} !important;
            background-color: transparent !important;
        }}

        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="textarea"] textarea::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {{
            color: {placeholder_color} !important;
            -webkit-text-fill-color: {placeholder_color} !important;
            opacity: 1 !important;
        }}

        [data-testid="stTextArea"] [data-baseweb="textarea"] {{
            background-color: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 8px !important;
        }}

        /* --------------------------------
           SELECT BOX TEXT AND OPTIONS
        -------------------------------- */

        [data-testid="stSelectbox"] [data-baseweb="select"] *,
        [data-baseweb="popover"] *,
        [role="listbox"] * {{
            color: {text_color} !important;
        }}

        [data-baseweb="popover"],
        [role="listbox"] {{
            background-color: {card_bg} !important;
        }}

        /* --------------------------------
           RADIO OPTIONS AND CODE TEXT
        -------------------------------- */

        [data-testid="stRadio"] label,
        [data-testid="stRadio"] label *,
        [data-testid="stRadio"] [data-testid="stMarkdownContainer"],
        [data-testid="stRadio"] [data-testid="stMarkdownContainer"] * {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            opacity: 1 !important;
        }}

        .stMarkdown code,
        .stRadio code,
        [data-testid="stRadio"] code {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            border: 1px solid {card_border} !important;
            border-radius: 5px;
            padding: 2px 5px;
        }}

        /* --------------------------------
           BUTTONS
        -------------------------------- */

        [data-testid="stButton"] button,
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stDownloadButton"] button {{
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border: 1px solid #60A5FA !important;
        }}

        [data-testid="stButton"] button *,
        [data-testid="stFormSubmitButton"] button *,
        [data-testid="stDownloadButton"] button * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        [data-testid="stButton"] button:hover,
        [data-testid="stFormSubmitButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover {{
            background-color: #1D4ED8 !important;
        }}
        
        /* --------------------------------
          FILE UPLOADER
        -------------------------------- */

        [data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploader"] section {{
           background-color: {card_bg} !important;
           border: 1px dashed {input_border} !important;
        }}

        /* Selected uploaded file background */

        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {{
           background-color: {card_bg} !important;
           border: 1px solid {input_border} !important;
           opacity: 1 !important;
        }}

        /* Selected uploaded filename */

        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *,
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] p,
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span {{
           color: {text_color} !important;
           -webkit-text-fill-color: {text_color} !important;
           opacity: 1 !important;
        }}

        [data-testid="stFileUploader"] button {{
           background-color: #2563EB !important;
           color: #FFFFFF !important;
        }}

        /* FILE UPLOADER - HELP TEXT AND SIZE LIMIT VISIBILITY */

        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] label {{
           color: {text_color} !important;
           -webkit-text-fill-color: {text_color} !important;
           opacity: 1 !important;
        }}

        /* --------------------------------
           AI TUTOR CHAT MESSAGES
        -------------------------------- */

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] strong,
        [data-testid="stChatMessage"] em {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}

        /* AI TUTOR CHAT HEADINGS AND BOLD TEXT */

        [data-testid="stChatMessage"] h1,
        [data-testid="stChatMessage"] h2,
        [data-testid="stChatMessage"] h3,
        [data-testid="stChatMessage"] h4,
        [data-testid="stChatMessage"] h5,
        [data-testid="stChatMessage"] h6,
        [data-testid="stChatMessage"] strong,
        [data-testid="stChatMessage"] b {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            opacity: 1 !important;
        }}

        /* --------------------------------
           AI TUTOR CHAT INPUT AND SEND ARROW
        -------------------------------- */

        [data-testid="stChatInput"] {{
            background-color: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 12px !important;
        }}

        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] [data-baseweb="textarea"] {{
            background-color: {input_bg} !important;
        }}

        [data-testid="stChatInput"] textarea {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            caret-color: {text_color} !important;
        }}

        [data-testid="stChatInput"] textarea::placeholder {{
            color: {placeholder_color} !important;
            -webkit-text-fill-color: {placeholder_color} !important;
            opacity: 1 !important;
        }}

        [data-testid="stChatInput"] button {{
            color: {text_color} !important;
        }}

        [data-testid="stChatInput"] button svg {{
            color: {text_color} !important;
            fill: currentColor !important;
            stroke: currentColor !important;
        }}

        /* --------------------------------
           SPINNERS AND PROCESSING MESSAGES
        -------------------------------- */

        [data-testid="stSpinner"] *,
        [data-testid="stStatusWidget"] * {{
            color: {text_color} !important;
        }}

        /* --------------------------------
           METRICS
        -------------------------------- */

        [data-testid="stMetric"] label,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] *,
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] *,
        [data-testid="stMetricDelta"],
        [data-testid="stMetricDelta"] * {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            opacity: 1 !important;
        }}

        /* --------------------------------
           ALERTS
        -------------------------------- */

        [data-testid="stAlert"],
        [data-testid="stAlert"] > div,
        [data-testid="stAlertContent"] {{
            background-color: {card_bg} !important;
            border-color: {card_border} !important;
            border-radius: 10px !important;
        }}

        [data-testid="stAlert"] p,
        [data-testid="stAlert"] span,
        [data-testid="stAlert"] strong,
        [data-testid="stAlert"] li {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}

        /* --------------------------------
           BORDERED CONTAINERS
        -------------------------------- */

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 12px !important;
        }}

        /* --------------------------------
           CAPTIONS
        -------------------------------- */

        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] * {{
            color: {card_text} !important;
            -webkit-text-fill-color: {card_text} !important;
            opacity: 1 !important;
        }}

        /* --------------------------------
           SIDEBAR
        -------------------------------- */

        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
        }}

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] label *,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            opacity: 1 !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: {card_border} !important;
        }}

        /* Sidebar collapse and expand controls */

        [data-testid="stSidebar"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stHeader"] button {{
            color: {text_color} !important;
        }}

        [data-testid="stSidebar"] button svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stHeader"] button svg {{
            color: {text_color} !important;
            fill: currentColor !important;
            stroke: currentColor !important;
            opacity: 1 !important;
        }}

        /* --------------------------------
           STREAMLIT TOOLBAR
        -------------------------------- */

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stToolbar"] * {{
            color: {text_color} !important;
        }}

        [data-testid="stToolbar"] button svg {{
            color: {text_color} !important;
            fill: currentColor !important;
            stroke: currentColor !important;
        }}

        /* --------------------------------
           DASHBOARD HERO
        -------------------------------- */

        .hero {{
            padding: 28px;
            border-radius: 18px;
            background: {hero_bg};
            margin-bottom: 24px;
        }}

        .hero h1 {{
            color: {hero_heading} !important;
            -webkit-text-fill-color: {hero_heading} !important;
            margin-bottom: 8px;
        }}

        .hero p {{
            color: {hero_text} !important;
            -webkit-text-fill-color: {hero_text} !important;
            font-size: 16px;
        }}

        /* --------------------------------
           DASHBOARD MODULE CARDS
        -------------------------------- */

        .module-card {{
            background-color: {card_bg};
            padding: 22px;
            border-radius: 15px;
            border: 1px solid {card_border};
            min-height: 175px;
            margin-bottom: 15px;
        }}

        .module-card h3 {{
            color: {card_heading} !important;
            -webkit-text-fill-color: {card_heading} !important;
        }}

        .module-card p {{
            color: {card_text} !important;
            -webkit-text-fill-color: {card_text} !important;
            font-size: 14px;
        }}


        /* ==========================================
           FINAL WIDGET VISIBILITY FIX
        ========================================== */

        /* Widget labels */

        .stApp [data-testid="stWidgetLabel"],
        .stApp [data-testid="stWidgetLabel"] *,
        .stApp [data-testid="stSlider"] label,
        .stApp [data-testid="stRadio"] label,
        .stApp [data-testid="stCheckbox"] label,
        .stApp [data-testid="stFileUploader"] label {{
            color: {label_color} !important;
            -webkit-text-fill-color: {label_color} !important;
            opacity: 1 !important;
        }}

        /* Text inputs and text areas */

        .stApp [data-testid="stTextInput"] input,
        .stApp [data-testid="stNumberInput"] input,
        .stApp [data-testid="stDateInput"] input,
        .stApp [data-testid="stTimeInput"] input,
        .stApp [data-testid="stTextArea"] textarea,
        .stApp [data-testid="stChatInput"] textarea {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            caret-color: {text_color} !important;
            opacity: 1 !important;
        }}

        /* Input containers */

        .stApp [data-baseweb="input"],
        .stApp [data-baseweb="textarea"] {{
            background-color: {input_bg} !important;
            border-color: {input_border} !important;
        }}

        /* Placeholder text */

        .stApp input::placeholder,
        .stApp textarea::placeholder {{
            color: {placeholder_color} !important;
            -webkit-text-fill-color: {placeholder_color} !important;
            opacity: 1 !important;
        }}

        /* Select boxes */

        .stApp [data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            border-color: {input_border} !important;
        }}

        .stApp [data-baseweb="select"] *,
        .stApp [data-baseweb="popover"] *,
        .stApp [role="option"] {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}

        /* Sidebar controls */

        .stApp [data-testid="stSidebarCollapseButton"],
        .stApp [data-testid="stSidebarCollapsedControl"],
        .stApp [data-testid="stHeader"] button {{
            color: {text_color} !important;
        }}

        .stApp [data-testid="stSidebarCollapseButton"] svg,
        .stApp [data-testid="stSidebarCollapsedControl"] svg,
        .stApp [data-testid="stHeader"] button svg {{
            color: {text_color} !important;
            fill: currentColor !important;
            stroke: currentColor !important;
            opacity: 1 !important;
        }}

        /* ==========================================
           SIDEBAR COLLAPSE / EXPAND CONTROLS
        ========================================== */

        .stApp [data-testid="stSidebarCollapseButton"],
        .stApp [data-testid="stSidebarCollapsedControl"],
        .stApp [data-testid="stHeader"] button {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            border-color: {card_border} !important;
            opacity: 1 !important;
        }}

        .stApp [data-testid="stSidebarCollapseButton"] svg,
        .stApp [data-testid="stSidebarCollapsedControl"] svg,
        .stApp [data-testid="stHeader"] button svg {{
            color: {text_color} !important;
            fill: {text_color} !important;
            stroke: {text_color} !important;
            opacity: 1 !important;
        }}

        /* ==========================================
           STREAMLIT TOP TOOLBAR
        ========================================== */

        .stApp [data-testid="stHeader"] {{
            background-color: {main_bg} !important;
        }}

        .stApp [data-testid="stToolbar"] {{
            background-color: {main_bg} !important;
            color: {text_color} !important;
            opacity: 1 !important;
        }}

        .stApp [data-testid="stToolbar"] button {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            border-color: {card_border} !important;
            opacity: 1 !important;
        }}

        .stApp [data-testid="stToolbar"] button svg,
        .stApp [data-testid="stToolbar"] svg {{
            color: {text_color} !important;
            fill: {text_color} !important;
            stroke: {text_color} !important;
            opacity: 1 !important;
        }}

    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("🎓 AI LearnSphere")
st.sidebar.caption("Intelligent Learning Platform")

pages = [
    "Dashboard",
    "AI Tutor",
    "Smart Quiz",
    "Knowledge Evaluator",
    "Document Intelligence",
    "Practice Arena",
    "Learning Roadmap",
    "My Learning Journey",
    "AI Learning Insights",
    "Learning History",
    "Settings"
]

selected_page = st.sidebar.radio(
    "Navigation",
    pages
)

st.sidebar.divider()
st.sidebar.caption("Learn • Practice • Improve")

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if selected_page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>Welcome to AI LearnSphere! 🎓</h1>
        <p>
            Your intelligent learning companion for academic subjects,
            technical skills, practice and personal growth.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Your Learning Space")

    # Retrieve saved learning progress
    topic_records = get_topic_progress()

    overall_progress = (
        sum(
            item["progress_percentage"]
            for item in topic_records
        ) / len(topic_records)
        if topic_records else 0
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Learning Modules", "6")

    with col2:
        current_level = st.session_state.user_preferences.get(
            "learning_level", "Not Set"
        )
        st.metric("Learning Level", current_level)

    with col3:
        st.metric(
            "Learning Progress",
            f"{overall_progress:.1f}%"
        )


    st.divider()

    st.subheader("Explore Your Learning Modules")

    modules = [
        (
            "🤖 AI Tutor",
            "Learn any subject with simple explanations, examples and interactive questions."
        ),
        (
            "📝 Smart Quiz Generator",
            "Create topic-based quizzes and evaluate your knowledge."
        ),
        (
            "📊 Knowledge Evaluator",
            "Understand your strengths, weaknesses and learning gaps."
        ),
        (
            "🗺️ Personalised Learning Roadmap",
            "Build a learning path based on your goals and performance."
        ),
        (
            "📚 Document Intelligence",
            "Upload study materials and learn directly from your documents."
        ),
        (
            "🎯 Practice Arena",
            "Improve your knowledge through topic-based practice and challenges."
        )
    ]

    for start in range(0, len(modules), 3):
        columns = st.columns(3)

        for column, module in zip(
            columns,
            modules[start:start + 3]
        ):
            with column:
                st.markdown(
                    f"""
                    <div class="module-card">
                        <h3>{module[0]}</h3>
                        <p>{module[1]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# --------------------------------------------------
# AI TUTOR
# --------------------------------------------------

elif selected_page == "AI Tutor":
    st.title("🤖 AI Tutor")
    st.write(
        "Learn any subject through interactive explanations "
        "and follow-up conversations."
    )

    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = []

    col1, col2 = st.columns(2)

    with col1:
        subject = st.text_input(
            "Subject (Optional)",
            placeholder="e.g. Python, Mathematics, Physics"
        )

        learning_level = st.selectbox(
            "Learning Level",
            ["Beginner", "Intermediate", "Advanced", "Auto-detect"],
            index=["Beginner", "Intermediate", "Advanced", "Auto-detect"].index(
                st.session_state.user_preferences["learning_level"]
            )
        )

    with col2:
        explanation_style = st.selectbox(
            "Explanation Style",
            ["Simple", "Detailed", "Both"],
            index=["Simple", "Detailed", "Both"].index(
                st.session_state.user_preferences["explanation_style"]
            )
        )

        st.markdown("**Response Language:** English")

    st.divider()

    if st.button("Clear Conversation"):
        st.session_state.tutor_messages = []
        st.rerun()

    for message in st.session_state.tutor_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask your learning question...")

    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("AI Tutor is preparing your explanation..."):
                try:
                    history = st.session_state.tutor_messages.copy()

                    response = ask_tutor(
                        question=question,
                        subject=subject.strip() or None,
                        learning_level=learning_level,
                        explanation_style=explanation_style,
                        language="English",
                        model=st.session_state.user_preferences["model"],
                        conversation_history=history if history else None
                    )

                    st.markdown(response)

                    st.session_state.tutor_messages.append({
                        "role": "user",
                        "content": question
                    })

                    st.session_state.tutor_messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as error:
                    st.error(f"Unable to generate response: {error}")

# --------------------------------------------------
# SMART QUIZ
# --------------------------------------------------

elif selected_page == "Smart Quiz":
    if "quiz_question_history" not in st.session_state:
        st.session_state.quiz_question_history = {}

    st.title("📝 Smart Quiz Generator")
    st.write(
        "Test your knowledge with topic-based multiple-choice quizzes."
    )

    st.divider()

    # Quiz configuration
    col1, col2 = st.columns(2)

    with col1:
        subject = st.text_input(
            "Subject",
            value="Computer Science",
            key="quiz_subject"
        )

        topic = st.text_input(
            "Quiz Topic",
            placeholder="e.g. Python Variables",
            key="quiz_topic"
        )

    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            key="quiz_difficulty"
        )

        num_questions = st.selectbox(
            "Number of Questions",
            [5, 10, 15, 20],
            key="quiz_question_count"
        )

    history_key = (
        (subject.strip() or "General").casefold(),
        topic.strip().casefold(),
        difficulty
    )

    # Generate quiz
    if st.button("Generate Quiz", type="primary"):

        if not topic.strip():
            st.warning("Please enter a quiz topic.")

        else:
            with st.spinner("Generating your quiz..."):

                try:
                    used_questions = st.session_state.quiz_question_history.get(
                        history_key, []
                    )

                    quiz = generate_quiz(
                        subject=subject.strip() or None,
                        topic=topic.strip(),
                        difficulty=difficulty,
                        num_questions=num_questions,
                        previous_questions=used_questions
                    )

                    st.session_state.quiz_question_history[history_key] = (
                       used_questions
                       + [item["question"] for item in quiz["questions"]]
                    ) 

                    st.session_state.active_quiz = quiz
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_evaluation = None
                    st.session_state.quiz_result = None

                except Exception as error:
                    st.error(f"Unable to generate quiz: {error}")

    # Display generated quiz
    if st.session_state.get("active_quiz"):

        quiz = st.session_state.active_quiz

        st.divider()
        st.subheader("Your Quiz")

        with st.form("quiz_submission_form"):

            for index, question in enumerate(quiz["questions"]):

                st.markdown(
                    f"**Question {index + 1}. {question['question']}**"
                )

                options = question["options"]

                selected_option = st.radio(
                    "Choose your answer:",
                    options=list(options.keys()),
                    format_func=lambda key, opts=options: (
                        f"{key}. {opts[key]}"
                    ),
                    key=f"quiz_answer_{index}",
                    index=None
                )

                st.session_state.quiz_answers[index] = selected_option

                st.write("")

            submitted = st.form_submit_button(
                "Submit Quiz",
                type="primary"
            )

        if submitted:

            try:
                evaluation = evaluate_quiz(
                    quiz,
                    st.session_state.quiz_answers
                )

                result = generate_quiz_result(evaluation)

                st.session_state.quiz_evaluation = evaluation
                st.session_state.quiz_result = result

                # Save quiz result in the database
                summary = result["summary"]

                saved = save_quiz_result(
                    subject=quiz.get("subject") or subject.strip() or "General",
                    topic=quiz.get("topic") or topic.strip(),
                    difficulty=quiz.get("difficulty") or difficulty,
                    total_questions=len(quiz["questions"]),
                    correct_answers=summary["correct_answers"]
                )

                if saved:
                    st.success("Quiz result saved to Learning History.")
                else:
                    st.info(
                        "Quiz evaluated, but Learning History saving "
                        "is disabled or unavailable."
                    )

            except Exception as error:
                st.error(f"Unable to evaluate or save quiz: {error}")
    # Display quiz results
    if st.session_state.get("quiz_result"):

        result = st.session_state.quiz_result
        summary = result["summary"]

        st.divider()
        st.subheader("Quiz Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Correct Answers",
                summary["correct_answers"]
            )

        with col2:
            st.metric(
                "Incorrect Answers",
                summary["incorrect_answers"]
            )

        with col3:
            st.metric(
                "Score",
                f"{summary['percentage']}%"
            )

        st.subheader(result["performance"])
        st.write(result["message"])

        st.progress(summary["percentage"] / 100)

        st.divider()
        st.subheader("Answer Review")

        for index, item in enumerate(result["detailed_results"]):

            st.markdown(
                f"**Question {index + 1}: {item['question']}**"
            )

            if item["is_correct"]:
                st.success("Correct answer!")
            else:
                st.error(
                    f"Your answer: {item['user_answer'] or 'Not answered'}"
                )

            st.write(
                f"Correct answer: {item['correct_answer']}"
            )

            st.info(item["explanation"])


        if st.button("Generate Another Quiz"):

            try:
                with st.spinner("Generating a new quiz..."):

                    used_questions = (
                        st.session_state.quiz_question_history.get(
                            history_key, []
                        )
                    )

                    new_quiz = generate_quiz(
                        subject=subject.strip() or None,
                        topic=topic.strip(),
                        difficulty=difficulty,
                        num_questions=num_questions,
                        previous_questions=used_questions
                    )

                    st.session_state.quiz_question_history[history_key] = (
                        used_questions
                        + [
                            item["question"]
                            for item in new_quiz["questions"]
                        ]
                    )

                    st.session_state.active_quiz = new_quiz
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_evaluation = None
                    st.session_state.quiz_result = None

                st.rerun()

            except Exception as error:
                st.error(f"Unable to generate a new quiz: {error}")

# --------------------------------------------------
# KNOWLEDGE EVALUATOR
# --------------------------------------------------

elif selected_page == "Knowledge Evaluator":

    st.title("Knowledge Evaluator")

    st.write(
        "Test your conceptual understanding through written answers "
        "and receive AI-powered feedback."
    )

    st.divider()

    st.subheader("Generate Assessment")

    subject = st.text_input(
        "Subject",
        value="Computer Science"
    )

    topic = st.text_input(
        "Topic",
        placeholder="e.g. Python Variables"
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    if st.button("Generate Assessment",width="stretch"):

        if not subject.strip() or not topic.strip():

            st.warning("Please enter both subject and topic.")

        else:

            try:
                with st.spinner("Generating your assessment..."):

                    assessment = generate_assessment(
                        subject=subject,
                        topic=topic,
                        difficulty=difficulty
                    )

                    st.session_state.knowledge_assessment = assessment
                    st.session_state.knowledge_evaluation = None
                    st.session_state.knowledge_answer = ""

            except Exception as e:

                st.error(f"Assessment generation failed: {e}")

    # Display generated assessment

    assessment = st.session_state.get("knowledge_assessment")

    if assessment:

        st.divider()

        st.subheader("Your Assessment")

        st.write(f"**Subject:** {assessment['subject']}")
        st.write(f"**Topic:** {assessment['topic']}")
        st.write(f"**Difficulty:** {assessment['difficulty']}")

        st.info(assessment["question"])

        learner_answer = st.text_area(
            "Write your answer below:",
            height=180,
            key="knowledge_answer"
        )

        if st.button("Evaluate My Answer",width="stretch"):

            if not learner_answer.strip():

                st.warning("Please write an answer first.")

            else:

                try:
                    with st.spinner("Evaluating your knowledge..."):

                        evaluation = evaluate_knowledge(
                            assessment=assessment,
                            learner_answer=learner_answer
                        )

                        st.session_state.knowledge_evaluation = evaluation

                        # Save Knowledge Evaluator result
                        history_data = {
                           "difficulty": assessment["difficulty"],
                           "question": assessment["question"],
                           "reference_answer": assessment.get("reference_answer"),
                           "key_concepts": assessment.get("key_concepts", []),
                           "learner_answer": learner_answer,
                           "evaluation": evaluation
                        }

                        saved = save_learning_history(
                           session_title="Knowledge Evaluation",
                           subject=assessment["subject"],
                           topic=assessment["topic"],
                           data=history_data
                        )

                        if saved:
                             st.success("Evaluation result saved to Learning History.")
                        else:
                            st.info(
                              "Evaluation completed, but Learning History saving "
                              "is disabled."
                            )

                except Exception as e:

                    st.error(f"Evaluation failed: {e}")

        # Display evaluation results

        evaluation = st.session_state.get("knowledge_evaluation")

        if evaluation:

            st.divider()

            st.subheader("Evaluation Results")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Your Score",
                    f"{evaluation['score']}%"
                )

            with col2:
                st.metric(
                    "Understanding Level",
                    evaluation["understanding"]
                )

            st.subheader("Strengths")

            if evaluation["strengths"]:
                for strength in evaluation["strengths"]:
                    st.write(f"✅ {strength}")
            else:
                st.write("No specific strengths identified yet.")

            st.subheader("Knowledge Gaps")

            if evaluation["knowledge_gaps"]:
                for gap in evaluation["knowledge_gaps"]:
                    st.write(f"📌 {gap}")
            else:
                st.success("All assessed key concepts were covered.")

            st.subheader("Feedback")

            st.write(evaluation["feedback"])

            st.subheader("Improvement Suggestions")

            for suggestion in evaluation["improvement_suggestions"]:
                st.write(f"💡 {suggestion}")

# --------------------------------------------------
# LEARNING HISTORY
# --------------------------------------------------

elif selected_page == "Learning History":

    st.title("Learning History")

    st.write(
        "View your previously saved quiz results, "
        "knowledge evaluations and practice sessions."
    )

    quiz_results = get_quiz_results()
    learning_history = get_learning_history()

    # Separate learning history records by session type
    knowledge_sessions = [
        session for session in learning_history
        if session.get("session_title") == "Knowledge Evaluation"
    ]

    practice_sessions = [
        session for session in learning_history
        if session.get("session_title") == "Practice Arena - MCQ"
    ]

    coding_sessions = [
        session for session in learning_history
        if session.get("session_title") == "Practice Arena - Coding Challenge"
    ]

    st.divider()

    # --------------------------------------------------
    # SMART QUIZ HISTORY
    # --------------------------------------------------

    st.subheader("📚 Smart Quiz History")

    if quiz_results:

        for quiz in quiz_results:

            with st.expander(
                f"{quiz['topic']} | {format_ist_time(quiz['created_at'])}"
            ):

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Score",
                    f"{quiz['score_percentage']}%"
                )

                col2.metric(
                    "Correct Answers",
                    f"{quiz['correct_answers']}/{quiz['total_questions']}"
                )

                col3.metric(
                    "Difficulty",
                    quiz["difficulty"]
                )

                st.write(f"**Subject:** {quiz['subject']}")
                st.write(f"**Topic:** {quiz['topic']}")

    else:
        st.info("No quiz results saved yet.")

    st.divider()

    # --------------------------------------------------
    # KNOWLEDGE EVALUATION HISTORY
    # --------------------------------------------------

    st.subheader("🧠 Knowledge Evaluation History")

    if knowledge_sessions:

        for session in knowledge_sessions:

            data = session["conversation_data"]
            evaluation = data.get("evaluation", {})

            with st.expander(
                f"{session['topic']} | {format_ist_time(session['created_at'])}"
            ):

                st.write(f"**Subject:** {session['subject']}")
                st.write(f"**Topic:** {session['topic']}")
                st.write(f"**Difficulty:** {data.get('difficulty', 'N/A')}")

                st.write("**Question:**")
                st.write(data.get("question", "N/A"))

                st.write("**Your Answer:**")
                st.write(data.get("learner_answer", "N/A"))

                if evaluation:

                    col1, col2 = st.columns(2)

                    col1.metric(
                        "Score",
                        f"{evaluation.get('score', 0)}%"
                    )

                    col2.metric(
                        "Understanding",
                        evaluation.get("understanding", "N/A")
                    )

                    st.write("**Feedback:**")
                    st.write(evaluation.get("feedback", "N/A"))

                    st.write("**Knowledge Gaps:**")

                    for gap in evaluation.get("knowledge_gaps", []):
                        st.write(f"📌 {gap}")

                    st.write("**Improvement Suggestions:**")

                    for suggestion in evaluation.get(
                        "improvement_suggestions", []
                    ):
                        st.write(f"💡 {suggestion}")

    else:
        st.info("No knowledge evaluation sessions saved yet.")

    st.divider()

    # --------------------------------------------------
    # PRACTICE ARENA HISTORY
    # --------------------------------------------------

    st.subheader("🎯 Practice Arena History")

    if practice_sessions:

        for session in practice_sessions:

            data = session["conversation_data"]
            summary = data.get("summary", {})

            with st.expander(
                f"{session['topic']} | {format_ist_time(session['created_at'])}"
            ):

                st.write(f"**Subject:** {session['subject']}")
                st.write(f"**Topic:** {session['topic']}")
                st.write(f"**Difficulty:** {data.get('difficulty', 'N/A')}")

                st.write(
                    f"**Practice Type:** "
                    f"{'Timed' if data.get('timed') else 'Untimed'}"
                )

                if data.get("timed"):
                    st.write(
                        f"**Time Limit:** "
                        f"{data.get('time_limit_minutes')} minutes"
                    )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Score",
                    f"{summary.get('percentage', 0)}%"
                )

                col2.metric(
                    "Correct Answers",
                    f"{summary.get('correct_answers', 0)}"
                )

                col3.metric(
                    "Incorrect Answers",
                    f"{summary.get('incorrect_answers', 0)}"
                )

                st.write(
                    f"**Performance:** "
                    f"{data.get('performance', 'N/A')}"
                )

                st.write(data.get("message", ""))

                st.divider()

                st.write("**Answer Review:**")

                for index, item in enumerate(
                    data.get("detailed_results", [])
                ):

                    st.markdown(
                        f"**Question {index + 1}: "
                        f"{item.get('question', 'N/A')}**"
                    )

                    if item.get("is_correct"):
                        st.success("Correct answer!")
                    else:
                        st.error(
                            f"Your answer: "
                            f"{item.get('user_answer') or 'Not answered'}"
                        )

                    st.write(
                        f"Correct answer: "
                        f"{item.get('correct_answer', 'N/A')}"
                    )

                    st.info(item.get("explanation", "No explanation available."))

    else:
        st.info("No practice sessions saved yet.")

    st.divider()

    # --------------------------------------------------
    # CODING CHALLENGE HISTORY
    # --------------------------------------------------

    st.subheader("💻 Coding Challenge History")

    if coding_sessions:

        for session in coding_sessions:

            data = session["conversation_data"]
            evaluation = data.get("evaluation", {})

            with st.expander(
                f"{session['topic']} | {format_ist_time(session['created_at'])}"
            ):

                st.write(f"**Subject:** {session['subject']}")
                st.write(
                    f"**Challenge:** "
                    f"{data.get('challenge_title', session['topic'])}"
                )
                st.write(
                    f"**Difficulty:** {data.get('difficulty', 'N/A')}"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Score",
                    f"{evaluation.get('score', 0)}/100"
                )
                col2.metric(
                    "Correctness",
                    evaluation.get("correctness", "N/A")
                )
                col3.metric(
                    "Code Quality",
                    evaluation.get("code_quality", "N/A")
                )

                st.write("**Your Submitted Code:**")
                st.code(
                    data.get("code_submission", ""),
                    language="python"
                )

                st.write("**Strengths:**")
                strengths = evaluation.get("strengths", [])

                if strengths:
                    for item in strengths:
                        st.success(item)
                else:
                    st.write("No strengths recorded.")

                st.write("**Areas to Improve:**")
                issues = evaluation.get("issues", [])

                if issues:
                    for item in issues:
                        st.warning(item)
                else:
                    st.write("No issues recorded.")

                st.write("**Feedback:**")
                st.write(evaluation.get("feedback", "N/A"))

                st.write("**Suggestions:**")
                suggestions = evaluation.get("suggestions", [])

                if suggestions:
                    for item in suggestions:
                        st.write(f"- {item}")
                else:
                    st.write("No suggestions recorded.")

    else:
        st.info("No coding challenge attempts saved yet.")

# --------------------------------------------------
# LEARNING ROADMAP
# --------------------------------------------------

elif selected_page == "Learning Roadmap":

    st.title("Personalised Learning Roadmap")

    st.write(
        "Plan your learning journey, track topic progress, "
        "and monitor your development."
    )

    # Retrieve saved topic progress
    topic_records = get_topic_progress()

    # Overall progress metrics
    total_topics = len(topic_records)

    completed_topics = sum(
        1 for item in topic_records
        if item["status"] == "Completed"
    )

    in_progress_topics = sum(
        1 for item in topic_records
        if item["status"] == "In Progress"
    )

    overall_progress = (
        sum(item["progress_percentage"] for item in topic_records)
        / total_topics
        if total_topics > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Topics", total_topics)
    col2.metric("Completed Topics", completed_topics)
    col3.metric("In Progress", in_progress_topics)

    st.metric(
        "Overall Learning Progress",
        f"{overall_progress:.1f}%"
    )

    st.progress(overall_progress / 100)

    st.divider()

    # Add or update learning topic
    st.subheader("Add or Update Learning Topic")

    with st.form("learning_roadmap_form"):

        subject = st.text_input(
            "Subject",
            placeholder="e.g. Computer Science"
        )

        topic = st.text_input(
            "Learning Topic",
            placeholder="e.g. Python Functions"
        )

        status = st.selectbox(
            "Learning Status",
            [
                "Not Started",
                "In Progress",
                "Completed"
            ]
        )

        progress_percentage = st.slider(
            "Topic Progress",
            min_value=0,
            max_value=100,
            value=0,
            step=5
        )

        submit_topic = st.form_submit_button(
            "Save Learning Progress",
            width="stretch"
        )

        if submit_topic:

            if not subject.strip() or not topic.strip():

                st.warning(
                    "Please enter both subject and learning topic."
                )

            else:

                try:

                    saved = save_topic_progress(
                        subject=subject.strip(),
                        topic=topic.strip(),
                        status=status,
                        progress_percentage=progress_percentage
                    )

                    if saved:
                        st.success(
                            "Learning progress saved successfully!"
                        )
                        st.rerun()

                    else:
                        st.info(
                            "Learning history saving is disabled. "
                            "Enable it in Settings to save progress."
                        )

                except Exception as e:

                    st.error(
                        f"Unable to save learning progress: {e}"
                    )

    st.divider()

    # Display saved learning topics
    st.subheader("Your Learning Topics")

    topic_records = get_topic_progress()

    if topic_records:

        for item in topic_records:

            with st.expander(
                f"{item['topic']} | {item['status']}"
            ):

                st.write(f"**Subject:** {item['subject']}")
                st.write(f"**Status:** {item['status']}")

                st.progress(
                    float(item["progress_percentage"]) / 100
                )

                st.write(
                    f"**Progress:** "
                    f"{item['progress_percentage']:.0f}%"
                )

                st.caption(
                    f"Last updated: {item['updated_at']}"
                )

    else:

        st.info(
            "No learning topics added yet. "
            "Add your first topic above to start tracking progress."
        )


elif selected_page == "My Learning Journey":

    st.title("📊 My Learning Journey")

    st.write(
        "Explore your learning activities, monitor your performance, "
        "identify strengths, and discover areas for improvement."
    )

    st.divider()

    # Retrieve existing learning records
    quiz_records = get_quiz_results()
    learning_records = get_learning_history()
    topic_records = get_topic_progress()

    # Separate learning activity records
    knowledge_records = [
        item for item in learning_records
        if item["session_title"] == "Knowledge Evaluation"
    ]

    practice_records = [
        item for item in learning_records
        if item["session_title"] == "Practice Arena - MCQ"
    ]

    coding_records = [
        item for item in learning_records
        if item["session_title"] == "Practice Arena - Coding Challenge"
    ]

    # Learning overview
    st.subheader("Learning Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Smart Quizzes",
        len(quiz_records)
    )

    col2.metric(
        "Knowledge Evaluations",
        len(knowledge_records)
    )

    col3.metric(
        "Practice Sessions",
        len(practice_records)
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Coding Attempts",
        len(coding_records)
    )

    col5.metric(
        "Tracked Topics",
        len(topic_records)
    )

    total_activities = (
        len(quiz_records)
        + len(knowledge_records)
        + len(practice_records)
        + len(coding_records)
    )

    col6.metric(
        "Total Learning Activities",
        total_activities
    )

    st.divider()

    st.subheader("Your Learning Activity")

    if total_activities > 0:

        st.write(
            "Your recorded learning activities are displayed below."
        )

        activity_data = {
            "Activity": [
                "Smart Quizzes",
                "Knowledge Evaluations",
                "Practice Sessions",
                "Coding Attempts"
            ],
            "Total": [
                len(quiz_records),
                len(knowledge_records),
                len(practice_records),
                len(coding_records)
            ]
        }

        st.bar_chart(
            activity_data,
            x="Activity",
            y="Total"
        )

    else:

        st.info(
            "No learning activities recorded yet. "
            "Complete a quiz, evaluation, or practice session "
            "to begin building your learning journey."
        )

    st.divider()

    st.subheader("Learning Progress")

    if topic_records:

        for item in topic_records:

            st.write(
                f"**{item['subject']} — {item['topic']}**"
            )

            st.progress(
                float(item["progress_percentage"]) / 100
            )

            st.caption(
                f"{item['status']} | "
                f"{item['progress_percentage']:.0f}% completed"
            )

    else:

        st.info(
            "No tracked topics found. Add topics in Learning Roadmap "
            "to monitor your progress here."
        )


    st.divider()

    # Quiz Performance Analytics
    st.subheader("📈 Quiz Performance Analytics")

    if quiz_records:

        quiz_scores = [
            float(item["score_percentage"])
            for item in quiz_records
            if item.get("score_percentage") is not None
        ]

        if quiz_scores:

            # Prepare scores in chronological order
            chronological_quizzes = sorted(
               [
                    item for item in quiz_records
                    if item.get("score_percentage") is not None
               ],
               key=lambda item: item["created_at"]
            )

            average_score = sum(quiz_scores) / len(quiz_scores)
            best_score = max(quiz_scores)
            latest_score = float(
                chronological_quizzes[-1]["score_percentage"]
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Average Quiz Score",
                f"{average_score:.1f}%"
            )

            col2.metric(
                "Best Quiz Score",
                f"{best_score:.1f}%"
            )

            col3.metric(
                "Latest Quiz Score",
                f"{latest_score:.1f}%"
            )
            
            chart_data = {
                "Quiz Attempt": [
                    f"Quiz {index + 1}"
                    for index in range(len(chronological_quizzes))
                ],
                "Score (%)": [
                    float(item["score_percentage"])
                    for item in chronological_quizzes
                ]
            }

            st.write("**Your Quiz Score Trend**")

            if len(chronological_quizzes) == 1:
                  st.info(
                    "Your first quiz score is recorded! "
                    "Complete more quizzes to unlock your "
                    "performance trend."
                )

            else:

                st.line_chart(
                    chart_data,
                    x="Quiz Attempt",
                    y="Score (%)"
                )

            st.caption(
                "The chart shows your quiz scores in chronological order."
            )

        else:

            st.info(
                "No valid quiz scores are available for analytics yet."
            )

    else:

        st.info(
            "Complete a Smart Quiz to start tracking your performance."
        )

    st.divider()

    # Practice Performance Analytics
    st.subheader("🎯 Practice Performance Analytics")

    practice_score_records = []

    for session in practice_records:

        data = session.get("conversation_data") or {}
        summary = data.get("summary") or {}
        percentage = summary.get("percentage")

        if percentage is not None:

            try:
                practice_score_records.append({
                    "created_at": session["created_at"],
                    "score": float(percentage)
                })

            except (ValueError, TypeError):
                continue

    if practice_score_records:

        average_practice_score = sum(
            item["score"] for item in practice_score_records
        ) / len(practice_score_records)

        best_practice_score = max(
            item["score"] for item in practice_score_records
        )

        chronological_practice = sorted(
            practice_score_records,
            key=lambda item: item["created_at"]
        )

        latest_practice_score = chronological_practice[-1]["score"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Average Practice Score",
            f"{average_practice_score:.1f}%"
        )

        col2.metric(
            "Best Practice Score",
            f"{best_practice_score:.1f}%"
        )

        col3.metric(
            "Latest Practice Score",
            f"{latest_practice_score:.1f}%"
        )

        st.write("**Your Practice Score Trend**")

        if len(chronological_practice) == 1:

            st.info(
                "Your first practice score is recorded! "
                "Complete more practice sessions to unlock "
                "your performance trend."
            )

        else:

            practice_chart_data = {
                "Practice Attempt": [
                    f"Attempt {index + 1}"
                    for index in range(len(chronological_practice))
                ],
                "Score (%)": [
                    item["score"]
                    for item in chronological_practice
                ]
            }

            st.line_chart(
                practice_chart_data,
                x="Practice Attempt",
                y="Score (%)"
            )

    else:

        st.info(
            "No valid practice scores are available yet. "
            "Complete a Practice Arena MCQ session to begin."
        )


    st.divider()

    # Coding Performance Analytics
    st.subheader("💻 Coding Performance Analytics")

    coding_score_records = []

    correctness_counts = {}

    for session in coding_records:

        data = session.get("conversation_data") or {}
        evaluation = data.get("evaluation") or {}

        score = evaluation.get("score")
        correctness = evaluation.get("correctness")

        if score is not None:

            try:
                numeric_score = float(score)

                if 0 <= numeric_score <= 100:

                    coding_score_records.append({
                        "created_at": session["created_at"],
                        "score": numeric_score,
                        "correctness": correctness or "Not Available"
                    })

                    label = correctness or "Not Available"

                    correctness_counts[label] = (
                        correctness_counts.get(label, 0) + 1
                    )

            except (ValueError, TypeError):
                continue

    if coding_score_records:

        chronological_coding = sorted(
            coding_score_records,
            key=lambda item: item["created_at"]
        )

        scores = [
            item["score"]
            for item in chronological_coding
        ]

        average_coding_score = sum(scores) / len(scores)
        best_coding_score = max(scores)
        latest_coding_score = scores[-1]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Average Coding Score",
            f"{average_coding_score:.1f}%"
        )

        col2.metric(
            "Best Coding Score",
            f"{best_coding_score:.1f}%"
        )

        col3.metric(
            "Latest Coding Score",
            f"{latest_coding_score:.1f}%"
        )

        st.write("**Your Coding Performance Trend**")

        if len(chronological_coding) == 1:

            st.info(
                "Your first coding attempt is recorded! "
                "Complete more coding challenges to unlock "
                "your performance trend."
            )

        else:

            coding_chart_data = {
                "Coding Attempt": [
                    f"Attempt {index + 1}"
                    for index in range(len(chronological_coding))
                ],
                "Score (%)": scores
            }

            st.line_chart(
                coding_chart_data,
                x="Coding Attempt",
                y="Score (%)"
            )

        st.divider()

        st.write("**Coding Correctness Analysis**")

        if len(coding_score_records) == 1:

            st.info(
                "Your first coding evaluation is recorded! "
                "Complete more coding challenges to build "
                "your correctness analysis."
            )

        else:

            correctness_chart_data = {
                "Evaluation": list(correctness_counts.keys()),
                "Attempts": list(correctness_counts.values())
            }

            st.bar_chart(
               correctness_chart_data,
               x="Evaluation",
               y="Attempts"
            )

        st.caption(
            "Coding scores are AI-assisted estimates based on "
            "static code analysis and AI review, not verified "
            "test-case execution."
        )

    else:

        st.info(
            "No valid coding evaluation records are available yet. "
            "Complete a Python Coding Challenge to begin tracking "
            "your coding performance."
        )

        st.divider()

    # Strength Analysis & Weak Topic Detection
    st.subheader("🧠 Strength Analysis & Weak Topic Detection")

    topic_performance = {}

    # Collect Smart Quiz scores
    for item in quiz_records:

        subject = item.get("subject") or "Unknown Subject"
        topic = item.get("topic")
        score = item.get("score_percentage")

        if topic and score is not None:

            try:
                numeric_score = float(score)

                if 0 <= numeric_score <= 100:
                    topic_key = (subject, topic)

                    if topic_key not in topic_performance:
                        topic_performance[topic_key] = []

                    topic_performance[topic_key].append(numeric_score)

            except (ValueError, TypeError):
                continue
   
    # Collect Practice Arena MCQ scores
    for session in practice_records:

        subject = session.get("subject") or "Unknown Subject"
        topic = session.get("topic")
        data = session.get("conversation_data") or {}
        summary = data.get("summary") or {}
        score = summary.get("percentage")

        if topic and score is not None:

            try:
                numeric_score = float(score)

                if 0 <= numeric_score <= 100:

                    topic_key = (subject, topic)

                    if topic_key not in topic_performance:
                        topic_performance[topic_key] = []

                    topic_performance[topic_key].append(numeric_score)

            except (ValueError, TypeError):
                continue


    if topic_performance:

        strength_topics = []
        developing_topics = []
        weak_topics = []

        for (subject, topic), scores in topic_performance.items():

            if len(scores) < 2:
                continue

            average = sum(scores) / len(scores)

            topic_result = {
                "Subject": subject,
                "Topic": topic,
                "Average Score (%)": round(average, 1),
                "Attempts": len(scores)
            }

            if average >= 80:
                strength_topics.append(topic_result)

            elif average < 60:
                weak_topics.append(topic_result)

            else:
                developing_topics.append(topic_result)

        if strength_topics or developing_topics or weak_topics:

            col1, col2, col3 = st.columns(3)

            col1.metric("Strengths", len(strength_topics))
            col2.metric("Developing Topics", len(developing_topics))
            col3.metric("Needs Improvement", len(weak_topics))

            if strength_topics:

                st.write("**🌟 Your Strengths**")

                st.dataframe(
                    strength_topics,
                    width="stretch",
                    hide_index=True
                )

            if developing_topics:

                st.write("**📘 Developing Topics**")

                st.dataframe(
                    developing_topics,
                    width="stretch",
                    hide_index=True
                )

            if weak_topics:

                st.write("**🎯 Topics Needing Improvement**")

                st.dataframe(
                    weak_topics,
                    width="stretch",
                    hide_index=True
                )

        else:

            st.info(
                "Complete at least two quizzes or practice attempts "
                "for the same topic to unlock your strength analysis."
            )

    else:

        st.info(
            "Complete Smart Quizzes or Practice Arena MCQ sessions "
            "to begin identifying your strengths and learning gaps."
        )

    st.caption(
        "Analysis is based on Smart Quiz and Practice Arena MCQ "
        "scores. Topics require at least two attempts before "
        "a performance category is assigned."
    )

    # --------------------------------------------------
    # 7. LEARNING GOALS
    # --------------------------------------------------

    st.divider()
    st.subheader("🎯 Learning Goals")

    st.write(
        "Set learning targets and track your progress "
        "automatically as you use AI LearnSphere."
    )

    st.caption(
        "Progress tracking depends on Learning History being enabled "
        "so your learning activity can be saved."
    )

    # --------------------------------------------------
    # CREATE A NEW GOAL
    # --------------------------------------------------
    st.markdown("### Create a New Goal")

    goal_type = st.selectbox(
        "Goal Type",
        [
            "Score Goal",
            "Practice Goal",
            "Topic Completion Goal"
        ],
        help=(
            "Score Goal: achieve a quiz or MCQ score.\n"
            "Practice Goal: complete practice sessions.\n"
            "Topic Completion Goal: reach a topic progress percentage."
        )
    )
    with st.form("create_learning_goal_form"):

        goal_title = st.text_input(
            "Goal Title",
            placeholder="Example: Improve my Python knowledge"
        )

        col1, col2 = st.columns(2)

        with col1:
            goal_subject = st.text_input(
                "Subject",
                placeholder="Example: Python"
            )

        with col2:
            goal_topic = st.text_input(
                "Topic",
                placeholder="Example: Variables"
            )

        if goal_type == "Practice Goal":

            target_value = st.number_input(
                "Target Number of Practice Sessions",
                min_value=1,
                max_value=100000,
                value=5,
                step=1
            )

        else:

            target_value = st.number_input(
                "Target Percentage",
                min_value=1.0,
                max_value=100.0,
                value=80.0,
                step=1.0
            )

        deadline = st.date_input(
            "Goal Deadline",
            value=date.today(),
            min_value=date.today()
        )

        create_goal_button = st.form_submit_button(
            "Create Learning Goal",
            type="primary",
            width="stretch"
        )

        if create_goal_button:

            if not goal_title.strip():

                st.error("Please enter a goal title.")

            elif (
                goal_type == "Topic Completion Goal"
                and (
                    not goal_subject.strip()
                    or not goal_topic.strip()
                )
            ):

                st.error(
                    "Subject and topic are required "
                    "for a Topic Completion Goal."
                )

            else:

                try:

                    create_goal(
                        goal_type=goal_type,
                        title=goal_title.strip(),
                        target_value=(
                            int(target_value)
                            if goal_type == "Practice Goal"
                            else float(target_value)
                        ),
                        deadline=deadline,
                        subject=goal_subject.strip() or None,
                        topic=goal_topic.strip() or None
                    )

                    st.success("Learning goal created successfully!")
                    st.rerun()

                except Exception as error:

                    st.error(f"Unable to create goal: {error}")

    # --------------------------------------------------
    # DISPLAY AND TRACK SAVED GOALS
    # --------------------------------------------------

    st.divider()
    st.markdown("### Your Learning Goals")

    try:

        goal_progress_records = get_all_goal_progress()

        if not goal_progress_records:

            st.info(
                "You haven't created any learning goals yet. "
                "Create your first goal above!"
            )

        else:

            for goal in goal_progress_records:

                goal_id = goal["id"]

                with st.expander(
                    f"🎯 {goal['title']} — {goal['status']}",
                    expanded=False
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write("**Goal Type**")
                        st.write(goal["goal_type"])

                        st.write("**Subject**")
                        st.write(goal.get("subject") or "All subjects")

                    with col2:

                        st.write("**Topic**")
                        st.write(goal.get("topic") or "All topics")

                        st.write("**Deadline**")
                        st.write(str(goal["deadline"])[:10])

                    st.write("**Current Progress**")

                    current_value = goal["current_value"]
                    target = goal["target_value"]

                    if goal["goal_type"] == "Practice Goal":

                        st.write(
                            f"{int(current_value)} / {int(target)} sessions"
                        )

                    else:

                        st.write(
                            f"{current_value:.2f}% / {target:.2f}%"
                        )

                    st.progress(
                        min(
                            max(
                                goal["completion_percentage"] / 100,
                                0.0
                            ),
                            1.0
                        )
                    )

                    st.caption(
                        f"Completion: "
                        f"{goal['completion_percentage']:.2f}%"
                    )

                    if goal["status"] == "Completed":

                        st.success("Congratulations! Goal completed.")

                    elif goal["status"] == "Overdue":

                        st.error("This goal is overdue.")

                    else:

                        if goal["goal_type"] == "Practice Goal":

                            st.info(
                                f"{int(goal['remaining'])} "
                                "practice sessions remaining."
                            )

                        else:

                            st.info(
                                f"{goal['remaining']:.2f}% "
                                "remaining to reach your target."
                            )

                    # --------------------------------------------------
                    # EDIT GOAL
                    # --------------------------------------------------

                    st.markdown("#### Edit Goal")

                    with st.form(
                        f"edit_goal_form_{goal_id}"
                    ):

                        edited_title = st.text_input(
                            "Goal Title",
                            value=goal["title"],
                            key=f"edit_title_{goal_id}"
                        )

                        edit_col1, edit_col2 = st.columns(2)

                        with edit_col1:

                            edited_subject = st.text_input(
                                "Subject",
                                value=goal.get("subject") or "",
                                key=f"edit_subject_{goal_id}"
                            )

                        with edit_col2:

                            edited_topic = st.text_input(
                                "Topic",
                                value=goal.get("topic") or "",
                                key=f"edit_topic_{goal_id}"
                            )

                        if goal["goal_type"] == "Practice Goal":

                            edited_target = st.number_input(
                                "Target Sessions",
                                min_value=1,
                                max_value=100000,
                                value=int(target),
                                step=1,
                                key=f"edit_target_{goal_id}"
                            )

                        else:

                            edited_target = st.number_input(
                                "Target Percentage",
                                min_value=1.0,
                                max_value=100.0,
                                value=float(target),
                                step=1.0,
                                key=f"edit_target_{goal_id}"
                            )

                        existing_deadline = date.fromisoformat(
                            str(goal["deadline"])[:10]
                        )

                        edited_deadline = st.date_input(
                           "Deadline",
                            value=existing_deadline,
                            min_value=min(date.today(), existing_deadline),
                            key=f"edit_deadline_{goal_id}"
                        )
                       
                        save_changes = st.form_submit_button(
                            "Save Changes",
                            width="stretch"
                        )

                        if save_changes:

                            if not edited_title.strip():

                                st.error(
                                    "Goal title cannot be empty."
                                )

                            elif (
                                goal["goal_type"]
                                == "Topic Completion Goal"
                                and (
                                    not edited_subject.strip()
                                    or not edited_topic.strip()
                                )
                            ):

                                st.error(
                                    "Subject and topic are required "
                                    "for this goal."
                                )

                            else:

                                try:

                                    update_goal(
                                        goal_id,
                                        title=edited_title.strip(),
                                        subject=(
                                            edited_subject.strip() or None
                                        ),
                                        topic=(
                                            edited_topic.strip() or None
                                        ),
                                        target_value=edited_target,
                                        deadline=edited_deadline
                                    )

                                    st.success(
                                        "Goal updated successfully!"
                                    )
                                    st.rerun()

                                except Exception as error:

                                    st.error(
                                        f"Unable to update goal: {error}"
                                    )

                    # --------------------------------------------------
                    # DELETE GOAL
                    # --------------------------------------------------

                    st.markdown("#### Delete Goal")

                    if st.button(
                        "Delete This Goal",
                        key=f"delete_goal_{goal_id}",
                        type="secondary"
                    ):

                        try:

                            delete_goal(goal_id)

                            st.success(
                                "Learning goal deleted successfully!"
                            )
                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to delete goal: {error}"
                            )

    except Exception as error:

        st.error(
            f"Unable to load learning goals: {error}"
        )

# --------------------------------------------------
# DOCUMENT INTELLIGENCE
# --------------------------------------------------

elif selected_page == "Document Intelligence":

    st.title("📚 Document Intelligence")

    st.write(
        "Upload your study materials, ask questions, "
        "and receive AI-generated answers grounded in your documents."
    )

    st.divider()

    # --------------------------------------------------
    # DOCUMENT UPLOAD
    # --------------------------------------------------

    st.subheader("Upload Learning Documents")

    uploaded_files = st.file_uploader(
        "Choose PDF, TXT or DOCX files",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        key="document_upload_files"
    )

    if st.button(
        "Upload Selected Documents",
        type="primary",
        disabled=not uploaded_files
    ):

        successful_uploads = 0

        for uploaded_file in uploaded_files:

            try:
                with st.spinner(
                    f"Processing {uploaded_file.name}..."
                ):

                    result = upload_document(uploaded_file)

                st.success(
                    f"{uploaded_file.name} uploaded successfully! "
                    f"({result['total_chunks']} chunks)"
                )

                successful_uploads += 1

            except Exception as error:

                st.error(
                    f"Unable to upload {uploaded_file.name}: {error}"
                )

        if successful_uploads:
            st.session_state.document_qa_result = None

    st.divider()

    # --------------------------------------------------
    # REGISTERED DOCUMENTS
    # --------------------------------------------------

    st.subheader("Your Uploaded Documents")

    documents = get_registered_documents()

    if documents:

        document_lookup = {
            document["document_id"]: document
            for document in documents
        }

        st.metric(
            "Total Uploaded Documents",
            len(documents)
        )

        for document in documents:

            with st.expander(document["filename"]):

                st.write(
                    f"**File Type:** {document['file_type'].upper()}"
                )

                st.write(
                    f"**Total Chunks:** {document['total_chunks']}"
                )

                st.write(
                    f"**Uploaded At:** {document['uploaded_at']}"
                )

                st.caption(
                    f"Document ID: {document['document_id']}"
                )

        # --------------------------------------------------
        # DELETE DOCUMENT
        # --------------------------------------------------

        st.divider()

        st.subheader("Manage Documents")

        selected_delete_id = st.selectbox(
            "Select a document to delete",
            options=list(document_lookup.keys()),
            format_func=lambda document_id: (
                f"{document_lookup[document_id]['filename']} "
                f"({document_id[:8]})"
            ),
            key="document_delete_selection"
        )

        if st.button(
            "Delete Selected Document",
            type="secondary"
        ):

            try:

                remove_document(
                    document_id=selected_delete_id
                )

                st.session_state.document_qa_result = None

                st.success(
                    "Document deleted from ChromaDB, SQLite "
                    "and physical storage."
                )

                st.rerun()

            except Exception as error:

                st.error(f"Document deletion failed: {error}")

        # --------------------------------------------------
        # DOCUMENT QUESTION ANSWERING
        # --------------------------------------------------

        st.divider()

        st.subheader("Ask Questions About Your Documents")

        st.write(
            "Select one or multiple documents and ask "
            "questions about their content."
        )

        selected_document_ids = st.multiselect(
            "Select Documents",
            options=list(document_lookup.keys()),
            format_func=lambda document_id: (
                document_lookup[document_id]["filename"]
            ),
            key="document_qa_selected_documents"
        )

        question = st.text_area(
            "Enter Your Question",
            placeholder=(
                "Example: What is a Python variable "
                "and how is it created?"
            ),
            height=100,
            key="document_qa_question"
        )

        if st.button(
            "Ask AI About Documents",
            type="primary",
            disabled=(
                not selected_document_ids
                or not question.strip()
            )
        ):

            st.session_state.document_qa_result = None

            try:

                with st.spinner(
                    "Searching documents and generating your answer..."
                ):

                    result = answer_document_question(
                        query=question.strip(),
                        document_ids=selected_document_ids,
                        model="llama3.2:latest"
                    )

                    st.session_state.document_qa_result = result

            except Exception as error:

                st.error(
                    f"Unable to answer your question: {error}"
                )

        # --------------------------------------------------
        # DISPLAY ANSWER
        # --------------------------------------------------

        qa_result = st.session_state.get(
            "document_qa_result"
        )

        if qa_result:

            st.divider()

            st.subheader("🤖 AI Generated Answer")

            st.markdown(qa_result["answer"])

            st.caption(
                f"Retrieved Chunks: {qa_result['retrieval_count']}"
            )

            st.divider()

            st.subheader("📖 Source References")

            if qa_result["sources"]:

                for source in qa_result["sources"]:

                    source_title = (
                        f"Source {source['source_number']}: "
                        f"{source['filename']}"
                    )

                    with st.expander(source_title):

                        st.write(
                            f"**Document ID:** "
                            f"{source['document_id']}"
                        )

                        if source["page"] is not None:

                            st.write(
                                f"**Page:** {source['page']}"
                            )

                        if source["section"]:

                            st.write(
                                f"**Section:** {source['section']}"
                            )

                        if source["chunk"] is not None:

                            st.write(
                                f"**Chunk:** {source['chunk']}"
                            )

            else:

                st.info("No source references available.")

    else:

        st.info(
            "No documents uploaded yet. "
            "Upload your first learning document above "
            "to start using Document Intelligence."
        )

# --------------------------------------------------
# PRACTICE ARENA
# --------------------------------------------------

elif selected_page == "Practice Arena":

    st.title("🎯 Practice Arena")

    st.write(
        "Strengthen your knowledge through structured practice "
        "sessions, timed assessments and instant feedback."
    )

    st.divider()

    st.subheader("Configure Your Practice Session")

    col1, col2 = st.columns(2)

    with col1:

        subject = st.text_input(
            "Subject",
            value="Computer Science",
            key="practice_subject"
        )

        topic = st.text_input(
            "Practice Topic",
            placeholder="e.g. Python Variables",
            key="practice_topic"
        )

        difficulty = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            key="practice_difficulty"
        )

    with col2:

        num_questions = st.selectbox(
            "Number of Questions",
            [5, 10, 15, 20],
            key="practice_question_count"
        )

        timed = st.checkbox(
            "Enable Timed Practice",
            key="practice_timed"
        )

        time_limit = None

        if timed:

            time_limit = st.selectbox(
                "Time Limit (Minutes)",
                [5, 10, 15, 20, 30],
                key="practice_time_limit"
            )

    if st.button(
        "Start Practice",
        type="primary",
        width="stretch"
    ):

        if not subject.strip() or not topic.strip():

            st.warning("Please enter both subject and topic.")

        else:

            try:

                with st.spinner("Preparing your practice session..."):

                    session = create_practice_session(
                        subject=subject.strip(),
                        topic=topic.strip(),
                        difficulty=difficulty,
                        num_questions=num_questions,
                        timed=timed,
                        time_limit_minutes=time_limit
                    )

                    st.session_state.practice_session = session
                    st.session_state.practice_result = None
                    st.session_state.practice_answers = {}
                    st.session_state.practice_submitted = False

                    if timed:
                        st.session_state.practice_deadline = (
                           time.time() + (time_limit * 60)
                        )   
                    else:                     
                        st.session_state.practice_deadline = None

                st.success("Your practice session is ready!")

            except Exception as error:

                st.error(
                    f"Unable to start practice session: {error}"
                )

    # --------------------------------------------------
    # ACTIVE PRACTICE SESSION
    # --------------------------------------------------

    session = st.session_state.get("practice_session")

    if session:

        st.divider()

        st.subheader("📝 Your Practice Questions")

        col1, col2, col3 = st.columns(3)

        col1.metric("Subject", session["subject"])
        col2.metric("Questions", session["total_questions"])
        col3.metric("Difficulty", session["difficulty"])

        if session["timed"]:

            st.info(
                f"⏱️ Time limit: "
                f"{session['time_limit_minutes']} minutes. "
                "A live countdown is displayed, and your practice "
                "will be automatically submitted when the time expires."    
            )

        if not st.session_state.practice_submitted:

            @st.fragment(run_every="1s")
            def render_practice_questions():

                # Display countdown for timed sessions.
                if session["timed"]:

                    deadline = st.session_state.get(
                        "practice_deadline"
                    )

                    if deadline is None:
                        deadline = (
                            time.time()
                            + session["time_limit_minutes"] * 60
                        )

                        st.session_state.practice_deadline = deadline

                    remaining = max(
                        0,
                        int(deadline - time.time() + 0.999)
                    )

                    minutes, seconds = divmod(
                        remaining, 60
                    )

                    st.metric(
                        "⏱️ Time Remaining",
                        f"{minutes:02d}:{seconds:02d}"
                    )

                    if remaining == 0:
                        st.warning(
                            "Time is up! Your practice is being submitted."
                        )

                st.subheader("Answer the Questions")

                answers = {}

                for index, question in enumerate(
                    session["questions"]
                ):

                    st.markdown(
                        f"**Question {index + 1}. "
                        f"{question['question']}**"
                    )

                    options = question["options"]

                    answers[index] = st.radio(
                        "Choose your answer:",
                        options=list(options.keys()),
                        format_func=lambda key, opts=options: (
                            f"{key}. {opts[key]}"
                        ),
                        key=f"practice_answer_{index}",
                        index=None
                    )

                    st.write("")

                manual_submit = st.button(
                    "Submit Practice",
                    type="primary",
                    width="stretch",
                    key="submit_practice"
                )

                time_expired = (
                    session["timed"]
                    and remaining == 0
                )

                if manual_submit or time_expired:

                    try:

                        # Collect all selected answers.
                        final_answers = {
                            index: st.session_state.get(
                                f"practice_answer_{index}"
                            )
                            for index in range(
                                len(session["questions"])
                            )
                        }

                        with st.spinner(
                            "Evaluating your answers..."
                        ):

                            result = evaluate_practice_session(
                                session=session,
                                user_answers=final_answers
                            )

                            st.session_state.practice_result = result
                            st.session_state.practice_answers = final_answers
                            st.session_state.practice_submitted = True

                            history_data = {
                                "difficulty": result["difficulty"],
                                "timed": result["timed"],
                                "time_limit_minutes": result["time_limit_minutes"],
                                "answers": final_answers,
                                "summary": result["summary"],
                                "performance": result["performance"],
                                "message": result["message"],
                                "detailed_results": result["detailed_results"]
                            }

                            saved = save_learning_history(
                                session_title="Practice Arena - MCQ",
                                subject=result["subject"],
                                topic=result["topic"],
                                data=history_data
                            )

                        if time_expired:
                            st.info(
                                "Your practice was automatically submitted "
                                "because the time limit ended."
                            )

                        if saved:
                            st.success(
                                "Practice result saved to Learning History."
                            )
                        else:
                            st.info(
                                "Practice completed. Learning History saving "
                                "is disabled or unavailable."
                            )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Unable to evaluate practice session: {error}"
                        )

            render_practice_questions()  
        # --------------------------------------------------
        # PRACTICE RESULTS
        # --------------------------------------------------

        result = st.session_state.get("practice_result")

        if result:

            st.divider()

            st.subheader("🏆 Practice Results")

            summary = result["summary"]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Correct Answers",
                summary["correct_answers"]
            )

            col2.metric(
                "Incorrect Answers",
                summary["incorrect_answers"]
            )

            col3.metric(
                "Score",
                f"{summary['percentage']}%"
            )

            st.subheader(result["performance"])

            st.write(result["message"])

            st.progress(summary["percentage"] / 100)

            st.divider()

            st.subheader("Answer Review")

            for index, item in enumerate(result["detailed_results"]):

                st.markdown(
                    f"**Question {index + 1}: {item['question']}**"
                )

                if item["is_correct"]:
                    st.success("Correct answer!")
                else:
                    st.error(
                        f"Your answer: "
                        f"{item['user_answer'] or 'Not answered'}"
                    )

                st.write(
                    f"Correct answer: {item['correct_answer']}"
                )

                st.info(item["explanation"])

            if st.button(
                "Start New Practice Session",
                type="primary"
            ):

                st.session_state.practice_session = None
                st.session_state.practice_result = None
                st.session_state.practice_answers = {}
                st.session_state.practice_submitted = False

                st.rerun()


    # ==========================================
    # PYTHON CODING CHALLENGES
    # ==========================================

    st.divider()

    st.subheader("💻 Python Coding Challenges")

    st.write(
        "Develop practical Python programming skills "
        "through beginner, intermediate and advanced challenges."
    )

    challenges = get_coding_challenges()

    difficulty_filter = st.selectbox(
        "Select Challenge Difficulty",
        ["All", "Beginner", "Intermediate", "Advanced"],
        key="coding_difficulty_filter"
    )

    if difficulty_filter == "All":
        filtered_challenges = challenges
    else:
        filtered_challenges = get_coding_challenges(
            difficulty=difficulty_filter
        )

    if filtered_challenges:

        challenge_options = {
            challenge["title"]: challenge["id"]
            for challenge in filtered_challenges
        }

        selected_challenge_title = st.selectbox(
            "Choose a Coding Challenge",
            list(challenge_options.keys()),
            key="coding_challenge_selection"
        )

        selected_challenge_id = challenge_options[
            selected_challenge_title
        ]

        challenge = get_coding_challenge_by_id(
            selected_challenge_id
        )

        if challenge:

            st.markdown("### Challenge Details")

            st.write(challenge["description"])

            col1, col2 = st.columns(2)

            col1.metric(
                "Difficulty",
                challenge["difficulty"]
            )

            col2.metric(
                "Topic",
                challenge["topic"]
            )

            st.markdown("### Example Input")

            st.code(
                challenge["example_input"],
                language="python"
            )

            st.markdown("### Expected Output")

            st.code(
                challenge["example_output"],
                language="text"
            )

            st.markdown("### Expected Concepts")

            for concept in challenge["expected_concepts"]:
                st.write(f"- {concept}")

            st.divider()

            st.markdown("### Write Your Python Solution")

            submitted_code = st.text_area(
                "Python Code Editor",
                height=250,
                placeholder=(
                    "def your_function(...):\n"
                    "    # Write your solution here\n"
                    "    pass"
                ),
                key=f"coding_submission_{selected_challenge_id}"
            )

            if st.button(
                "Evaluate My Code",
                type="primary",
                key="evaluate_coding_challenge"
            ):

                if not submitted_code.strip():

                    st.warning(
                        "Please write your Python solution first."
                    )

                else:

                    try:

                        with st.spinner(
                            "Evaluating your solution..."
                        ):

                            result = evaluate_code_submission(
                                challenge,
                                submitted_code
                            )

                            st.session_state[
                                "coding_result"
                            ] = result

                            st.session_state[
                                "coding_result_challenge_id"
                            ] = selected_challenge_id

                            # Prepare coding challenge history data.
                            history_data = {
                                "challenge_id": selected_challenge_id,
                                "challenge_title": challenge["title"],
                                "difficulty": challenge["difficulty"],
                                "code_submission": submitted_code,
                                "evaluation": result
                            }

                            # Save the coding attempt.
                            saved = save_learning_history(
                                session_title="Practice Arena - Coding Challenge",
                                subject="Computer Science",
                                topic=challenge["title"],
                                data=history_data
                            )

                        if saved:
                           st.success(
                               "Coding challenge result saved to Learning History."
                            )
                        else:
                            st.info(
                                "Evaluation completed, but Learning History saving "
                                "is disabled or unavailable."
                            )

                    except Exception as error:

                        st.error(
                            f"Code evaluation failed: {error}"
                        )

            # ------------------------------------------
            # CODING CHALLENGE RESULTS
            # ------------------------------------------

            if (
                st.session_state.get(
                    "coding_result_challenge_id"
                ) == selected_challenge_id
                and st.session_state.get("coding_result")
            ):

                result = st.session_state["coding_result"]

                st.divider()

                st.subheader("📊 Code Evaluation Results")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Score",
                    f"{result.get('score', 0)}/100"
                )

                col2.metric(
                    "Correctness",
                    result.get("correctness", "N/A")
                )

                col3.metric(
                    "Code Quality",
                    result.get("code_quality", "N/A")
                )

                st.markdown("#### Strengths")

                for item in result.get("strengths", []):
                    st.success(item)

                st.markdown("#### Areas to Improve")

                for item in result.get("issues", []):
                    st.warning(item)

                st.markdown("#### Feedback")

                st.write(result.get("feedback", ""))

                st.markdown("#### Suggestions")

                for item in result.get("suggestions", []):
                    st.write(f"- {item}")

                st.info(
                    "This evaluation uses AI review and static "
                    "code analysis. Submitted code is not executed, "
                    "so the score is an estimate rather than a "
                    "verified test-case result."
                )

    else:

        st.info(
            "No challenges are available for the selected difficulty."
        )

# --------------------------------------------------
# AI LEARNING INSIGHTS
# --------------------------------------------------

elif selected_page == "AI Learning Insights":

    st.title("🧠 AI Learning Insights")

    st.write(
        "Understand your learning performance, identify topic-level "
        "patterns, and receive personalized learning recommendations."
    )

    st.caption(
        "This analysis uses saved Smart Quiz and Practice Arena MCQ results. "
        "Coding Challenge and Knowledge Evaluator results remain separate "
        "in My Learning Journey and Learning History."
    )

    st.divider()

    try:

        analysis = get_performance_analysis()
        trends = analyze_learning_trends()
        recommendations = generate_recommendations()

    except Exception as error:

        st.error(f"Unable to load learning insights: {error}")

    else:

        overall = analysis["overall"]

        if overall["total_sessions"] == 0:

            st.info(
                "Complete a Smart Quiz or Practice Arena MCQ session "
                "to generate your learning insights."
            )

        else:

            # ------------------------------------------
            # OVERALL PERFORMANCE
            # ------------------------------------------

            st.subheader("📊 Overall Performance")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Learning Sessions",
                overall["total_sessions"]
            )

            col2.metric(
                "Questions Answered",
                overall["total_questions"]
            )

            col3.metric(
                "Correct Answers",
                overall["correct_answers"]
            )

            col4.metric(
                "Overall Accuracy",
                f'{overall["overall_accuracy"]:.1f}%'
            )

            performance_level = classify_performance(
                overall["overall_accuracy"]
            )

            st.info(
                f"Overall Performance Level: **{performance_level}**"
            )

            st.divider()

            # ------------------------------------------
            # SUBJECT PERFORMANCE
            # ------------------------------------------

            st.subheader("📚 Subject-wise Performance")

            subject_rows = []

            for item in analysis["subject_performance"]:

                subject_rows.append({
                    "Subject": item["subject"],
                    "Attempts": item["attempts"],
                    "Questions": item["total_questions"],
                    "Correct Answers": item["correct_answers"],
                    "Average Score (%)": round(
                        item["average_score"], 1
                    ),
                    "Performance Level": classify_performance(
                        item["average_score"]
                    )
                })

            if subject_rows:

                st.dataframe(
                    subject_rows,
                    hide_index=True,
                    width="stretch"
                )

            else:

                st.info("No subject performance data available.")

            st.divider()

            # ------------------------------------------
            # TOPIC PERFORMANCE
            # ------------------------------------------

            st.subheader("🎯 Topic-wise Performance")

            topic_rows = []

            for item in analysis["topic_performance"]:

                topic_rows.append({
                    "Subject": item["subject"],
                    "Topic": item["topic"],
                    "Attempts": item["attempts"],
                    "Questions": item["total_questions"],
                    "Correct Answers": item["correct_answers"],
                    "Average Score (%)": round(
                        item["average_score"], 1
                    ),
                    "Performance Level": classify_performance(
                        item["average_score"]
                    )
                })

            if topic_rows:

                st.dataframe(
                    topic_rows,
                    hide_index=True,
                    width="stretch"
                )

            else:

                st.info("No topic performance data available.")

            st.divider()

            # ------------------------------------------
            # LEARNING TREND ANALYSIS
            # ------------------------------------------

            st.subheader("📈 Learning Trend Analysis")

            if trends["status"] == "Insufficient Data":

                st.info(trends["message"])

            else:

                trend_col1, trend_col2, trend_col3 = st.columns(3)

                trend_col1.metric(
                    "Recent Average",
                    f'{trends["recent_average"]:.1f}%'
                )

                trend_col2.metric(
                    "Previous Average",
                    f'{trends["previous_average"]:.1f}%'
                )

                trend_col3.metric(
                    "Score Difference",
                    f'{trends["score_difference"]:+.1f}%'
                )

                st.info(
                    f'Learning Trend: **{trends["trend"]}**'
                )

                st.write(trends["message"])

            st.divider()

            # ------------------------------------------
            # PERSONALIZED RECOMMENDATIONS
            # ------------------------------------------

            st.subheader("💡 Personalized Recommendations")

            recommendation_items = recommendations["recommendations"]

            if recommendation_items:

                for item in recommendation_items:

                    priority = str(
                        item.get("priority") or "Normal"
                    ).strip()

                    subject = str(
                        item.get("subject") or ""
                    ).strip()

                    topic = str(
                        item.get("topic") or ""
                    ).strip()

                    category = str(
                        item.get("category") or "General Learning"
                    ).strip()

                    if subject and topic:
                        heading = (
                            f"{priority} Priority — {subject}: {topic}"
                        )

                    elif topic:
                        heading = (
                            f"{priority} Priority — {topic}"
                        )

                    elif subject:
                        heading = (
                            f"{priority} Priority — {subject}"
                        )

                    else:
                        heading = (
                            f"{priority} Priority — "
                            f"{category} Recommendation"
                        )

                    with st.expander(heading):

                        st.write(
                            f"**Category:** {category}"
                        )

                        score = item.get("score")

                        if score is not None:
                            st.write(
                                f"**Current Score:** {score}%"
                            )

                        suggestion = (
                            item.get("suggestion")
                            or "No recommendation details available."
                        )

                        st.write(
                            f"**Recommendation:** {suggestion}"
                        )
            else:

                st.info(recommendations["message"])

            st.divider()

            # ------------------------------------------
            # AI-GENERATED LEARNING REPORT
            # ------------------------------------------

            st.subheader("🤖 AI Learning Report")

            st.write(
                "Generate a personalized report using your saved learning "
                "performance, trends, and recommendations."
            )

            if st.button(
                "Generate / Refresh AI Learning Report",
                type="primary",
                width="stretch"
            ):

                with st.spinner(
                    "Analyzing your learning performance..."
                ):

                    try:

                        st.session_state["ai_learning_report"] = (
                            generate_ai_learning_report()
                        )

                    except Exception as error:

                        st.session_state["ai_learning_report"] = None

                        st.error(
                            f"Unable to generate AI report: {error}"
                        )

            if st.session_state.get("ai_learning_report"):

                st.markdown(
                    st.session_state["ai_learning_report"]
                )

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

elif selected_page == "Settings":

    st.title("⚙️ Settings")
    st.write(
        "Customize your AI LearnSphere learning experience."
    )

    preferences = st.session_state.user_preferences.copy()

    st.subheader("🌐 Language Preferences")
    language = "English"

    st.markdown("**Preferred Language:** English")

    st.divider()

    st.subheader("🎓 Learning Preferences")

    learning_level = st.selectbox(
        "Default Learning Level",
        ["Beginner", "Intermediate", "Advanced", "Auto-detect"],
        index=[
            "Beginner",
            "Intermediate",
            "Advanced",
            "Auto-detect"
        ].index(preferences["learning_level"])
    )

    explanation_style = st.selectbox(
        "Default Explanation Style",
        ["Simple", "Detailed", "Both"],
        index=["Simple", "Detailed", "Both"].index(
            preferences["explanation_style"]
        )
    )

    st.divider()

    st.subheader("🤖 AI Model Settings")

    if check_ollama_connection():

        try:

            available_models = get_available_models()

            if available_models:

                selected_model = st.selectbox(
                    "Select Local Ollama Model",
                    available_models,
                    index=(
                        available_models.index(preferences["model"])
                        if preferences["model"] in available_models
                        else 0
                    )
                )

                st.success(
                    f"Ollama connected. {len(available_models)} "
                    "local model(s) available."
                )

            else:

                selected_model = preferences["model"]

                st.warning(
                    "No local Ollama models were found."
                )

        except Exception as error:

            selected_model = preferences["model"]

            st.error(
                f"Unable to load Ollama models: {error}"
            )

    else:

        selected_model = preferences["model"]

        st.warning(
            "Ollama is not running. Start Ollama to select a model."
        )

    st.divider()

    st.subheader("🎨 Appearance")

    theme = st.selectbox(
        "Application Theme",
        ["Light", "Dark"],
        index=["Light", "Dark"].index(
            preferences["theme"]
        )
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save Settings",
            type="primary",
            width="stretch"
        ):

            updated_preferences = {
                "language": language,
                "learning_level": learning_level,
                "explanation_style": explanation_style,
                "model": selected_model,
                "theme": theme
            }

            try:

                save_preferences(updated_preferences)

                st.session_state.user_preferences = (
                    updated_preferences
                )

                st.success(
                    "Your settings have been saved successfully!"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to save settings: {error}"
                )

    with col2:

        if st.button(
            "↩️ Reset Settings",
            width="stretch"
        ):

            try:

                default_preferences = reset_preferences()

                st.session_state.user_preferences = (
                    default_preferences
                )

                st.success(
                    "Settings restored to default values."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to reset settings: {error}"
                )

# --------------------------------------------------
# OTHER MODULE PLACEHOLDERS
# --------------------------------------------------

else:

    st.title(selected_page)

    st.info(
        f"The {selected_page} module will be developed "
        "in its dedicated implementation phase."
    )

    st.write(
        "This section is part of the AI LearnSphere application structure."
    )

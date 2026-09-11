import streamlit as st
import sqlite3
import hashlib
from logic.recommender import recommend_careers
from logic.experiments import get_experiment

def init_database():
    conn = sqlite3.connect("careercompass.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_progress (
            profile_id TEXT PRIMARY KEY,
            name TEXT,
            career TEXT,
            current_day INTEGER,
            experiment_started INTEGER
        )
    """)

    conn.commit()
    conn.close()


init_database()

def save_progress(profile_id, name, career, current_day, experiment_started):
    conn = sqlite3.connect("careercompass.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO student_progress
        (profile_id, name, career, current_day, experiment_started)
        VALUES (?, ?, ?, ?, ?)
    """, (
        profile_id,
        name,
        career,
        current_day,
        int(experiment_started)
    ))

    conn.commit()
    conn.close()

def load_progress(profile_id):
    conn = sqlite3.connect("careercompass.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT career, current_day, experiment_started
        FROM student_progress
        WHERE profile_id = ?
    """, (profile_id,))

    result = cursor.fetchone()

    conn.close()

    return result

def create_profile_id(name, stream, interests, skills, experience):

    profile_data = (
        name.strip().lower()
        + stream
        + "|".join(sorted(interests))
        + "|".join(sorted(skills))
        + experience
    )

    return hashlib.sha256(
        profile_data.encode()
    ).hexdigest()

st.set_page_config(
    page_title="Lorem Ipsum",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Lorem Ipsum")
st.subheader("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

st.write(
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
)

st.divider()

st.header("👤 Tell us about yourself")

name = st.text_input("What should we call you?")

stream = st.selectbox(
    "What was your 12th-grade stream?",
    [
        "Science",
        "Commerce",
        "Humanities",
        "Vocational",
        "Other"
    ]
)

interests = st.multiselect(
    "What are you interested in?",
    [
        "Technology",
        "Business",
        "Design",
        "Science",
        "Finance",
        "Healthcare",
        "Media",
        "Education",
        "Social Impact"
    ]
)

skills = st.multiselect(
    "Which skills do you currently have?",
    [
        "Python",
        "Programming",
        "Communication",
        "Excel",
        "Writing",
        "Graphic Design",
        "Public Speaking",
        "Research",
        "Problem Solving"
    ]
)

experience = st.selectbox(
    "How much practical experience do you have?",
    [
        "No practical experience",
        "Tried a few small projects",
        "Built several personal/academic projects",
        "Completed an internship or work experience"
    ]
)

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

# -----------------------------
# CAREER DISCOVERY
# -----------------------------

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "student" not in st.session_state:
    st.session_state.student = None

if "experiment_started" not in st.session_state:
    st.session_state.experiment_started = False

if "current_day" not in st.session_state:
    st.session_state.current_day = 1


if st.button("🚀 Discover My Career Path"):

    if not name:
        st.warning("Please enter your name.")

    elif not interests:
        st.warning("Choose at least one interest.")

    else:

        student = {
            "name": name,
            "stream": stream,
            "interests": interests,
            "skills": skills,
            "experience": experience
        }

        profile_id = create_profile_id(
            name,
            stream,
            interests,
            skills,
            experience
        )

        recommendations = recommend_careers(student)

        st.session_state.student = student
        st.session_state.recommendations = recommendations

        # Check if this student already has saved progress
        saved_progress = load_progress(profile_id)

        if saved_progress:
            saved_career, saved_day, saved_started = saved_progress

            # Only restore progress if the saved career is one
            # of the careers recommended for this profile
            matching_career = next(
                (
                    career for career in recommendations
                    if career["name"] == saved_career
                ),
                None
            )

            if matching_career:
                st.session_state.current_day = saved_day
                st.session_state.experiment_started = bool(saved_started)

                st.info(
                    f"👋 Welcome back! You're on Day {saved_day} "
                    f"of your {saved_career} experiment."
                )

            else:
                # Saved career doesn't match the new profile
                st.session_state.current_day = 1
                st.session_state.experiment_started = False

        else:
            # Completely new student
            st.session_state.current_day = 1
            st.session_state.experiment_started = False

        # Reset experiment when discovering a new career path
        st.session_state.experiment_started = False
        st.session_state.day_1_complete = False


# -----------------------------
# SHOW RESULTS
# -----------------------------

if st.session_state.recommendations:

    recommendations = st.session_state.recommendations

    student = st.session_state.student

    st.success(f"Welcome, {student['name']}! 🎉")

    st.header("🎯 Your Career Direction")

    # -----------------------------
    # TOP CAREER
    # -----------------------------

    top_career = recommendations[0]

    st.subheader(f"🌟 {top_career['name']}")

    st.write(top_career["description"])

    st.success(
        f"Based on your interests, skills and experience, "
        f"**{top_career['name']}** looks like a strong direction to explore."
    )

    # -----------------------------
    # PATHWAY
    # -----------------------------

    if top_career["pathway"] == "explore":

        st.info(
            "🌱 You're at the exploration stage — and that's completely fine. "
            "We'll help you understand this field before asking you to take on a project."
        )

    elif top_career["pathway"] == "beginner_experiment":

        st.info(
            "🧪 You already have some relevant knowledge. "
            "Let's try a beginner-friendly task and see how you like the work."
        )

    elif top_career["pathway"] == "guided_experiment":

        st.success(
            "🟢 You already have relevant skills. "
            "Let's put them to the test with a guided career experiment."
        )

    elif top_career["pathway"] == "intermediate_experiment":

        st.success(
            "🚀 Your previous projects give you a useful foundation. "
            "You're ready for a more realistic challenge."
        )

    elif top_career["pathway"] == "advanced_challenge":

        st.success(
            "⚡ You have a strong foundation. "
            "You're ready for a more advanced career challenge."
        )

    st.write(
        "**Useful skills for this path:** "
        + ", ".join(top_career["required_skills"])
    )


    # -----------------------------
    # CAREER EXPERIMENT
    # -----------------------------

    experiment = get_experiment(top_career["name"])

    if experiment:

        st.divider()

        st.subheader("🧪 Try this career before you commit")

        st.write(
            f"**{experiment['duration']} experiment:** "
            f"{experiment['goal']}"
        )

        # Beginner orientation
        if top_career["pathway"] == "explore":

            with st.expander("📚 I'm new to this field"):

                st.write(
                    f"**{experiment['orientation']['title']}**"
                )

                st.write(
                    experiment["orientation"]["description"]
                )

                st.write("**Starter activity:**")

                st.info(
                    experiment["orientation"]["starter_activity"]
                )

                st.write("**Beginner resource:**")

                for resource in experiment["orientation"]["resources"]:

                    st.markdown(
                        f"[{resource['title']}]({resource['url']})"
                    )


        # 7-day experiment
        with st.expander("🗓️ See the 7-day experiment"):

            for day, task in enumerate(
                experiment["tasks"],
                start=1
            ):

                st.write(
                    f"**Day {day}:** {task}"
                )


        # -----------------------------
        # START EXPERIMENT
        # -----------------------------

        if not st.session_state.experiment_started:

            if st.button("🚀 Start my experiment"):

                st.session_state.experiment_started = True

                profile_id = create_profile_id(
                    student["name"],
                    student["stream"],
                    student["interests"],
                    student["skills"],
                    student["experience"]
                )

                save_progress(
                    profile_id,
                    student["name"],
                    top_career["name"],
                    st.session_state.current_day,
                    st.session_state.experiment_started
                )

                st.rerun()

        # -----------------------------
        # ACTIVE EXPERIMENT
        # -----------------------------

        if st.session_state.experiment_started:

            st.divider()

            st.subheader("🎯 Your 7-Day Career Experiment")

            st.write(
                "You don't need to be perfect. "
                "The goal is to experience what this career actually feels like."
            )

            current_day = st.session_state.current_day

            # Day heading
            st.subheader(f"🎯 Day {current_day}")

            # Current day's task
            st.info(
                experiment["tasks"][current_day - 1]
            )

            # Complete current day
            if st.button(f"✅ Mark Day {current_day} complete"):

                if current_day < len(experiment["tasks"]):

                    # Move to the next day
                    st.session_state.current_day += 1

                    profile_id = create_profile_id(
                        student["name"],
                        student["stream"],
                        student["interests"],
                        student["skills"],
                        student["experience"]
                    )

                    # Save the new progress
                    save_progress(
                        profile_id,
                        student["name"],
                        top_career["name"],
                        st.session_state.current_day,
                        st.session_state.experiment_started
                    )
                    st.rerun()

                else:

                    profile_id = create_profile_id(
                        student["name"],
                        student["stream"],
                        student["interests"],
                        student["skills"],
                        student["experience"]
                    )

                    # Day 7 completed
                    save_progress(
                        student["name"],
                        top_career["name"],
                        current_day,
                        st.session_state.experiment_started
                    )

                    st.success(
                        "🎉 You completed the entire 7-day experiment!"
                    )


    # -----------------------------
    # OTHER CAREER OPTIONS
    # -----------------------------

    if len(recommendations) > 1:

        st.divider()

        st.subheader("🔎 Other paths worth exploring")

        for career in recommendations[1:3]:

            with st.expander(
                career["name"]
            ):

                st.write(
                    career["description"]
                )

                st.write(
                    "**Useful skills:** "
                    + ", ".join(
                        career["required_skills"]
                    )
                )
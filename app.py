import streamlit as st
import sqlite3
import hashlib
from logic.recommender import recommend_careers
from logic.experiments import get_experiment
from logic.roadmap import CAREER_ROADMAPS

def init_database():
    conn = sqlite3.connect("careercompass.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_progress (
            profile_id TEXT PRIMARY KEY,
            name TEXT,
            career TEXT,
            current_day INTEGER,
            experiment_started INTEGER,
            reflection TEXT
        )
    """)

    conn.commit()
    conn.close()


init_database()

def save_progress(
    profile_id,
    name,
    career,
    current_day,
    experiment_started,
    reflection=""
):
    conn = sqlite3.connect("careercompass.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO student_progress
        (profile_id, name, career, current_day, experiment_started, reflection)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        profile_id,
        name,
        career,
        current_day,
        int(experiment_started),
        reflection
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
    page_title="CareerUp",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# DEVELOPER TEST MODE
# -----------------------------

DEV_MODE = True

st.title("🎓 CareerUp")
st.subheader("The Career Catalyst: Discover Your Path, One Experiment at a Time")

st.write(
    '"Start by doing what is necessary, '
    "then what is possible,"
    'and suddenly you are doing the impossible."'
)

st.divider()

st.header("👤 Start with you")

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

    st.info(
        f"🎯 Based on what you've told us, "
        f"**{top_career['name']}** is a direction worth trying."
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
            f"**{experiment['duration']} experiment**"
        )

        st.write(
            experiment["goal"]
        )

        st.caption(
            "You don't have to know everything beforehand. "
            "The goal is to experience the work and see how it feels."
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
        with st.expander("🗓️ See the full 7-day plan"):

            for day, task in enumerate(
                experiment["tasks"],
                start=1
            ):

                st.write(
                    f"**Day {day}:** {task}"
                )

        # -----------------------------
        # DEVELOPER SHORTCUT
        # -----------------------------

#        if DEV_MODE:

#            if st.button("🛠️ DEV: Jump to Day 7"):

#               st.session_state.experiment_started = True
#                st.session_state.current_day = 7

#                profile_id = create_profile_id(
#                    student["name"],
#                    student["stream"],
#                    student["interests"],
#                    student["skills"],
#                    student["experience"]
#                )

#                save_progress(
#                    profile_id,
#                    student["name"],
#                    top_career["name"],
#                   7,
#                    True
#                )

#                st.rerun()


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

            st.subheader("🧪 Your career experiment")

            st.caption(
                "You don't need to be perfect. "
                "You're here to discover whether you enjoy the work."
            )

            current_day = st.session_state.current_day

            st.divider()

            st.subheader(f"🎯 Day {current_day} of 7")

            st.write("### Today's challenge")

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

                    save_progress(
                        profile_id,
                        student["name"],
                        top_career["name"],
                        st.session_state.current_day,
                        st.session_state.experiment_started
                    )

                    st.rerun()

                else:

                    # Day 7 completed
                    st.session_state.experiment_completed = True

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
                        current_day,
                        st.session_state.experiment_started
                    )

                    st.rerun()

            if st.session_state.get("experiment_completed", False):

                st.divider()

                st.subheader("🎉 You completed your 7-day experiment!")

                st.write(
                    f"You've now had a chance to experience "
                    f"what **{top_career['name']}** is like."
                )

                st.caption(
                    "You didn't have to choose a career — you actually tried one."
                )

                st.subheader("🧠 What did you discover?")

                reflection = st.radio(
                    "How did the experience feel?",
                    [
                        "😍 I really enjoyed it",
                        "🙂 It was interesting",
                        "😐 I'm still unsure",
                        "😕 I didn't enjoy it"
                    ],
                    key="career_reflection"
                )

                next_step = st.radio(
                    "What would you like to do next?",
                    [
                        "🚀 Explore this career further",
                        "📚 Learn the basics first",
                        "🔎 Try another career",
                        "🤷 I'm still figuring it out"
                    ],
                    key="career_next_step"
                )

                if st.button("🎯 Show me my next step"):

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
                        current_day,
                        st.session_state.experiment_started,
                        reflection
                    )

                    st.session_state.reflection_submitted = True

            if st.session_state.get("reflection_submitted", False):

                st.divider()

                st.subheader("🎯 Your next step")

                roadmap = CAREER_ROADMAPS.get(top_career["name"])

                # Student loved the career and wants to explore further
                if (
                    ("really enjoyed" in reflection or "interesting" in reflection)
                    and "Explore" in next_step
                ):

                    st.success(
                        f"🚀 **{top_career['name']} looks worth exploring further!**"
                    )

                    st.write(
                        "You enjoyed the hands-on experience. "
                        "Now let's turn that interest into useful skills."
                    )

                    if roadmap:

                        st.write("### 📚 1. Build your foundation")

                        for resource in roadmap["learn"]:
                            st.markdown(
                                f"**[{resource['title']}]({resource['url']})**"
                            )
                            st.write(resource["description"])

                        st.write("### 🛠️ 2. Build something")

                        st.info(roadmap["project"])

                        st.write("### 💼 3. Move toward opportunities")

                        st.write(roadmap["internship"])

                    else:

                        st.write(
                            "We'll help you find beginner resources, "
                            "projects and opportunities for this career."
                        )

                # Student wants to learn before going further
                elif "Learn the basics" in next_step:

                    st.info(
                        f"📚 **Let's build your foundation in {top_career['name']}.**"
                    )

                    st.write(
                        "You don't need to be job-ready immediately. "
                        "Start with the basics, then gradually move toward projects."
                    )

                    if roadmap:

                        st.write("### Start here")

                        for resource in roadmap["learn"]:
                            st.markdown(
                                f"**[{resource['title']}]({resource['url']})**"
                            )
                            st.write(resource["description"])

                        st.write("### 🛠️ When you're ready")

                        st.info(roadmap["project"])

                    else:

                        st.write(
                            "Start with beginner resources for this career, "
                            "then move toward a small practical project."
                        )

                # Student wants another career
                elif "another career" in next_step:

                    st.info(
                        "🔎 **Let's explore another direction.**"
                    )

                    st.write(
                        "Trying a career and discovering that you want "
                        "something different is valuable information."
                    )

                    st.write(
                        "Your next step is to return to your career recommendations "
                        "and try another path."
                    )

                # Student is still unsure
                elif "still figuring" in next_step or "still unsure" in reflection:

                    st.info(
                        "🤔 **You're still figuring it out — and that's okay.**"
                    )

                    st.write(
                        "Seven days doesn't have to decide your career. "
                        "The goal is to learn more about yourself and your options."
                    )

                    st.write("### What we recommend")

                    st.write("🔎 Explore a related career")
                    st.write("🧪 Try another short experiment")
                    st.write("🧭 Compare what you enjoyed in each experience")

                # Student didn't enjoy the career
                elif "didn't enjoy" in reflection:

                    st.info(
                        "🔄 **This career might not be the right fit — "
                        "and that's useful information.**"
                    )

                    st.write(
                        "You just learned something important about "
                        "the kind of work you may not enjoy."
                    )

                    st.write("### Your next move")

                    st.write("🔎 Explore another career")
                    st.write("🧪 Try another experiment")
                    st.write("🎯 Compare your experiences before deciding")


    # -----------------------------
    # OTHER CAREER OPTIONS
    # -----------------------------

    if len(recommendations) > 1:

        st.divider()

        st.subheader("🔎 Other paths you could try")

        st.caption(
            "These are alternatives worth considering based on your profile."
        )

        for career in recommendations[1:3]:

            with st.expander(
                career["name"]
            ):

                st.write(
                    career["description"]
                )

                st.write(
                    "**Skills you could build:** "
                    + ", ".join(
                        career["required_skills"]
                    )
                )
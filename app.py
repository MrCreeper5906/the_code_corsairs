import streamlit as st
from logic.recommender import recommend_careers

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
        "None yet",
        "A little",
        "Some projects",
        "Previous internship/work experience"
    ]
)

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

        recommendations = recommend_careers(student)

        st.success(f"Welcome, {name}! 🎉")

        st.header("🎯 Your Career Matches")

        for index, career in enumerate(recommendations[:3]):

            st.subheader(
                f"{index + 1}. {career['name']} — {career['score']}% match"
            )

            st.write(career["description"])

            st.write(
                "**Skills you'll need:** "
                + ", ".join(career["required_skills"])
            )

            st.progress(career["score"] / 100)

            st.divider()
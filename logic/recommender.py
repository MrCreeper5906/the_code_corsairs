import json


def load_careers():
    with open("data/careers.json", "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_match(student, career):
    score = 0

    # Stream compatibility
    if student["stream"] in career["streams"]:
        score += 25

    # Interest matching
    matching_interests = (
        set(student["interests"]) & set(career["interests"])
    )
    score += len(matching_interests) * 15

    # Skill matching
    matching_skills = (
        set(student["skills"]) & set(career["skills"])
    )
    score += len(matching_skills) * 10

    return min(score, 100)


def calculate_readiness(student, career):
    required_skills = set(career["required_skills"])
    student_skills = set(student["skills"])

    if not required_skills:
        return 0

    matching_skills = required_skills & student_skills

    skill_readiness = (
        len(matching_skills) / len(required_skills)
    ) * 100

    return round(skill_readiness)


def get_experience_level(experience):
    experience_levels = {
        "No practical experience": 0,
        "Tried a few small projects": 1,
        "Built several personal/academic projects": 2,
        "Completed an internship or work experience": 3
    }

    return experience_levels.get(experience, 0)


def determine_pathway(readiness, experience_level):

    if readiness < 34 and experience_level == 0:
        return "explore"

    elif readiness < 67 and experience_level <= 1:
        return "beginner_experiment"

    elif readiness >= 67 and experience_level <= 1:
        return "guided_experiment"

    elif readiness < 67 and experience_level >= 2:
        return "intermediate_experiment"

    else:
        return "advanced_challenge"


def recommend_careers(student):
    careers = load_careers()

    results = []

    experience_level = get_experience_level(
        student["experience"]
    )

    for career in careers:

        match_score = calculate_match(
            student,
            career
        )

        readiness = calculate_readiness(
            student,
            career
        )

        pathway = determine_pathway(
            readiness,
            experience_level
        )

        results.append({
            "name": career["name"],
            "description": career["description"],
            "score": match_score,
            "readiness": readiness,
            "experience_level": experience_level,
            "pathway": pathway,
            "required_skills": career["required_skills"]
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results
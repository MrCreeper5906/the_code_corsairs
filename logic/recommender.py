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
    matching_interests = set(student["interests"]) & set(career["interests"])
    score += len(matching_interests) * 15

    # Skill matching
    matching_skills = set(student["skills"]) & set(career["skills"])
    score += len(matching_skills) * 10

    return min(score, 100)


def recommend_careers(student):
    careers = load_careers()

    results = []

    for career in careers:
        score = calculate_match(student, career)

        results.append({
            "name": career["name"],
            "description": career["description"],
            "score": score,
            "required_skills": career["required_skills"]
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results
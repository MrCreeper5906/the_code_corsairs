import json


def load_experiments():
    with open("data/experiments.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_experiment(career_name):
    experiments = load_experiments()

    for experiment in experiments:
        if experiment["career"] == career_name:
            return experiment

    return None
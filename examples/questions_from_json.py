from pprint import pprint

import inquirer  # noqa

with open("examples/test_questions.json", "rb") as fd:
    questions = inquirer.load_from_json(fd.read())  # type: ignore

answers = inquirer.prompt(questions)  # type: ignore

pprint(answers)

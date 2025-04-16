import numpy as np
import pandas as pd
import csv
import os

from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
MISTAKES_CSV_PATH = os.path.join(script_dir, "mistakes.csv")
ORIGINAL_QUIZ_CSV_PATH = os.path.join(script_dir, "Combined_Quizzes.csv")



def generate_random_quiz(df, num_questions=20):
    selected_questions = df

    if num_questions <= len(df):
        # Randomly select questions
        selected_questions = df.sample(n=num_questions)

    questions = selected_questions["Question"].tolist()
    answers = selected_questions["Answer"].tolist()
    explanations = selected_questions["Explanations"].tolist()
    return questions, answers, explanations

def generate_chosen_quiz(df, choice):
    if choice < 1 or choice > 7:
        print("Invalid choice. Exiting.")
        exit(1)

    match str(choice):
        case "1":
            interval = (0, 44)
        case "2":
            interval = (44, 98)
        case "3":
            interval = (98, 148)
        case "4":
            interval = (148, 169)
        case "5":
            interval = (169, 188)
        case "6":
            interval = (188, 223)
        case "7":
            interval = (223, 228)
        case _:
            pass
    
    if choice == 5 or choice == 7:
        selected_questions = df[interval[0]:interval[1]]
        questions = selected_questions["Question"].tolist()
        answers = selected_questions["Answer"].tolist()
        explanations = selected_questions["Explanations"].tolist()
    else:
        questions, answers, explanations = generate_random_quiz(df[interval[0]:interval[1]], 20)
    
    return questions, answers, explanations

def normalize_answer(ans):
    if pd.isna(ans):
        return set()  # treat missing answers as empty
    # Convert to string, lower it, replace '&' and 'and' with ','
    ans = str(ans).lower().replace("&", ",").replace("and", ",").replace(")", "")
    # Split and strip each item
    items = [item.strip() for item in ans.split(",") if item.strip()]
    return set(items)


def is_correct(correct_ans, submitted_ans):
    return normalize_answer(correct_ans) == normalize_answer(submitted_ans)


def ask_questions(questions, answers, explanations):
    score = 0

    mistakes = []
    correct_questions = []

    for i, question in enumerate(questions):
        print(
            Style.BRIGHT
            + Fore.YELLOW
            + "------------------------------------------------------------"
        )
        print(Style.BRIGHT + Fore.YELLOW + f"Question {i + 1}:")
        print(Style.BRIGHT + f"{question}")
        print()
        user_answer = input(Fore.WHITE + "Your answer: ")
        if is_correct( answers[i], user_answer):
            print(Style.BRIGHT + Fore.GREEN + "Correct!")
            score += 1
            correct_questions.append(question)
        else:
            print(
                Style.BRIGHT
                + Fore.RED
                + f"Incorrect. {Fore.WHITE} The correct answer is: {answers[i]}"
            )
            print(f"Explanation: {explanations[i]}")
            mistakes.append(
                {
                    "Question": question,
                    "Answer": answers[i],
                    "Explanations": explanations[i],
                }
            )
        print()
    return score, mistakes, correct_questions


def write_questions_to_csv(questions, filepath):
    # Load existing rows
    try:
        with open(filepath, "r", newline="") as file:
            reader = csv.DictReader(file)
            existing_rows = list(reader)
    except FileNotFoundError:
        existing_rows = []
    # Avoid duplicates
    new_rows = []
    for entry in questions:
        if entry not in existing_rows:
            new_rows.append(entry)
    # Write to CSV
    if new_rows:
        with open(filepath, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=new_rows[0].keys())
            if not existing_rows:
                writer.writeheader()
            writer.writerows(new_rows)


def get_quiz_df(path_to_quiz=ORIGINAL_QUIZ_CSV_PATH):

    # Load the CSV file
    try:
        df = pd.read_csv(path_to_quiz)
    except FileNotFoundError:
        print(Style.BRIGHT + Fore.RED + f"File {path_to_quiz} not found.")
        exit(1)

    return df

def delete_from_csv_with_questions(questions, filepath):
    # Read the existing data
    with open(filepath, 'r', newline='') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader if row['Question'] not in map(str, questions)]

    # Write back the filtered rows to the CSV
    with open(filepath, 'w', newline='') as file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# TODO: refactor by adding context manager
if __name__ == "__main__":

    review = False
    review_mistakes = input(
        Fore.YELLOW
        + "Do you want to review your mistakes? [y/N]: "
    ).strip().lower()

    if review_mistakes == "y":
        df = get_quiz_df(MISTAKES_CSV_PATH)
        review = True

        num_questions = int(input("Number of questions (default is 20): ") or 20)
        questions, answers, explanations = generate_random_quiz(df, num_questions)

    else:
        df = get_quiz_df(ORIGINAL_QUIZ_CSV_PATH)
    
        random = input(Fore.YELLOW + "Random? [Y/n]: ").strip().lower()

        if random == "n":
            print("CHOICES:")
            print("1. Overview and Applications")
            print("2. Data Collection & Engineering")
            print("3. DataOps and DSP")
            print("4. DSP #2")
            print("5. Feature Extraction")
            print("6. Feature Extraction and Basic Learning")
            print("7. Stat Tests")
            choice = int(input("Choose a quiz (1-7): "))
            
            questions, answers, explanations = generate_chosen_quiz(df, choice)
        
        else:
            num_questions = int(input("Number of questions (default is 20): ") or 20)
            questions, answers, explanations = generate_random_quiz(df, num_questions)

    score, mistakes, correct_questions = ask_questions(questions, answers, explanations)

    write_questions_to_csv(mistakes, MISTAKES_CSV_PATH)

    print(Style.BRIGHT + f"Your score: {score}/{len(questions)}")
    if not review:
        print(f"Writing mistakes to {MISTAKES_CSV_PATH}")
    else:
        delete = input(
            Fore.YELLOW
            + "Do you want to delete the correct questions from the mistakes CSV? [y/N]: "
        ).strip().lower()
        if delete == "y":
            print(f"Deleting correct questions from {MISTAKES_CSV_PATH}")
            # Remove correct questions from the mistakes CSV
            delete_from_csv_with_questions(correct_questions, MISTAKES_CSV_PATH)



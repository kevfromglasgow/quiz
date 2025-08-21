import streamlit as st
import requests
import random
import html

# --- CONFIGURATION ---
# The Trivia API endpoint
API_URL = "https://the-trivia-api.com/v2/questions"

# Dictionary of available sports categories from the API
# You can add or remove sports here
SPORTS_CATEGORIES = {
    "Football": "sport_and_leisure",
    "Basketball": "sport_and_leisure",
    "Baseball": "sport_and_leisure",
    "Soccer": "sport_and_leisure",
    "Hockey": "sport_and_leisure",
    "Tennis": "sport_and_leisure",
    "Golf": "sport_and_leisure",
    "Boxing": "sport_and_leisure",
    "MMA": "sport_and_leisure",
    "Motorsport": "sport_and_leisure",
}

# --- HELPER FUNCTIONS ---

def fetch_quiz_questions(categories, difficulty, limit):
    """
    Fetches quiz questions from The Trivia API based on user selections.
    """
    params = {
        "limit": limit,
        "categories": ",".join(categories),
        "difficulties": difficulty,
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        questions = response.json()
        return questions
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching questions from the API: {e}")
        return []
    except ValueError:
        st.error("Failed to decode the API response. The API might be temporarily down.")
        return []

def display_question(question_data, question_number):
    """
    Displays a single quiz question, including any images and answer options.
    """
    st.subheader(f"Question {question_number}:")
    # The API returns HTML-encoded strings, so we decode them
    question_text = html.unescape(question_data["question"]['text'])
    st.write(question_text)

    # Check if there's an image URL and display it
    # Note: The Trivia API does not consistently provide image URLs.
    # This is here for when it does.
    if "image" in question_data and question_data["image"]:
        st.image(question_data["image"], use_column_width=True)

    # Combine correct and incorrect answers and shuffle them
    options = question_data["incorrectAnswers"] + [question_data["correctAnswer"]]
    random.shuffle(options)

    # Decode HTML entities in options
    decoded_options = [html.unescape(opt) for opt in options]

    # Use a radio button for user's answer selection
    user_answer = st.radio("Select your answer:", decoded_options, key=f"q_{question_number}")
    return user_answer, html.unescape(question_data["correctAnswer"])

def initialize_session_state():
    """
    Initializes the session state variables if they don't exist.
    """
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

# --- UI LAYOUT ---

st.set_page_config(page_title="Sports Quiz Challenge", layout="wide")

# Initialize session state
initialize_session_state()

# Title of the app
st.title("Sports Quiz Challenge 🏆")

# --- SIDEBAR FOR QUIZ CONFIGURATION ---
with st.sidebar:
    st.header("Quiz Settings")

    # Sports category selection
    selected_sports = st.multiselect(
        "Choose your sports categories:",
        options=list(SPORTS_CATEGORIES.keys()),
        default=list(SPORTS_CATEGORIES.keys())[0] if SPORTS_CATEGORIES else []
    )

    # Difficulty selection
    difficulty = st.radio(
        "Select difficulty:",
        options=["easy", "medium", "hard"],
        index=1 # Default to medium
    )

    # Number of questions selection
    num_questions = st.number_input(
        "Number of questions:",
        min_value=5,
        max_value=20,
        value=10,
        step=1
    )

    # Start Quiz Button
    if st.button("Start Quiz", type="primary"):
        if not selected_sports:
            st.warning("Please select at least one sports category.")
        else:
            # Get the corresponding API category names for the selected sports
            api_categories = [SPORTS_CATEGORIES[sport] for sport in selected_sports]
            # Fetch new questions and reset the quiz state
            st.session_state.questions = fetch_quiz_questions(api_categories, difficulty, num_questions)
            if st.session_state.questions:
                st.session_state.quiz_started = True
                st.session_state.score = 0
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.rerun() # Rerun the script to start the quiz immediately
    
    # Add some information at the bottom of the sidebar
    st.markdown("---")
    st.info("Powered by [The Trivia API](https://the-trivia-api.com/) and Streamlit.")


# --- MAIN QUIZ AREA ---

if not st.session_state.quiz_started:
    st.info("Welcome to the Sports Quiz Challenge! Adjust the settings on the left and click 'Start Quiz' to begin.")

elif st.session_state.questions:
    # Display the quiz progress
    progress_text = f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}"
    st.progress((st.session_state.current_question + 1) / len(st.session_state.questions), text=progress_text)
    st.markdown("---")


    # Get the current question data
    current_q_data = st.session_state.questions[st.session_state.current_question]

    # Display the question and get the user's answer
    user_answer, correct_answer = display_question(current_q_data, st.session_state.current_question + 1)

    # Submit Answer Button
    if st.button("Submit Answer", key=f"submit_{st.session_state.current_question}"):
        # Store the user's answer and the correct answer
        st.session_state.user_answers[st.session_state.current_question] = {
            "user_choice": user_answer,
            "correct_answer": correct_answer
        }

        # Check if the answer is correct and update the score
        if user_answer == correct_answer:
            st.session_state.score += 1
            st.success("Correct! 🎉")
        else:
            st.error(f"Incorrect. The correct answer was: **{correct_answer}**")

        # Move to the next question
        st.session_state.current_question += 1
        
        # A short delay before showing the next question
        import time
        time.sleep(1.5)
        
        # If it's the last question, end the quiz, otherwise rerun for the next question
        if st.session_state.current_question >= len(st.session_state.questions):
            st.session_state.quiz_started = False # Mark quiz as finished
        
        st.rerun()

# --- QUIZ RESULTS ---
# This block runs when the quiz is over
if not st.session_state.quiz_started and st.session_state.user_answers:
    st.balloons()
    st.header("Quiz Over!")
    st.subheader(f"Your Final Score: {st.session_state.score} / {len(st.session_state.questions)}")
    st.markdown("---")

    # Display a review of all questions and answers
    st.header("Review Your Answers:")
    for i, q_data in enumerate(st.session_state.questions):
        review = st.session_state.user_answers.get(i)
        if review:
            with st.container():
                st.write(f"**Question {i+1}:** {html.unescape(q_data['question']['text'])}")
                if review['user_choice'] == review['correct_answer']:
                    st.success(f"Your answer: {review['user_choice']} (Correct)")
                else:
                    st.error(f"Your answer: {review['user_choice']} (Incorrect)")
                    st.info(f"Correct answer: {review['correct_answer']}")
                st.markdown("---")

    # Play Again Button
    if st.button("Play Again", type="primary"):
        # Reset all state variables to start fresh
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()


import streamlit as st
import re
import openai
from backend import (
    get_llm_tech_questions,
    get_llm_assignment,
    initialize_client,
    conversation_end,
)

# Import prompts if needed for local usage
from prompts import generate_tech_questions_prompt, generate_assignment_prompt

# Securely load the OpenAI API key from secrets
api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.error("❌ OpenAI API key not found. Please add it to `.streamlit/secrets.toml`.")
    st.stop()

# Initialize OpenAI client for backend usage
initialize_client(api_key)

st.set_page_config(
    page_title="TalentScout Hiring Assistant 🤖",
    page_icon="🤖",
    layout="centered",
)

st.markdown("<h1 style='text-align:center;'>TalentScout Hiring Assistant 🤖</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:gray;'>Smart AI Screening and Assignment generation</p>",
    unsafe_allow_html=True,
)

# Candidate info steps, now including category selection
steps = [
    ("What is your full name?", "name"),
    ("Your email address?", "email"),
    ("Your phone number?", "phone"),
    ("How many years of professional experience do you have?", "experience"),
    ("Which position(s) are you interested in?", "position"),
    ("Where are you currently located?", "location"),
    ("List your tech stack (comma-separated, e.g., Python, React, SQL):", "tech_stack"),
    ("Select categories you are interested in assignments for:", "categories"),
]

categories_options = [
    "Backend Development",
    "Frontend Development",
    "Data Science",
    "DevOps",
    "Mobile Development",
    "Machine Learning",
    "Cloud Computing"
]

end_keywords = ["quit", "exit", "bye", "cancel", "end"]

# Initialize session state on first run
if "state" not in st.session_state:
    st.session_state.state = {
        "step": 0,
        "candidate_info": {},
        "tech_questions": [],
        "assignments": [],
        "ended": False,
        "finished": False,
        "message": "",
    }

# Validation functions
def is_valid_email(email: str):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

def is_valid_phone(phone: str):
    digits_only = re.sub(r"\D", "", phone)
    return 7 <= len(digits_only) <= 15

def is_valid_experience(exp: str):
    try:
        return int(exp) >= 0
    except:
        return False

def check_convo_end(text: str):
    return any(keyword in text.lower() for keyword in end_keywords)

def progress_bar(step: int, total: int):
    percent = int((step / total) * 100)
    st.markdown(
        f"""
        <div style='width:100%;background:#e0e0e0;border-radius:15px;height:15px;'>
          <div style='width:{percent}%;background:#4A90E2;height:15px;border-radius:15px;'></div>
        </div>
        <p style='text-align:right;font-weight:bold;margin-top:5px;'>{percent}% Complete</p>
        """,
        unsafe_allow_html=True,
    )

def render_input(question, key, hint="", value=""):
    st.markdown(f"### {question}")
    return st.text_input("", key=key, value=value, placeholder=hint)

def render_multiselect(question, key, options, default=[]):
    st.markdown(f"### {question}")
    return st.multiselect("", options, default=default, key=key)

# Main conversation flow
def main():
    total_steps = len(steps)
    current_step = st.session_state.state["step"]

    progress_bar(current_step, total_steps)

    if not st.session_state.state["ended"] and not st.session_state.state["finished"]:
        if current_step < total_steps:
            question, key = steps[current_step]
            stored_value = st.session_state.state["candidate_info"].get(key, "")

            if key == "categories":
                user_input = render_multiselect(question, key, categories_options, default=stored_value if isinstance(stored_value, list) else [])
            else:
                user_input = render_input(question, key, value=stored_value)

            if st.button("Next", key=f"next_{key}"):
                # Check for exit keywords
                if isinstance(user_input, str) and check_convo_end(user_input):
                    st.session_state.state["ended"] = True
                    st.session_state.state["message"] = conversation_end()
                    st.experimental_rerun()
                    return

                # Input validations
                error_msg = ""

                if key == "email" and not is_valid_email(user_input):
                    error_msg = "Please enter a valid email address."
                elif key == "phone" and not is_valid_phone(user_input):
                    error_msg = "Please enter a valid phone number."
                elif key == "experience" and not is_valid_experience(user_input):
                    error_msg = "Please enter valid years of experience (non-negative integer)."
                elif key == "tech_stack" and len([t.strip() for t in user_input.split(",") if t.strip()]) == 0:
                    error_msg = "Please specify at least one technology in your tech stack."
                elif key == "categories" and (not isinstance(user_input, list) or len(user_input) == 0):
                    error_msg = "Please select at least one category."

                if error_msg:
                    st.error(error_msg)
                else:
                    st.session_state.state["candidate_info"][key] = user_input
                    st.session_state.state["step"] += 1
                    st.experimental_rerun()

        else:
            # All steps done, generate questions and assignments
            st.info("Generating your personalized technical questions and assignments, please wait...")

            tech_stack_str = st.session_state.state["candidate_info"].get("tech_stack", "")
            years_exp = st.session_state.state["candidate_info"].get("experience", "2")
            categories = st.session_state.state["candidate_info"].get("categories", [])

            tech_list = [t.strip() for t in tech_stack_str.split(",") if t.strip()]
            all_questions = []
            all_assignments = []

            # Generate technical questions for each tech item
            for tech in tech_list:
                q_list = get_llm_tech_questions(tech, years_exp)
                st.markdown(f"### {tech} Interview Questions")
                for q in q_list:
                    st.write(f"- {q}")
                all_questions.extend(q_list)

            # Generate assignments for selected categories
            for category in categories:
                assignment_text = get_llm_assignment(category)
                st.markdown(f"### Assignment Task: {category}")
                st.write(assignment_text)
                all_assignments.append({"category": category, "assignment": assignment_text})

            st.session_state.state["tech_questions"] = all_questions
            st.session_state.state["assignments"] = all_assignments
            st.session_state.state["finished"] = True
            st.success(conversation_end())

    elif st.session_state.state["ended"]:
        st.success(st.session_state.state.get("message", conversation_end()))

    elif st.session_state.state["finished"]:
        st.success(conversation_end())
        if st.session_state.state.get("tech_questions"):
            st.markdown("### Your Technical Questions")
            for question in st.session_state.state["tech_questions"]:
                st.write(f"- {question}")
        if st.session_state.state.get("assignments"):
            st.markdown("### Your Assignments")
            for assignment in st.session_state.state["assignments"]:
                st.markdown(f"**{assignment['category']}**: {assignment['assignment']}")

if __name__ == "__main__":
    main()

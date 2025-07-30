import openai
from prompts import generate_tech_questions_prompt, generate_assignment_prompt

# Initialize OpenAI client globally to reuse
client = None

def initialize_client(api_key):
    global client
    client = openai.OpenAI(api_key=api_key)

def get_llm_tech_questions(tech, years):
    prompt = generate_tech_questions_prompt(tech, years)
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
            n=1,
        )
        content = completion.choices[0].message.content
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        # Strip numbering from questions
        questions = [line.lstrip('1234567890. ').strip() for line in lines]
        return questions if questions else [content]
    except Exception as e:
        return [f"Error generating questions for {tech}: {str(e)}"]

def get_llm_assignment(category):
    prompt = generate_assignment_prompt(category)
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=350,
            temperature=0.3,
            n=1,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating assignment for {category}: {str(e)}"

def conversation_end():
    return (
        "Thank you for chatting with TalentScout! We'll review your information, "
        "your technical questions, and assignment, then contact you regarding the next steps."
    )

def generate_tech_questions_prompt(tech, years):
    return (
        f"You are a senior technical interviewer. "
        f"Generate 3 technical interview questions to assess a candidate's proficiency in {tech}. "
        f"The candidate has {years} years of professional experience. "
        f"Return only the questions, numbered."
    )

def generate_assignment_prompt(category):
    return (
        f"You are an expert task designer for technical hiring. "
        f"Please create one challenging and practical coding or project assignment suitable for evaluating a candidate in {category}. "
        f"Keep it concise, about 2-3 sentences."
    )

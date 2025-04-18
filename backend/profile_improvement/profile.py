import openai
import os

# Set your API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_improvement_suggestions(profile_text: str, job_description: str) -> str:
    system_prompt = (
        "You are an expert career coach helping candidates improve their profiles to better match job descriptions. "
        "Given a candidate's profile and the job description, suggest improvements they can make to their resume, GitHub, "
        "skills, or experience to increase their chances of getting selected for an interview. "
        "Provide your feedback in the form of bullet points."
    )

    user_prompt = f"""
Candidate Profile:
{profile_text}

Job Description:
{job_description}

Please provide concise, actionable suggestions in bullet points.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error generating suggestions: {str(e)}"

# --- Example usage ---
if __name__ == "__main__":
    profile = """
    Jane Doe is a junior web developer with 1.5 years of experience. She's skilled in HTML, CSS, and JavaScript. 
    Her GitHub includes a few frontend projects. She holds a Bachelor’s degree in Computer Science.
    """

    job = """
    We are seeking a mid-level full-stack developer with 3+ years of experience in React, Node.js, and AWS.
    Familiarity with CI/CD pipelines and Docker is required.
    """

    suggestions = generate_improvement_suggestions(profile, job)
    print("=== Profile Improvement Suggestions ===")
    print(suggestions)

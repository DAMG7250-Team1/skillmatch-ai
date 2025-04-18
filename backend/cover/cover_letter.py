# 


from openai import OpenAI
from datetime import datetime

class CoverProfileAgent:
    """
    Agent for generating cover letters and profile improvement suggestions
    using OpenAI's chat completions API.
    """
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the agent with specific model and temperature.
        Ensure OPENAI_API_KEY is set in environment.
        """
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature

    def generate_cover_letter(self, profile: str, job_description: str) -> str:
        """
        Generate a personalized cover letter based on the candidate profile and job description.
        Returns the cover letter text.
        """
        prompt = f"""
            Generate a personalized cover letter using this candidate profile and job description.
            Highlight the candidate's skills and achievements, and explain why they're a perfect fit.

            Candidate Profile:
            {profile}

            Job Description:
            {job_description}

            Format with clear introduction, body, and closing. Use professional business letter format.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def generate_improvement_suggestions(self, profile: str, job_description: str) -> str:
        """
        Generate actionable improvement suggestions for a candidate profile
        given the job description. Returns a bullet list.
        """
        prompt = f"""
            Provide actionable recommendations to improve this candidate's profile for the target job.

            Candidate Profile:
            {profile}

            Job Description:
            {job_description}

            Format as a bullet list with concise, specific suggestions.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "You are an expert career advisor."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def generate_all(self, profile: str, job_description: str) -> dict:
        """
        Run both cover letter generation and improvement suggestions.
        Returns a dict with keys 'cover_letter' and 'improvement_suggestions'.
        """
        cover_letter = self.generate_cover_letter(profile, job_description)
        feedback = self.generate_improvement_suggestions(profile, job_description)
        return {
            "cover_letter": cover_letter,
            "improvement_suggestions": feedback
        }

# Example usage:
if __name__ == "__main__":
    agent = CoverProfileAgent()
    candidate_profile = """
    John Doe is a software engineer with 5 years of experience in full-stack development.
    He is skilled in Python, JavaScript, and has a strong background in cloud-based application design.
    """
    job_description = """
    We are seeking a Senior Software Engineer with a focus on building high-performance web applications.
    The ideal candidate should have experience in Python, cloud technologies, and microservices architecture.
    """
    result = agent.generate_all(candidate_profile, job_description)
    print("--- Cover Letter ---")
    print(result["cover_letter"])
    print("\n--- Improvement Suggestions ---")
    print(result["improvement_suggestions"])

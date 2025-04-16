from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Define the prompt template for generating profile improvement suggestions.
profile_improvement_template = """
You are an expert career advisor. Given the candidate's profile and the job description provided, generate a concise bullet list of actionable recommendations 
on how the candidate can improve their profile to become more suitable for the position.

Candidate Profile:
{profile}

Job Description:
{job_description}

Provide your answer as a bullet list of suggestions.
"""

# Create a PromptTemplate instance.
profile_improvement_prompt = PromptTemplate(
    input_variables=["profile", "job_description"],
    template=profile_improvement_template
)

# Initialize the LLM (here we use OpenAI's GPT-3.5-turbo model; set your desired parameters).
llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

# Create the LLMChain for profile improvement.
profile_improvement_chain = LLMChain(
    llm=llm, 
    prompt=profile_improvement_prompt, 
    output_key="improvement_suggestions"
)

def generate_improvement_suggestions(profile: str, job_description: str) -> str:
    """
    Given a candidate's profile and a job description, 
    generate a bullet list of improvement suggestions.
    """
    inputs = {"profile": profile, "job_description": job_description}
    result = profile_improvement_chain.run(inputs)
    return result

# --- Example usage ---
if __name__ == "__main__":
    candidate_profile = """
    John Doe is a software engineer with 5 years of experience in full-stack development.
    He is skilled in Python, JavaScript, and has a strong background in cloud-based application design.
    He has successfully led projects at mid-sized tech companies and is passionate about building scalable systems.
    """
    job_description = """
    We are seeking a Senior Software Engineer with a focus on building high-performance web applications.
    The ideal candidate should have experience in Python, cloud technologies, and microservices architecture.
    Leadership skills and experience in project management are highly valued.
    """
    
    suggestions = generate_improvement_suggestions(candidate_profile, job_description)
    print("Profile Improvement Suggestions:")
    print(suggestions)

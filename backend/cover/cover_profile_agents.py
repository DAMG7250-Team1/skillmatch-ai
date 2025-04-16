# cover_profile_agents.py

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# Note: if using langgraph, ensure it’s installed and import its Graph class.
# For simplicity, we simulate a basic graph orchestration below.
# You can install langgraph via pip if you wish to use more sophisticated orchestration.

try:
    from langgraph import Graph
except ImportError:
    # If langgraph is not installed, we simulate a graph with a simple dictionary.
    class Graph:
        def __init__(self):
            self.nodes = {}
        def add_node(self, name, chain):
            self.nodes[name] = chain
            return name
        def add_edge(self, from_node, to_node):
            # For this simple example, edges are not used for control flow.
            pass
        def run_all(self, inputs):
            results = {}
            for name, chain in self.nodes.items():
                results[name] = chain.run(inputs)
            return results

# --- Define the Cover Letter Generation Agent ---

cover_letter_template = """
You are a professional cover letter writer. Given the following candidate profile and job description, generate a personalized cover letter that highlights the candidate's skills and achievements and explains why they are a perfect fit for the job.

Candidate Profile:
{profile}

Job Description:
{job_description}

Please format the answer as a cover letter with a clear introduction, body, and closing.
"""

cover_letter_prompt = PromptTemplate(
    input_variables=["profile", "job_description"],
    template=cover_letter_template
)

# --- Define the Profile Improvement Agent ---

profile_improvement_template = """
You are an expert career advisor. Given the candidate's profile and the job description provided, generate a concise bullet list of actionable recommendations 
on how the candidate can improve their profile to become more suitable for the position.

Candidate Profile:
{profile}

Job Description:
{job_description}

Provide your answer as a bullet list of suggestions.
"""

profile_improvement_prompt = PromptTemplate(
    input_variables=["profile", "job_description"],
    template=profile_improvement_template
)

# --- Initialize the LLM (for example, using OpenAI) ---

llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

# --- Create two LLMChains, one for each agent ---
cover_letter_chain = LLMChain(llm=llm, prompt=cover_letter_prompt, output_key="cover_letter")
profile_improvement_chain = LLMChain(llm=llm, prompt=profile_improvement_prompt, output_key="improvement_suggestions")

# --- (Optional) Build a simple LangGraph for orchestration ---
graph = Graph()
cover_letter_node = graph.add_node("CoverLetterAgent", chain=cover_letter_chain)
improvement_node = graph.add_node("ProfileImprovementAgent", chain=profile_improvement_chain)
# Here we add an edge if we want to simulate a workflow—this example runs both independently.
graph.add_edge(cover_letter_node, improvement_node)

# --- Define a function to run both agents ---
def generate_cover_letter_and_improvements(profile: str, job_description: str) -> dict:
    # Input dictionary for both chains
    inputs = {"profile": profile, "job_description": job_description}
    
    # Option 1: Run each chain separately (simple approach)
    cover_letter_result = cover_letter_chain.run(inputs)
    improvement_result = profile_improvement_chain.run(inputs)
    
    # Option 2: If using langgraph, you might run:
    # results = graph.run_all(inputs)
    # cover_letter_result = results.get("CoverLetterAgent")
    # improvement_result = results.get("ProfileImprovementAgent")
    
    return {
        "cover_letter": cover_letter_result,
        "improvement_suggestions": improvement_result
    }

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
    
    results = generate_cover_letter_and_improvements(candidate_profile, job_description)
    print("Generated Cover Letter:\n")
    print(results["cover_letter"])
    print("\nProfile Improvement Suggestions:\n")
    print(results["improvement_suggestions"])

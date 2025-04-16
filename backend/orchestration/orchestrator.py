# orchestrator.py

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Try importing LangGraph. If not available, we simulate a simple graph.
try:
    from langgraph import Graph
except ImportError:
    # Simulate a graph with a basic dictionary of nodes.
    class Graph:
        def __init__(self):
            self.nodes = {}
        def add_node(self, name, chain):
            self.nodes[name] = chain
            return name
        def add_edge(self, from_node, to_node):
            # In this simple simulation, edges are not used
            pass
        def run_all(self, inputs):
            results = {}
            for name, chain in self.nodes.items():
                results[name] = chain.run(inputs)
            return results

# --- Define prompt templates for each agent ---

# Cover Letter Agent: Generates a cover letter based on candidate profile and job description.
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

# Profile Improvement Agent: Provides actionable recommendations to improve the candidate profile.
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

# --- Initialize the LLM ---
# Adjust temperature or model_name parameters as needed.
llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

# --- Create LLMChain instances for each agent ---
cover_letter_chain = LLMChain(
    llm=llm, 
    prompt=cover_letter_prompt, 
    output_key="cover_letter"
)

profile_improvement_chain = LLMChain(
    llm=llm, 
    prompt=profile_improvement_prompt, 
    output_key="improvement_suggestions"
)

# --- Build the orchestration graph ---
graph = Graph()
cover_letter_node = graph.add_node("CoverLetterAgent", chain=cover_letter_chain)
improvement_node = graph.add_node("ProfileImprovementAgent", chain=profile_improvement_chain)

# Optionally add edges if you want to express a workflow order.
graph.add_edge(cover_letter_node, improvement_node)

# --- Define function to run the orchestration graph ---
def run_agents(profile: str, job_description: str) -> dict:
    """
    Run both the cover letter and profile improvement agents in parallel.
    Returns a dictionary with cover letter and improvement suggestions.
    """
    inputs = {"profile": profile, "job_description": job_description}
    
    # Option 1: Use the graph to run all nodes
    results = graph.run_all(inputs)
    
    # Alternatively, you can call each chain directly:
    # cover_letter = cover_letter_chain.run(inputs)
    # improvement = profile_improvement_chain.run(inputs)
    # results = {"cover_letter": cover_letter, "improvement_suggestions": improvement}
    
    return results

# --- Example usage ---
if __name__ == "__main__":
    # Example candidate profile and job description
    candidate_profile = """
    John Doe is a seasoned software engineer with 7 years of industry experience, specializing in backend development, cloud infrastructure, and microservices architecture.
    He has led development teams and is passionate about leveraging modern technologies to build scalable and reliable systems.
    """
    
    job_description = """
    Our company is seeking a Senior Software Engineer with strong experience in designing and implementing scalable back-end systems.
    The ideal candidate should have extensive experience with cloud infrastructure, containerization, and microservices.
    Leadership skills and the ability to mentor junior developers are essential.
    """
    
    # Run both agents via the orchestrator graph
    output = run_agents(candidate_profile, job_description)
    print("Generated Cover Letter:\n")
    print(output.get("CoverLetterAgent", "No cover letter generated."))
    print("\nProfile Improvement Suggestions:\n")
    print(output.get("ProfileImprovementAgent", "No suggestions generated."))

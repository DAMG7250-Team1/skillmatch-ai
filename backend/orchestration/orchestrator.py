# orchestration.py

import requests
try:
    from langgraph import Graph
except ImportError:
    # Simple simulation of a graph for orchestration
    class Graph:
        def __init__(self):
            self.nodes = {}
        def add_node(self, name, func):
            self.nodes[name] = func
            return name
        def add_edge(self, from_node, to_node):
            # In this simulation, edges are not used for control flow.
            pass
        def run_all(self, inputs):
            # Execute nodes in a fixed order.
            results = {}
            # Node order: ProcessProfile -> JobMatching -> GenerateFeedback
            for node_name in ["ProcessProfile", "JobMatching", "GenerateFeedback"]:
                func = self.nodes.get(node_name)
                if func:
                    output = func(inputs)
                    inputs.update(output)  # Update the inputs with the node's outputs
                    results[node_name] = output
            return results

# Import your cover letter and improvement generation function.
from cover.cover_letter import generate_cover_letter_and_improvements

def process_profile_node(inputs: dict) -> dict:
    """
    Fetches the resume and GitHub markdown content from the URLs,
    combines them into a full candidate profile, and passes the job description.
    Expects inputs to contain:
      - "resume_md_url"
      - "github_md_url"
      - "job_opening": a dict containing at least a "job_text" key.
    """
    resume_resp = requests.get(inputs["resume_md_url"])
    if resume_resp.status_code != 200:
        raise Exception(f"Error fetching resume markdown: {resume_resp.text}")
    git_resp = requests.get(inputs["github_md_url"])
    if git_resp.status_code != 200:
        raise Exception(f"Error fetching GitHub markdown: {git_resp.text}")
    
    combined_profile = resume_resp.text + "\n\n" + git_resp.text
    job_description = inputs.get("job_opening", {}).get("job_text", "")
    return {"combined_profile": combined_profile, "job_description": job_description}

def job_matching_node(inputs: dict) -> dict:
    """
    For orchestration, this node simply passes the job ID along.
    In an extended implementation, this node could query a job matching API.
    Expects inputs to contain "job_id".
    """
    return {"job_id": inputs.get("job_id", "")}

def generate_feedback_node(inputs: dict) -> dict:
    """
    Uses the combined candidate profile and job description to generate both a cover letter
    and profile improvement suggestions.
    Expects inputs to have:
       - "combined_profile"
       - "job_description"
    """
    profile = inputs.get("combined_profile", "")
    job_desc = inputs.get("job_description", "")
    # Call your helper function that uses direct OpenAI API calls.
    results = generate_cover_letter_and_improvements(profile, job_desc)
    return results

def create_workflow_graph() -> Graph:
    graph = Graph()
    graph.add_node("ProcessProfile", process_profile_node)
    graph.add_node("JobMatching", job_matching_node)
    graph.add_node("GenerateFeedback", generate_feedback_node)
    # Optionally, add edges (not used in this simple simulation)
    return graph

def run_workflow(resume_md_url: str, github_md_url: str, job_opening: dict, job_id: str) -> dict:
    """
    Runs the complete workflow:
      - Retrieves the candidate's markdown files (resume and GitHub) from their URLs,
      - Combines them into one candidate profile,
      - Passes along the job details from job_opening and the job_id,
      - Finally, generates both the cover letter and improvement suggestions.
    Returns the output from the GenerateFeedback node.
    """
    inputs = {
        "resume_md_url": resume_md_url,
        "github_md_url": github_md_url,
        "job_opening": job_opening,
        "job_id": job_id
    }
    graph = create_workflow_graph()
    results = graph.run_all(inputs)
    return results.get("GenerateFeedback", {})

if __name__ == "__main__":
    # Example usage:
    resume_md_url = "https://example.com/resume.md"
    github_md_url = "https://example.com/github.md"
    job_opening = {"job_text": "We are seeking a Senior Software Engineer with 3+ years of experience in cloud computing."}
    job_id = "job123"
    output = run_workflow(resume_md_url, github_md_url, job_opening, job_id)
    print(output)

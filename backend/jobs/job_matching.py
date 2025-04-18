

import os
import logging
import re
import json
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone

# Configure root logger to print DEBUG statements
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)
# Module-level logger
event_logger = logging.getLogger(__name__)
event_logger.setLevel(logging.DEBUG)

# Initialize OpenAI client
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables")
llm = OpenAI(api_key=openai_api_key)

# Initialize Pinecone client
pinecone_api_key = os.getenv('PINECONE_API_KEY')
if not pinecone_api_key:
    raise ValueError("Pinecone API key not found in environment variables")
pc = Pinecone(api_key=pinecone_api_key)
pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'skillmatch')
index = pc.Index(pinecone_index_name)

pinecone_user_namespace = os.getenv('PINECONE_USER_NAMESPACE', 'userprofile')
event_logger.info(f"Connected to Pinecone index: {pinecone_index_name}, namespace: {pinecone_user_namespace}")

# Initialize local embedding model for semantic skill matching
_skill_model = SentenceTransformer('all-MiniLM-L6-v2')

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill string by:
      - Lowercasing
      - Removing non-word characters except periods
      - Collapsing whitespace
    """
    lower = skill.lower().strip()
    cleaned = re.sub(r'[^a-z0-9\.]+', ' ', lower)
    return re.sub(r'\s+', ' ', cleaned).strip()

# Semantic skill matching function
def semantic_skill_match(user_skills: set, job_skills: set, threshold: float = 0.65) -> set:
    """
    Use embeddings to match skills semantically.
    Returns subset of user_skills that match any job_skill above threshold.
    """
    matches = set()
    # Pre-compute user skill embeddings
    user_vecs = {us: _skill_model.encode(us, convert_to_tensor=True) for us in user_skills}
    for js in job_skills:
        js_vec = _skill_model.encode(js, convert_to_tensor=True)
        for us, uv in user_vecs.items():
            sim = util.pytorch_cos_sim(uv, js_vec).item()
            if sim >= threshold:
                matches.add(us)
    return matches

def extract_degree_and_specialization(qual_text: str) -> tuple[str, str]:
    """
    Extract degree level and specialization from qualification text.
    Uses multiple patterns to handle different formats.
    """
    text = qual_text.lower()
    degree = None
    if 'phd' in text or 'doctor' in text:
        degree = 'phd'
    elif 'master' in text:
        degree = 'masters'
    elif 'bachelor' in text:
        degree = 'bachelors'

    # Improved specialization extraction with multiple patterns
    specialization = ''
    if degree:
        # Look for multiple patterns
        patterns = [
            r"(phd|master(?:s)?|bachelor(?:s)?) in ([a-z\s]+)",
            r"(phd|master(?:s)?|bachelor(?:s)?) of ([a-z\s]+)",
            r"(phd|master(?:s)?|bachelor(?:s)?).+?([a-z\s]+ engineering)",
            r"(phd|master(?:s)?|bachelor(?:s)?).+?([a-z\s]+ science)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                specialization = match.group(2).strip()
                break
                
    return degree, specialization

def semantic_specialization_match(user_spec: str, job_spec: str, threshold: float = 0.70) -> bool:
    """
    Check if specializations are semantically similar using embeddings.
    Returns True if similarity is above threshold.
    """
    if not user_spec or not job_spec:
        return False
    
    try:
        # Use the existing skill model to encode specializations
        user_vec = _skill_model.encode(user_spec, convert_to_tensor=True)
        job_vec = _skill_model.encode(job_spec, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(user_vec, job_vec).item()
        event_logger.debug(f"Specialization similarity: {user_spec} vs {job_spec} = {sim:.2f}")
        return sim >= threshold
    except Exception as e:
        event_logger.error(f"Error in semantic specialization matching: {e}")
        return False

class JobMatcher:
    def __init__(self):
        self.similarity_thresholds = {"high": 65, "medium": 35, "low": 10}
        self.index = index
        self.user_ns = pinecone_user_namespace

    def get_similarity_category(self, score: float) -> str:
        if score >= self.similarity_thresholds['high']:
            return 'high'
        if score >= self.similarity_thresholds['medium']:
            return 'average'
        if score >= self.similarity_thresholds['low']:
            return 'low'
        return 'very_low'

    def get_user_profile_embedding(self, profile: dict) -> list:
        return profile.get('combined_embedding', [])

    # def query_jobs(self, embedding: list, top_k: int = 5) -> list:
    #     try:
    #         resp = self.index.query(vector=embedding, top_k=top_k, include_metadata=True, namespace=None)
    #         event_logger.info(f"Received {len(resp.get('matches', []))} matches from Pinecone")
    #         return resp.get('matches', [])
    #     except Exception as e:
    #         event_logger.error(f"Pinecone query error: {e}")
    #         return []

    def query_jobs(self, embedding: list, top_k: int = 10) -> list:
        """
        Exhaustively queries all configured namespaces like DFS, collects all unique job matches,
        removes duplicates, and returns top-K sorted by similarity score.
        """
        namespaces_to_try = ["default", "jobs", "", None]
        all_matches = []

        for namespace in namespaces_to_try:
            try:
                logger.info(f"🔍 Querying namespace: {namespace or 'None'}")
                response = self.index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True,
                    namespace=namespace
                )
                matches = response.get("matches", [])
                logger.info(f"✅ Retrieved {len(matches)} matches from '{namespace}'")
                all_matches.extend(matches)
            except Exception as e:
                logger.warning(f"⚠️ Namespace query failed: {namespace} — {e}")
                continue

        # Deduplicate by match.id
        seen = set()
        unique_matches = []
        for match in all_matches:
            if match.id not in seen:
                seen.add(match.id)
                unique_matches.append(match)

        # Sort by Pinecone similarity score (highest first)
        sorted_matches = sorted(unique_matches, key=lambda m: m.score or 0.0, reverse=True)

        return sorted_matches[:top_k]





    def compute_weighted_score(self, profile: dict, job_meta: dict) -> float:
        # —— SKILLS ——
        # Get skills from multiple sources if all_skills is not present
        if 'all_skills' not in profile:
            github_skills = profile.get('github_skills', [])
            resume_skills = profile.get('resume_skills', [])
            user_skills = {normalize_skill(s) for s in github_skills + resume_skills}
            event_logger.debug(f"Combined skills from github and resume: {user_skills}")
        else:
            user_skills = {normalize_skill(s) for s in profile.get('all_skills', [])}
        
        job_skills = {normalize_skill(s) for s in job_meta.get('extracted_skills', [])}
        event_logger.debug(f"Job skills: {job_skills}")
        
        semantic_matches = semantic_skill_match(user_skills, job_skills)
        direct_matches = user_skills & job_skills
        
        # Log matches for debugging
        event_logger.debug(f"Direct matches: {direct_matches}")
        event_logger.debug(f"Semantic matches: {semantic_matches}")
        
        matched = semantic_matches.union(direct_matches)
        if user_skills and job_skills:
            overlap_pct = len(matched) / min(len(user_skills), len(job_skills)) * 100
        else:
            overlap_pct = 0.0
        skills_weighted = overlap_pct * 0.50  # 50% weight for skills
        event_logger.debug(f"Skills matched (direct+semantic): {matched} ({overlap_pct:.2f}% -> weighted {skills_weighted:.2f})")

        # —— QUALIFICATIONS ——
        udeg, uspec = extract_degree_and_specialization(profile.get('qualification', ''))
        jdeg, jspec = extract_degree_and_specialization(job_meta.get('qualifications', ''))
        event_logger.debug(f"User degree: {udeg}, specialization: {uspec}")
        event_logger.debug(f"Job degree: {jdeg}, specialization: {jspec}")
        
        rank = {'bachelors':1, 'masters':2, 'phd':3}
        # Apply 80% weightage to degree matching
        deg_score = 0.0
        if udeg in rank and jdeg in rank:
            deg_score = min(rank[udeg] / rank[jdeg], 1.0) * 100
        deg_weighted = deg_score * 0.80 * 0.15  # 80% of the 15% qualification weight

        # Apply 20% weightage to specialization matching
        spec_score = 0.0
        if uspec and jspec:
            # Use dynamic semantic matching instead of predefined pairs
            if semantic_specialization_match(uspec, jspec):
                spec_score = 100.0
        spec_weighted = spec_score * 0.20 * 0.15  # 20% of the 15% qualification weight

        qualification_weighted = deg_weighted + spec_weighted
        event_logger.debug(f"Degree: {deg_score:.2f} -> {deg_weighted:.2f}, Spec: {spec_score:.2f} -> {spec_weighted:.2f}")

        # —— EXPERIENCE ——
        raw_exp = profile.get('experience_year') or profile.get('senority')
        user_years = 0.0
        if isinstance(raw_exp, dict):
            user_years = float(raw_exp.get('total_experience_years', 0))
        else:
            try:
                data = json.loads(raw_exp or '{}')
                user_years = float(data.get('total_experience_years', 0))
            except Exception:
                user_years = 0.0
        m = re.search(r"(\d+)", job_meta.get('experience', ''))
        job_years = float(m.group(1)) if m else 0.0
        
        event_logger.debug(f"User experience years: {user_years}")
        event_logger.debug(f"Job required years: {job_years}")
        
        exp_score = 0.0
        if job_years > 0:
            diff_pct = abs(user_years - job_years) / job_years * 100
            exp_score = max(100 - diff_pct, 0)
        exp_weighted = exp_score * 0.20  # 20% weight for experience
        event_logger.debug(f"Experience: {exp_score:.2f}% -> {exp_weighted:.2f}")

        final = skills_weighted + qualification_weighted + exp_weighted
        event_logger.info(f"Final weighted score: {final:.2f}")
        return final

    def match_profile_with_jobs(self, profile: dict, top_k: int = 5) -> dict:
        event_logger.info(f"Matching profile with top {top_k} jobs...")
        emb = self.get_user_profile_embedding(profile)
        matches = self.query_jobs(emb, top_k=top_k)
        results = []
        for m in matches:
            score = self.compute_weighted_score(profile, m.metadata)
            cat = self.get_similarity_category(score)
            
            # Get skills from multiple sources if all_skills is not present
            if 'all_skills' not in profile:
                github_skills = profile.get('github_skills', [])
                resume_skills = profile.get('resume_skills', [])
                user_skills = {normalize_skill(s) for s in github_skills + resume_skills}
            else:
                user_skills = {normalize_skill(s) for s in profile.get('all_skills', [])}
                
            job_skills = {normalize_skill(s) for s in m.metadata.get('extracted_skills', [])}
            direct_matches = user_skills & job_skills
            semantic_matches = semantic_skill_match(user_skills, job_skills)
            all_matches = direct_matches.union(semantic_matches)
            matching_skills = list(all_matches)
            event_logger.debug(f"Result for job_id={m.id}: score={score:.2f}, category={cat}, skills={matching_skills}")
            results.append({
                'job_id': m.id,
                'job_title': m.metadata.get('job_title', ''),
                'company': m.metadata.get('company', ''),
                'similarity_score': score,
                'similarity_category': cat,
                'matching_skills': matching_skills
            })
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return {'status': 'success', 'total_matches': len(results), 'matches': results[:top_k]}


    def get_similar_jobs(self, query: str, top_k: int = 3):
        """
        Public wrapper to find similar jobs using Tavily.
        Returns a list of job dictionaries.
        """
        try:
            logging.info(f"[CompanyJobAgent] Getting similar jobs for query: {query}")
            similar_jobs_raw = self._search_jobs(query)
            return [job for _, job in similar_jobs_raw[:top_k]]
        except Exception as e:
            self.logger.error(f"Error in get_similar_jobs: {str(e)}")
            return []


def main():
    # import os
    # from pinecone import Pinecone, ServerlessSpec
    # pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
    # index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    matcher = JobMatcher()
    # matcher.index = index

    user_profile_data = {
        "ID": "test_user_123_d147f88fba006c714e27f17e96ea04bf",
        "combined_embedding": [0.25] * 3072,
        "qualification": "- Master of Computer Software Engineering from Northeastern University, Boston, USA (Expected Dec 2025)\n- Bachelor of Computer Science from Maharaja Sayajirao University, Vadodara, India (July 2018 - May 2022)",
        "experience_year": '{"total_experience_months": 39.0, "total_experience_years": 3, "experience_year": "Software Engineering Teacher Assistant: 7 months, Software Developer at Crest Data System: 16 months, Software Developer at Overclocked Brains: 16 months. Total Experience: 3 years"}',
        "github_skills": ["JavaScript", "TypeScript", "TSQL", "C++", "HTML", "CSS", "Node.js", "Yarn", "React", "SQL"],
        "resume_skills": ["JavaScript", "Java", "Python", "C++", "Typescript", "HTML", "CSS", "React.js", "Node.js"]
    }

    results = matcher.match_profile_with_jobs(user_profile_data, top_k=5)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()

import os
import re
import json
import logging
from typing import List, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone
from concurrent.futures import ThreadPoolExecutor
import time
 
# Setup logger
logger = logging.getLogger("HybridJobMatcher")
logger.setLevel(logging.INFO)
 
# Load local model once
_skill_model = SentenceTransformer('all-MiniLM-L6-v2')
 
def normalize_skill(skill: str) -> str:
    return re.sub(r'[^a-z0-9\.]+', ' ', skill.lower().strip())
 
def semantic_skill_match(user_vecs: Dict[str, Any], job_skills: set, threshold: float = 0.65) -> set:
    matches = set()
    job_vecs = _skill_model.encode(list(job_skills), convert_to_tensor=True)
    for js, js_vec in zip(job_skills, job_vecs):
        for us, us_vec in user_vecs.items():
            sim = util.pytorch_cos_sim(us_vec, js_vec).item()
            if sim >= threshold:
                matches.add(us)
    return matches
 
def semantic_specialization_match(user_spec: str, job_spec: str, threshold: float = 0.7) -> bool:
    if not user_spec or not job_spec:
        return False
    user_vec = _skill_model.encode(user_spec, convert_to_tensor=True)
    job_vec = _skill_model.encode(job_spec, convert_to_tensor=True)
    return util.pytorch_cos_sim(user_vec, job_vec).item() >= threshold
 
def extract_degree_and_specialization(text: str) -> Tuple[str, str]:
    text = text.lower()
    degree, spec = "", ""
    if "phd" in text:
        degree = "phd"
    elif "master" in text:
        degree = "masters"
    elif "bachelor" in text:
        degree = "bachelors"
    if " in " in text:
        spec = text.split(" in ")[1].split("\n")[0].strip()
    return degree, spec
 
class JobMatcher:
    def __init__(self):
        self.similarity_thresholds = {"high": 45, "medium": 25, "low": 5}
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "skillmatch")
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = self.pc.Index(self.pinecone_index_name)
 
    def fetch_jobs_from_pinecone(self, embedding: List[float], top_k: int = 100) -> List[Any]:
        namespaces = ["default", None, "jobs", ""]
        results = []
        for ns in namespaces:
            try:
                query = self.index.query(vector=embedding, top_k=top_k, include_metadata=True, namespace=ns)
                results.extend(query.get("matches", []))
            except Exception as e:
                logger.warning(f"Namespace '{ns}' failed: {e}")
 
        # Deduplicate and filter out jobs with missing title or company
        unique = {}
        for match in results:
            if match.id not in unique and match.metadata.get("job_title") and match.metadata.get("company"):
                unique[match.id] = match
        # Additional filtering: exclude jobs with empty critical fields
        filtered_jobs = []
        for match in unique.values():
            meta = match.metadata
            # Reject jobs missing 4 or more key fields
            missing_fields = sum(
                1 for field in ["job_title", "company", "job_type", "work_mode", "seniority", "experience", "responsibilities", "qualifications"]
                if not meta.get(field) or not str(meta.get(field)).strip()
            )
            if missing_fields < 4:
                filtered_jobs.append(match)
 
        return sorted(filtered_jobs, key=lambda m: m.score or 0, reverse=True)
 
    def compute_weighted_score(self, profile: dict, job: dict, profile_skills: set, user_vecs: Dict[str, Any]) -> float:
        job_skills = {normalize_skill(s) for s in job.get("extracted_skills", [])}
 
        semantic_matches = semantic_skill_match(user_vecs, job_skills) if len(job_skills) >= 3 else set()
        direct_matches = profile_skills & job_skills
        matched = semantic_matches | direct_matches
 
        skills_score = (len(matched) / max(len(job_skills), 1)) * 100 if job_skills else 0
        skills_weighted = skills_score * 0.50
 
        udeg, uspec = extract_degree_and_specialization(profile.get("qualification", ""))
        jdeg, jspec = extract_degree_and_specialization(job.get("qualifications", ""))
        rank = {"bachelors": 1, "masters": 2, "phd": 3}
 
        deg_score = 0
        if udeg in rank and jdeg in rank:
            deg_score = min(rank[udeg] / rank[jdeg], 1.0) * 100
        deg_weighted = deg_score * 0.80 * 0.15
 
        spec_score = 100.0 if semantic_specialization_match(uspec, jspec) else 0.0
        spec_weighted = spec_score * 0.20 * 0.15
 
        qualification_weighted = deg_weighted + spec_weighted
 
        exp_data = profile.get("experience_year", {})
        user_years = 0.0
        if isinstance(exp_data, dict):
            user_years = float(exp_data.get("total_experience_years", 0))
        elif isinstance(exp_data, str):
            try:
                user_years = float(json.loads(exp_data).get("total_experience_years", 0))
            except:
                pass
 
        job_exp = 0
        m = re.search(r"(\d+)", job.get("experience", ""))
        if m:
            job_exp = float(m.group(1))
        exp_score = max(100 - abs(user_years - job_exp) / job_exp * 100, 0) if job_exp > 0 else 100
        exp_weighted = exp_score * 0.20
 
        return skills_weighted + qualification_weighted + exp_weighted
 
    def match_profile_with_jobs(self, profile: dict, top_k: int = 40) -> Dict[str, Any]:
        embedding = profile.get("combined_embedding", [])
        profile_skills = {normalize_skill(s) for s in profile.get("all_skills", [])}
        user_vec_list = list(profile_skills)
        user_vecs_encoded = _skill_model.encode(user_vec_list, convert_to_tensor=True)
        user_vecs = dict(zip(user_vec_list, user_vecs_encoded))
 
        jobs = self.fetch_jobs_from_pinecone(embedding, top_k=100)
 
        if not jobs:
            return {"status": "success", "total_matches": 0, "matches": []}
 
        def score_job(match):
            score = self.compute_weighted_score(profile, match.metadata, profile_skills, user_vecs)
            job_skills = {normalize_skill(s) for s in match.metadata.get("extracted_skills", [])}
            matched_skills = list(profile_skills & job_skills)
            return {
                "job_id": match.id,
                "job_title": match.metadata.get("job_title", ""),
                "company": match.metadata.get("company", ""),
                "similarity_score": score,
                "similarity_category": self.get_similarity_category(score),
                "matching_skills": matched_skills
            }
 
        start_time = time.time()
 
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(score_job, jobs))
 
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        elapsed = time.time() - start_time
 
        logger.info(f"✅ Matched {len(results)} jobs in {elapsed:.2f} seconds.")
 
        return {
            "status": "success",
            "total_matches": len(results),
            "matches": results[:top_k]
        }
 
    def get_similarity_category(self, score: float) -> str:
        if score >= self.similarity_thresholds["high"]:
            return "high"
        elif score >= self.similarity_thresholds["medium"]:
            return "average"
        elif score >= self.similarity_thresholds["low"]:
            return "low"
        return "very_low"
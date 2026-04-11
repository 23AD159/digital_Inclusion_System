import os

def setup_nlp():
    import nltk
    """
    Downloads NLTK components if missing. 
    spaCy models should be installed via CLI.
    """
    try:
        # Standard lightweight downloads
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('universal_tagset', quiet=True)
    except:
        pass

def extract_skills_from_resume(resume_path):
    """
    Uses PyResParser to extract skills and experience.
    Returns (success, skills_list, experience_years)
    """
    if not resume_path or not os.path.exists(resume_path):
        return False, [], 0
    
    try:
        from pyresparser import ResumeParser
        # Pre-ensure models are there
        setup_nlp()
        
        data = ResumeParser(resume_path).get_extract_data()
        skills = data.get('skills', [])
        experience = data.get('total_experience', 0)
        
        return True, skills, experience
    except Exception as e:
        print(f"Resume parsing error: {e}")
        return False, [], 0

def calculate_trust_delta(claimed_skills, extracted_skills):
    """
    Compares claimed skills count to extracted skills.
    Simple ratio check for 'Trust' score calculation.
    """
    if not claimed_skills:
        return 1.0 # No skills claimed, no distrust
    
    matches = [s for s in claimed_skills if s.lower() in [es.lower() for es in extracted_skills]]
    return len(matches) / len(claimed_skills)

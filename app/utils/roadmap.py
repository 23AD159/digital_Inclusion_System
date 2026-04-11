def generate_roadmap(score, category, gaps, recommendations):
    """
    Generates a structured 30-day improvement roadmap based on student performance.
    """
    roadmap = {
        "title": f"30-Day Digital Workforce Readiness Roadmap",
        "phases": []
    }
    
    # Phase 1: Immediate Gaps (Day 1-10)
    phase1 = {
        "title": "Phase 1: Foundation & Critical Fixes",
        "tasks": []
    }
    if gaps[0] < 12: # Digital Access
        phase1["tasks"].append("Audit your internet connectivity and hardware setup.")
    if gaps[2] < 12: # Networking
        phase1["tasks"].append("Complete your LinkedIn profile and reach out to 5 alumni.")
    if not phase1["tasks"]:
        phase1["tasks"].append("Review your current project documentation for clarity.")
    roadmap["phases"].append(phase1)
    
    # Phase 2: Skill Building (Day 11-20)
    phase2 = {
        "title": "Phase 2: Domain Deep-Dive",
        "tasks": []
    }
    if gaps[1] < 18: # Meta-Skills
        phase2["tasks"].append("Enroll in a specialized technical course (e.g., Python Advanced or AI Basics).")
    if gaps[3] < 9: # Integration
        phase2["tasks"].append("Build a small project integrating at least one modern API.")
    if not phase2["tasks"]:
        phase2["tasks"].append("Contribute to one open-source repository on GitHub.")
    roadmap["phases"].append(phase2)
    
    # Phase 3: Professional Polish (Day 21-30)
    phase3 = {
        "title": "Phase 3: Industry Alignment & Mock Testing",
        "tasks": []
    }
    if gaps[4] < 9: # Career Readiness
        phase3["tasks"].append("Undergo 2 mock interviews focusing on behavioral questions.")
    else:
        phase3["tasks"].append("Refine your portfolio website for high-impact visual appeal.")
    roadmap["phases"].append(phase3)
    
    return roadmap

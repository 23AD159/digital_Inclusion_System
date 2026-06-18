# AI-Driven Digital Inclusion & Workforce Readiness Indexing System

## Abstract
With the rapid evolution of technology, analyzing the "Digital Inclusion & Workforce Readiness" of college students has become a critical need. This project proposes an AI-driven indexing system modeled after NASSCOM's skill requirements to evaluate and score 3rd and 4th-year students from Tier-2 and Tier-3 colleges. By securely collecting data on digital literacy, practical programming skills, professional networking, and modern tool usage, the system computes a Digital Inclusion Score out of 100. An underlying Machine Learning model (Random Forest) evaluates the student's background to categorize them into 'Industry Ready', 'Needs Upskilling', or 'High Risk'. Additionally, the system features a personalized recommendation engine to help students bridge their skill gaps and an overarching analytics dashboard for institutional administrators to identify trends and organize proper upskilling programs.

## Problem Statement
Students in Tier-2 and Tier-3 colleges often graduate with an academic degree but lack the specific digital skills required by modern industries (e.g., GitHub usage, AI tools familiarity, consistent coding practices). There is no standardized tool to index, quantify, and categorize these students' readiness before placement season begins. This results in high unemployment rates and skill mismatches, leaving placement cells completely unaware of targeted interventions needed for high-risk students.

## System Architecture Diagram
The architecture comprises a three-tier model:
1. **Frontend**: HTML/CSS/JS with Bootstrap for responsiveness, containing profiles, surveys, and Chart.js analytics.
2. **Backend Engine**: A Python Flask REST API connected to SQLite to handle user state, scores, and business logic.
3. **AI/ML Layer**: Scikit-Learn RandomForest classifier that infers the risk category from historical normalized inputs.

## Data Flow Explanation
1. **User Registration/Login**: The student creates a profile containing contextual metadata.
2. **Survey Data Collection**: Student fills a 25-point criteria survey capturing parameters across digital access, technical skills, networking, and soft skills.
3. **Backend Processing**: The Flask application sanitizes the inputs and assigns weights to each parameter to formulate the `Digital Inclusion Score (0-100)`.
4. **AI Inference**: The processed feature vector is passed to the pre-trained `scikit-learn` Machine Learning model. 
5. **Recommendation Engine**: A rule-based engine creates actionable points for the student tailored to their weaknesses.
6. **Admin Analytics**: Cohort data is pushed to the Admin Dashboard API, mapped into `Chart.js`.

## Future Improvements
- **LLM Integration**: Using GenAI to dynamically talk with the student and provide deeper resume review.
- **LinkedIn/GitHub API**: Automatically fetching student commits or repos for transparent background-checks.
- **Corporate Portal**: Allowing corporate HRs to login and filter out 'Industry Ready' students directly for placement drives.

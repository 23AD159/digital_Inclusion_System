import google.generativeai as genai
from flask import current_app

def get_gemini_response(user_message, student_context):
    """
    Interfaces with Gemini Pro to provide mentorship based on student data.
    student_context: { 'score': 80, 'category': 'Industry Ready', 'gaps': [...], 'roadmap': {...} }
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return "Mentor is offline (API Key Missing)."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Detect Interview Mode
        is_interview = "[MODE: INTERVIEW]" in user_message
        clean_message = user_message.replace("[MODE: INTERVIEW]", "").strip()

        # Construct the specialized prompt
        if is_interview:
            system_prompt = f"""
            You are 'DigiGuide Pro', a professional HR Interviewer and Technical Recruiter.
            MODE: BEHAVIORAL MOCK INTERVIEW.
            STUDENT CONTEXT: Score {student_context['score']}, Category {student_context['category']}.
            
            GOAL:
            1. Conduct a rigorous but encouraging behavioral interview.
            2. Ask one question at a time.
            3. Evaluate their digital readiness based on their answers.
            """
        else:
            system_prompt = f"""
            You are 'DigiGuide', a world-class Academic Mentor for a Digital Inclusion platform.
            Your goal is to help the student understand their Digital Workforce Readiness score and guide them through their roadmap.
            
            STUDENT PROFILE:
            - Current Score: {student_context['score']}/100
            - Category: {student_context['category']}
            - Key Gaps identified: {student_context['gaps']}
            - 30-Day Roadmap Summary: {student_context['roadmap']}
            
            STYLE GUIDELINES:
            1. Be professional, warm, and highly encouraging.
            2. Suggest exactly one task from their Roadmap to focus on first.
            """
        
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{system_prompt}\n\nStudent Message: {clean_message}")
        
        return response.text
    except Exception as e:
        # Smart Fallback System for Quota (429) or Network Errors
        fallback_tips = {
            'Digital Seed 🌱': "I'm currently busy helping students, but here is a tip for you: Focus on the 'Computer Fundamentals' section in W3Schools. Building a strong foundation is your first step to success! 🚀",
            'Digital Explorer 🧭': "I'm analyzing a lot of profiles right now! For your level, I recommend watching Abdul Bari's Algorithms introduction. It will help you move from basic coding to technical mastery. 💡",
            'Digital Master 🎖️': "You're doing great! While I'm busy with other students, my advice for you is to start practicing mock interviews on Interviewing.io. You are very close to landing a top role! 🎯",
            'Industry Ready 💼': "Impressive profile! While I'm temporarily offline, focus on optimizing your LinkedIn profile. Use the Wonsulting tips from your Learning Vault to attract recruiters! 🌟"
        }
        
        category = student_context.get('category', 'Digital Seed 🌱')
        return fallback_tips.get(category, "I'm busy reflecting on your great progress! Please try again in a moment, and keep following your personalized roadmap. You've got this! ✨")

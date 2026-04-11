from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.models import User, Result, SurveyResponse, Recommendation
from app.utils.llm_mentor import get_gemini_response
from app.utils.roadmap import generate_roadmap

api = Blueprint('api', __name__)

@api.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    """Gemini-Powered DigiGuide Mentor Backend"""
    data = request.json
    user_msg = data.get('message', '')
    
    if not user_msg:
        return jsonify({'reply': "I'm listening! How can I help you today?"})

    # Fetch Student Context for the AI
    res = Result.query.filter_by(student_id=current_user.id).first()
    if not res:
        return jsonify({'reply': "Please complete the AI Survey first so I can give you personalized advice! 📝"})
    
    sr = SurveyResponse.query.filter_by(student_id=current_user.id).first()
    recs = [r.recommendation_text for r in Recommendation.query.filter_by(student_id=current_user.id).all()]
    
    # Reconstruct Gaps for AI
    gaps = [0]*5
    if sr:
        gaps[0] = sum([getattr(sr, f'q{i}') for i in range(1, 6)])
        gaps[1] = sum([getattr(sr, f'q{i}') for i in range(6, 11)])
        gaps[2] = sum([getattr(sr, f'q{i}') for i in range(11, 16)])
        gaps[3] = sum([getattr(sr, f'q{i}') for i in range(16, 21)])
        gaps[4] = sum([getattr(sr, f'q{i}') for i in range(21, 26)])
    
    roadmap = generate_roadmap(res.score, res.category, gaps, recs)
    
    context = {
        'score': res.score,
        'category': res.category,
        'gaps': gaps,
        'roadmap': roadmap
    }
    
    # Special Handling for quick rule-based queries (Optional)
    if "points" in user_msg.lower() or "score" in user_msg.lower():
         return jsonify({'reply': f"You currently have {current_user.points} points and a score of {res.score}/100! You are categorized as '{res.category}'. What else should we focus on? 🚀"})

    # Call Gemini Pro
    reply = get_gemini_response(user_msg, context)
        
    return jsonify({'reply': reply})

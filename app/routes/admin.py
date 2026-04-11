from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Result, SurveyResponse
from sqlalchemy import func

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
        
    total = User.query.filter_by(role='student').count()
    avg_score = db.session.query(func.avg(Result.score)).scalar() or 0
    avg_score = round(float(avg_score), 2)
    
    # Category Distribution
    dist_raw = db.session.query(Result.category, func.count(Result.id)).group_by(Result.category).all()
    dist = {cat: count for cat, count in dist_raw}
    
    # Fill missing distribution keys
    for k in ['Industry Ready', 'Needs Upskilling', 'High Risk']:
        if k not in dist:
            dist[k] = 0
            
    # Line chart logic
    results = Result.query.order_by(Result.id).all()
    score_labels = [f"St-{r.id}" for r in results]
    score_data = [r.score for r in results]
    
    # Skill Gaps
    gaps = db.session.query(
        func.avg(SurveyResponse.q1 + SurveyResponse.q2 + SurveyResponse.q3 + SurveyResponse.q4 + SurveyResponse.q5),
        func.avg(SurveyResponse.q6 + SurveyResponse.q7 + SurveyResponse.q8 + SurveyResponse.q9 + SurveyResponse.q10),
        func.avg(SurveyResponse.q11 + SurveyResponse.q12 + SurveyResponse.q13 + SurveyResponse.q14 + SurveyResponse.q15),
        func.avg(SurveyResponse.q16 + SurveyResponse.q17 + SurveyResponse.q18 + SurveyResponse.q19 + SurveyResponse.q20),
        func.avg(SurveyResponse.q21 + SurveyResponse.q22 + SurveyResponse.q23 + SurveyResponse.q24 + SurveyResponse.q25)
    ).first()
    
    skill_gaps = [round(float(val), 1) if val is not None else 0 for val in gaps] if gaps else [0]*5

    # Skill Gap Heatmap Metrics
    total_surveys = SurveyResponse.query.count() or 1
    no_github = SurveyResponse.query.filter((SurveyResponse.q8 == 0) | (SurveyResponse.github_url == '') | (SurveyResponse.github_url == None)).count()
    percent_no_github = int((no_github / total_surveys) * 100)
    
    no_comm = SurveyResponse.query.filter((SurveyResponse.q21 <= 1)).count() # q21 is communication/presentation
    percent_no_comm = int((no_comm / total_surveys) * 100)

    # Verification Stats
    verified_count = Result.query.filter(Result.validation_status.contains('✅')).count()
    total_results = Result.query.count() or 1
    verification_rate = int((verified_count / total_results) * 100)

    return render_template('dashboard.html', total=total, avg_score=avg_score, dist=dist, score_labels=score_labels, score_data=score_data, skill_gaps=skill_gaps, percent_no_github=percent_no_github, percent_no_comm=percent_no_comm, verification_rate=verification_rate)

@admin.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    if current_user.role != 'admin': 
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    internet_boost = float(data.get('bandwidth', 0)) / 100.0
    training_boost = float(data.get('training', 0)) / 100.0
    
    avg_score_current = db.session.query(func.avg(Result.score)).scalar() or 0
    avg_score_current = float(avg_score_current)
    
    simulated_avg = min(100, avg_score_current + (avg_score_current * internet_boost * 0.4) + (avg_score_current * training_boost * 0.6))
    
    dist_raw = db.session.query(Result.category, func.count(Result.id)).group_by(Result.category).all()
    current_dist = {cat: count for cat, count in dist_raw}
    
    high_risk = current_dist.get('High Risk', 0)
    upskilling = current_dist.get('Needs Upskilling', 0)
    ready = current_dist.get('Industry Ready', 0)
    
    shift_factor = min(1.0, (internet_boost + training_boost))
    
    high_risk_migrating = int(high_risk * shift_factor)
    upskilling_migrating = int(upskilling * shift_factor)
    
    sim_high_risk = high_risk - high_risk_migrating
    sim_upskilling = upskilling + high_risk_migrating - upskilling_migrating
    sim_ready = ready + upskilling_migrating
    
    return jsonify({
        'current_avg': round(avg_score_current, 2),
        'simulated_avg': round(simulated_avg, 2),
        'distribution': {
            'High Risk': sim_high_risk,
            'Needs Upskilling': sim_upskilling,
            'Industry Ready': sim_ready
        }
    })

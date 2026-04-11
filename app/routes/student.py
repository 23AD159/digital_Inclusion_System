import os
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import User, SurveyResponse, Result, Recommendation
from app.utils.ml_engine import load_student_model, predict_student_category, calculate_placement_chance
from app.utils.pdf_generator import generate_report_pdf
from app.utils.cert_generator import generate_certificate_pdf
from app.utils.roadmap import generate_roadmap

student = Blueprint('student', __name__)

@student.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    
    # Check if student already submitted survey
    if Result.query.filter_by(student_id=current_user.id).first():
        return redirect(url_for('student.result'))
        
    if request.method == 'POST':
        # Retrieve Q1 to Q25
        qs = [int(request.form.get(f'q{i}', 0)) for i in range(1, 26)]
        
        # Professional Profile Links
        github_url = request.form.get('github_url', '')
        linkedin_url = request.form.get('linkedin_url', '')
        hackerrank_url = request.form.get('hackerrank_url', '')
        leetcode_url = request.form.get('leetcode_url', '')
        
        # Resume Upload
        resume_path = ''
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                filename = secure_filename(f"user_{current_user.id}_resume_{file.filename}")
                filepath = os.path.join(current_app.config['RESUME_FOLDER'], filename)
                file.save(filepath)
                resume_path = filepath
        
        # Certifications Upload
        certs_list = []
        cert_names = request.form.getlist('cert_names[]')
        cert_files = request.files.getlist('certs[]')
        
        for i, name in enumerate(cert_names):
            if i < len(cert_files):
                file = cert_files[i]
                if file and file.filename:
                    filename = secure_filename(f"user_{current_user.id}_cert_{i}_{file.filename}")
                    filepath = os.path.join(current_app.config['CERTIFICATE_FOLDER'], filename)
                    file.save(filepath)
                    certs_list.append({'name': name, 'path': filepath})
        
        certifications_json = json.dumps(certs_list)

        # Save to survey_responses
        response = SurveyResponse(
            student_id=current_user.id,
            github_url=github_url,
            linkedin_url=linkedin_url,
            hackerrank_url=hackerrank_url,
            leetcode_url=leetcode_url,
            resume_path=resume_path,
            certifications_json=certifications_json,
            **{f'q{i+1}': qs[i] for i in range(25)}
        )
        db.session.add(response)
        
        from app.utils.validators import verify_github_profile, verify_linkedin_profile
        from app.utils.resume_parser import extract_skills_from_resume, calculate_trust_delta
        
        # Profile Validation Logic (Safe Wrapped)
        validation_errors = []
        github_count = 0
        
        try:
            if github_url:
                success, github_count, msg = verify_github_profile(github_url)
                if not success:
                    validation_errors.append(f"GitHub: {msg}")
                elif github_count == 0 and qs[7] >= 3:
                    validation_errors.append("GitHub profile is empty despite claimed high usage")
            elif qs[7] >= 3:
                validation_errors.append("GitHub link missing despite claimed usage")

            if linkedin_url:
                success, msg = verify_linkedin_profile(linkedin_url)
                if not success:
                   validation_errors.append(f"LinkedIn: {msg}")
            elif qs[11] >= 2:
                validation_errors.append("LinkedIn profile missing despite claimed networking")

            # Resume Verification
            if resume_path:
                 try:
                     success, skills, exp = extract_skills_from_resume(resume_path)
                 except:
                     pass
            elif qs[10] >= 2:
                validation_errors.append("Resume missing despite claimed draft completeness")
                
            # Behavior Profile Checking Logic
            if qs[5] == 6 and current_user.login_count <= 1:
                validation_errors.append("Behavior mismatch: Claims daily activity but portal logs are nearly zero")
        except Exception as e:
            current_app.logger.error(f"Validation step partial failure: {e}")
            
        validation_status = "✅ Profile Verified" if not validation_errors else "❌ Verification Delta: " + " | ".join(validation_errors)

        # Base Score Penalty System
        penalty = len(validation_errors) * 5
        # Reward for actually having repos
        reward = 5 if github_count > 5 else 0
        score = max(0, sum(qs) - penalty + reward)
        
        # Placement Prediction
        placement_chance = calculate_placement_chance(score, len(validation_errors))
        
        # Prediction & Results
        try:
            model = load_student_model()
            cat = predict_student_category(qs, model)
        except:
            cat = predict_student_category(qs, None) # Fallback

        # Gamification
        points = score * 5 + 100 
        badge = "Digital Master 🎖️" if score >= 80 else "Digital Explorer 🧭" if score >= 50 else "Digital Seed 🌱"
        
        current_user.points = points
        current_user.badges = badge

        # Save result
        res = Result(
            student_id=current_user.id,
            score=score,
            category=cat,
            validation_status=validation_status,
            placement_chance=placement_chance
        )
        db.session.add(res)
        
        # Recommendations
        try:
            recs = []
            cat2_score = sum(qs[5:10])   # Coding exposure
            cat3_score = sum(qs[10:15])  # Professional/LinkedIn
            cat5_score = sum(qs[20:25])  # Career/Communication/Placements
            
            if cat2_score < 15: 
                recs.extend(["Practice coding daily on LeetCode/HackerRank.", "Build micro-projects in Python or Javascript."])
            if cat3_score < 10: 
                recs.extend(["Optimize your LinkedIn profile and connections.", "Create an active GitHub portfolio."])
            if cat5_score < 8:  
                recs.extend(["Attend placement training & mock interviews.", "Enhance professional email communication skills."])
            if qs[16] < 2:  # AI tool specific
                recs.extend(["Learn to safely leverage AI tools like ChatGPT for productivity."])
                
            if score < 50:
                recs.append("🚨 CRITICAL ACTION REQUIRED: Join our interactive Bootcamp. Recommend subscribing to Abdul Bari's Algorithms course, Jenni's Lectures, and utilizing FreeCodeCamp.org to rapidly upskill!")
                
            if not recs: 
                recs.append("You are currently tracking extremely well! Keep up the good work and mentor others.")
                
            for r in recs: 
                db.session.add(Recommendation(student_id=current_user.id, recommendation_text=r))
        except Exception as e:
            db.session.add(Recommendation(student_id=current_user.id, recommendation_text="Data processing partial failure, but your base score was saved."))
            
        db.session.commit()
        return redirect(url_for('student.result'))
        
    redirected = request.args.get('redirected')
    return render_template('survey.html', redirected=redirected)

@student.route('/result')
@login_required
def result():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    res = Result.query.filter_by(student_id=current_user.id).first()
    if not res:
        return redirect(url_for('student.survey', redirected=1))
    
    recs = [r.recommendation_text for r in Recommendation.query.filter_by(student_id=current_user.id).all()]
    
    # Calculate Gaps for Roadmap
    sr = SurveyResponse.query.filter_by(student_id=current_user.id).first()
    gaps = [0]*5
    if sr:
        gaps[0] = sum([getattr(sr, f'q{i}') for i in range(1, 6)])
        gaps[1] = sum([getattr(sr, f'q{i}') for i in range(6, 11)])
        gaps[2] = sum([getattr(sr, f'q{i}') for i in range(11, 16)])
        gaps[3] = sum([getattr(sr, f'q{i}') for i in range(16, 21)])
        gaps[4] = sum([getattr(sr, f'q{i}') for i in range(21, 26)])
    
    roadmap = generate_roadmap(res.score, res.category, gaps, recs)
    
    # Leaderboard
    leaderboard = User.query.filter(User.role=='student', User.points > 0).order_by(User.points.desc()).limit(5).all()
    
    # Peer Comparison
    total_students_res = Result.query.count() or 1
    lower_students = Result.query.filter(Result.score < res.score).count() or 0
    percentile = int((lower_students / total_students_res) * 100)
    
    # Dynamic Resource Mapping
    all_resources = {
        'foundation': [
            {'title': "Jenny's Lectures: CS Fundamentals", 'platform': 'YouTube', 'url': 'https://www.youtube.com/@JennyslecturesCSIT', 'icon': 'fa-brands fa-youtube'},
            {'title': 'W3Schools: Master the Basics', 'platform': 'Website', 'url': 'https://www.w3schools.com/', 'icon': 'fa-solid fa-code'},
            {'title': 'TutorialsPoint: Computer Science', 'platform': 'Website', 'url': 'https://www.tutorialspoint.com/index.htm', 'icon': 'fa-solid fa-graduation-cap'}
        ],
        'coding': [
            {'title': 'Abdul Bari: Algorithms & DSA', 'platform': 'YouTube', 'url': 'https://www.youtube.com/@abdul_bari', 'icon': 'fa-brands fa-youtube'},
            {'title': 'Algo Tamizha: Coding in Tamil', 'platform': 'YouTube', 'url': 'https://www.youtube.com/@AlgoTamizha', 'icon': 'fa-brands fa-youtube'},
            {'title': 'TakeUForward: Striver A2Z DSA', 'platform': 'Website', 'url': 'https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/', 'icon': 'fa-solid fa-bolt'},
            {'title': 'Programiz: Learn to Code', 'platform': 'Website', 'url': 'https://www.programiz.com/', 'icon': 'fa-solid fa-p'}
        ],
        'market': [
            {'title': 'Resume Building Guide', 'platform': 'GFG', 'url': 'https://www.geeksforgeeks.org/resume-building-guide/', 'icon': 'fa-solid fa-file-invoice'},
            {'title': 'Wonsulting: Career Tips', 'platform': 'YouTube', 'url': 'https://www.youtube.com/@Wonsulting', 'icon': 'fa-brands fa-youtube'}
        ],
        'ai': [
            {'title': 'AI & Machine Learning', 'platform': 'GFG', 'url': 'https://www.geeksforgeeks.org/machine-learning-projects/', 'icon': 'fa-solid fa-robot'},
            {'title': 'Prompt Engineering Guide', 'platform': 'YouTube', 'url': 'https://www.youtube.com/results?search_query=prompt+engineering+for+beginners', 'icon': 'fa-brands fa-youtube'}
        ],
        'career': [
            {'title': 'Interview Experiences', 'platform': 'GFG', 'url': 'https://www.geeksforgeeks.org/interview-experiences/', 'icon': 'fa-solid fa-comments'},
            {'title': 'Interviewing.io Mock Talks', 'platform': 'YouTube', 'url': 'https://www.youtube.com/@interviewingio', 'icon': 'fa-brands fa-youtube'}
        ]
    }
    
    personalized_resources = []
    # Logic: If gap score is low (< 70% of max), add resources
    thresholds = [14, 21, 14, 10, 10] # ~70% of max per category
    categories = ['foundation', 'coding', 'market', 'ai', 'career']
    
    for i, gap_score in enumerate(gaps):
        if gap_score < thresholds[i]:
            personalized_resources.extend(all_resources[categories[i]])
            
    # Always ensure at least 4 resources
    if len(personalized_resources) < 4:
        # Fill with general top-tier resources
        personalized_resources.extend(all_resources['coding'])
        personalized_resources.extend(all_resources['career'])
        
    # Limit to top 6 unique resources
    seen = set()
    unique_resources = []
    for r in personalized_resources:
        if r['url'] not in seen:
            unique_resources.append(r)
            seen.add(r['url'])
    
    return render_template('result.html', score=res.score, category=res.category, recommendations=recs, student=current_user, leaderboard=leaderboard, result_data=res, percentile=percentile, roadmap=roadmap, resources=unique_resources[:6])

@student.route('/history')
@login_required
def history():
    submissions = db.session.query(SurveyResponse, Result.score, Result.category)\
        .outerjoin(Result, SurveyResponse.student_id == Result.student_id)\
        .filter(SurveyResponse.student_id == current_user.id)\
        .order_by(SurveyResponse.id.desc()).all()
    
    # Format submissions for the template (template expects objects with score, category attributes)
    formatted_submissions = []
    for sr, score, category in submissions:
        sr.score = score
        sr.category = category
        formatted_submissions.append(sr)
        
    return render_template('history.html', submissions=formatted_submissions)

@student.route('/leaderboard')
@login_required
def leaderboard():
    # Fetch global rankings for top 50 students
    students = User.query.filter(User.role=='student', User.points > 0).order_by(User.points.desc()).limit(50).all()
    return render_template('leaderboard.html', students=students)

@student.route('/download_report')
@login_required
def download_report():
    res = Result.query.filter_by(student_id=current_user.id).first()
    if not res:
        return redirect(url_for('student.survey'))
        
    recs = [r.recommendation_text for r in Recommendation.query.filter_by(student_id=current_user.id).all()]
    
    pdf_buffer = generate_report_pdf(
        current_user.name, current_user.college, current_user.department, current_user.year,
        res.score, res.category, current_user.badges, current_user.points, recs
    )
    
    return send_file(pdf_buffer, as_attachment=True, download_name='academic_readiness_report.pdf', mimetype='application/pdf')

@student.route('/claim_certificate')
@login_required
def claim_certificate():
    res = Result.query.filter_by(student_id=current_user.id).first()
    if not res:
        return redirect(url_for('student.survey'))
        
    # Eligibility Logic: Score >= 80 and Verified
    if res.score < 80 or "❌" in res.validation_status:
        flash("You are not yet eligible for the Industry Ready Certification. Focus on your roadmap goals!", "warning")
        return redirect(url_for('student.result'))
        
    # Extract skills from resume if available
    skills = ["Digital Literacy", "Systematic Problem Solving", "Workforce Readiness"]
    # (Optional: fetch real skills from a parsed resume cache or AuditLog)
    
    pdf_buffer = generate_certificate_pdf(
        current_user.name, current_user.college, res.score, res.category, skills
    )
    
    return send_file(pdf_buffer, as_attachment=True, download_name='industry_ready_certificate.pdf', mimetype='application/pdf')

@student.route('/interview')
@login_required
def interview():
    res = Result.query.filter_by(student_id=current_user.id).first()
    if not res:
        return redirect(url_for('student.survey'))
    return render_template('interview.html', student=current_user, score=res.score, category=res.category)

    return render_template('interview.html', student=current_user, score=res.score, category=res.category)

@student.route('/retake_survey')
@login_required
def retake_survey():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    # Delete old results, survey responses, and recommendations
    Result.query.filter_by(student_id=current_user.id).delete()
    SurveyResponse.query.filter_by(student_id=current_user.id).delete()
    Recommendation.query.filter_by(student_id=current_user.id).delete()
    
    # Reset points for the new simulation if needed
    current_user.points = 0
    current_user.badges = 'Newcomer'
    
    db.session.commit()
    flash("Your past assessment data has been reset. You can now take the survey again!", "info")
    return redirect(url_for('student.survey'))

@student.route('/view_file/<path:filepath>')
@login_required
def view_file(filepath):
    # Ensure the path is within the uploads directory for security
    if not filepath.startswith('static/uploads'):
        return "Access Denied", 403
    return send_file(os.path.join(current_app.root_path, '..', '..', filepath))

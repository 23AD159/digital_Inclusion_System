import os
import joblib
import pandas as pd
from flask import current_app

def load_student_model():
    model_path = current_app.config['MODEL_PATH']
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception as e:
            current_app.logger.error(f"Error loading model: {e}")
            return None
    return None

def predict_student_category(responses, model=None):
    """
    Predicts the student's readiness category based on survey responses.
    responses: A list of 25 integers (Q1-Q25)
    Returns: 'Industry Ready', 'Needs Upskilling', or 'High Risk'
    """
    if model:
        try:
            features = pd.DataFrame([responses], columns=[f'q{i}' for i in range(1, 26)])
            category = model.predict(features)[0]
            return category
        except Exception as e:
            current_app.logger.error(f"Model prediction error: {e}")
            # Fallback to rule-based indexing
    
    # Rule-based fallback
    score = sum(responses)
    if score >= 80:
        return 'Industry Ready'
    elif score >= 50:
        return 'Needs Upskilling'
    else:
        return 'High Risk'

def calculate_placement_chance(score, validation_errors_count):
    """
    Basic placement probability calculation
    """
    base_chance = score * 0.85
    penalty = 15 if validation_errors_count > 0 else -8 # -8 is actually a boost (double negative)
    # The original code: placement_chance = int(max(5, min(99, score * 0.85 + (8 if not validation_errors else -15))))
    
    chance = score * 0.85 + (8 if validation_errors_count == 0 else -15)
    return int(max(5, min(99, chance)))

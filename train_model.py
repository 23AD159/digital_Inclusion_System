import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

os.makedirs('models', exist_ok=True)

print("Generating synthetic dataset with 500 samples for 25 features...")
np.random.seed(42)
num_samples = 500

# 25 questions grouped into 5 categories mapping to maximum score out of 100
# Cat 1 (Q1-Q5): max 4 each -> 20 pts
# Cat 2 (Q6-Q10): max 6 each -> 30 pts
# Cat 3 (Q11-Q15): max 4 each -> 20 pts
# Cat 4 (Q16-Q20): max 3 each -> 15 pts
# Cat 5 (Q21-Q25): max 3 each -> 15 pts

data = {}
for i in range(1, 6): data[f'q{i}'] = np.random.randint(0, 5, num_samples)    # 0 to 4
for i in range(6, 11): data[f'q{i}'] = np.random.randint(0, 7, num_samples)   # 0 to 6
for i in range(11, 16): data[f'q{i}'] = np.random.randint(0, 5, num_samples)  # 0 to 4
for i in range(16, 21): data[f'q{i}'] = np.random.randint(0, 4, num_samples)  # 0 to 3
for i in range(21, 26): data[f'q{i}'] = np.random.randint(0, 4, num_samples)  # 0 to 3

df = pd.DataFrame(data)
df['score'] = df.sum(axis=1)

def categorize(score):
    if score >= 80: return 'Industry Ready'
    elif score >= 50: return 'Needs Upskilling'
    else: return 'High Risk'

df['category'] = df['score'].apply(categorize)
print("Distribution of categories:")
print(df['category'].value_counts())

df.to_csv('dataset.csv', index=False)
print("Dataset saved to dataset.csv")

X = df.drop(columns=['score', 'category'])
y = df['category']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

model_path = 'models/model.pkl'
joblib.dump(clf, model_path)
print(f"Model saved efficiently using joblib to {model_path}!")

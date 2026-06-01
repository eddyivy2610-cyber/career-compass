import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from core.questionnaire_processor import process_questionnaire
from core.recommendation_engine import calculate_recommendation
from core.file_processor import process_file

print("Testing Backend Logic...")

data = {
    'Name': ['Musa', 'Ada'],
    'Math': [80, 60],
    'English': [70, 82],
    'Basic Science': [85, 55],
    'Business Studies': [45, 88],
    'Intro Tech': [78, 40]
}
df = pd.DataFrame(data)
df.to_csv('test_scores.csv', index=False)
print("Created test_scores.csv")

# Test file processor
parsed_df = process_file('test_scores.csv')
musa_data = parsed_df[parsed_df['Name'] == 'Musa'].iloc[0].drop('Name').to_dict()

print("Musa Data:", musa_data)

# Test questionnaire
responses = {
    "q1": "Strongly Agree",
    "q2": "Agree",
    "q3": "Neutral"
}
num_res = process_questionnaire(responses)
print("Questionnaire:", num_res)
skills_score = sum(num_res.values()) * 5
interests_score = sum(num_res.values()) * 5

# Test engine
result = calculate_recommendation(musa_data, skills_score, interests_score)
print("Result for Musa:", result)
print("All tests passed.")

import pandas as pd
import numpy as np
import os
import random

# Base student pool
student_names = [
    "John Doe", "Jane Smith", "Emeka Okafor", "Chidi Okafor", "Binta Bello",
    "Amina Musa", "Ibrahim Ali", "Samuel Peter", "David Mark", "Sarah James",
    "Michael Obi", "Grace John", "Daniel Moses", "Esther David", "Joseph Paul",
    "Mary Luke", "Peter Simon", "Paul Andrew", "Thomas James", "James John"
]

subjects = [
    "Mathematics", "English Language", "Basic Science", "Basic Technology",
    "Social Studies", "Civic Education", "Business Studies", "Computer Studies",
    "Agricultural Science", "Home Economics", "Cultural & Creative Arts", "CRS/IRS"
]
grades = ['A', 'B', 'C', 'D', 'E', 'F']
grade_weights = [0.15, 0.25, 0.3, 0.15, 0.1, 0.05] 

os.makedirs('mock_data', exist_ok=True)

classes = ['JS1', 'JS2', 'JS3']
terms = ['T1', 'T2', 'T3']

for cls in classes:
    for t in terms:
        if cls == 'JS1':
            current_students = student_names[0:16].copy()
        elif cls == 'JS2':
            current_students = student_names[2:18].copy()
        else:
            current_students = student_names[4:19].copy()
            
        # Randomly drop 1 student
        if random.random() > 0.3:
            current_students.pop(random.randint(0, len(current_students)-1))
            
        # Add a duplicate in JS1 T1 to test the new error
        if cls == 'JS1' and t == 'T1':
            current_students.append("John Doe") # Deliberate duplicate
            
        data = []
        for name in current_students:
            row = {'Name': name}
            for subj in subjects:
                row[subj] = np.random.choice(grades, p=grade_weights)
            data.append(row)
            
        df = pd.DataFrame(data)
        df.to_csv(f'mock_data/{cls}_{t}.csv', index=False)
        
print("Successfully generated 9 test CSV files in mock_data/")

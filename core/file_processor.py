import pandas as pd
import json
import os
import math

CACHE_DIR = 'cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def process_term_file(filepath, class_name, term):
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file format.")
        
    df.columns = [str(c).strip() for c in df.columns]
    
    name_col = next((c for c in df.columns if c.lower() in ['name', 'studentname', 'student_name']), None)
    
    if not name_col:
        raise ValueError(f"Could not find a 'Name' column in the file for {class_name} {term}.")
        
    df = df.dropna(subset=[name_col])
    
    name_counts = df[name_col].value_counts()
    duplicates = name_counts[name_counts > 1].index.tolist()
    if duplicates:
        raise ValueError(f"Duplicate names detected in this file: {', '.join(duplicates)}. Please edit your file to add initials (e.g. '{duplicates[0]} A') to differentiate them before uploading.")

    ignore_cols = [name_col]
    id_col = next((c for c in df.columns if c.lower() in ['id', 'studentid', 'student_id', 's/n']), None)
    if id_col:
        ignore_cols.append(id_col)
        
    subject_cols = [c for c in df.columns if c not in ignore_cols]
    grade_map = {'A': 85, 'B': 65, 'C': 55, 'D': 47, 'E': 42, 'F': 20}
    
    students_processed = 0
    
    for _, row in df.iterrows():
        name = str(row[name_col]).strip()
        safe_name = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        cache_path = os.path.join(CACHE_DIR, f"{safe_name}.json")
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                student_data = json.load(f)
        else:
            student_data = {
                "student_id": safe_name,
                "name": name,
                "records": {}
            }
            
        if class_name not in student_data["records"]:
            student_data["records"][class_name] = {}
            
        student_data["records"][class_name][term] = {}
        
        for subj in subject_cols:
            val = row[subj]
            if not pd.isna(val):
                val_str = str(val).strip().upper()
                if val_str in grade_map:
                    student_data["records"][class_name][term][subj] = grade_map[val_str]
                else:
                    try:
                        score = float(val)
                        student_data["records"][class_name][term][subj] = score
                    except ValueError:
                        pass 
                    
        with open(cache_path, 'w') as f:
            json.dump(student_data, f)
            
        students_processed += 1
        
    return students_processed

def get_cached_student(safe_name):
    cache_path = os.path.join(CACHE_DIR, f"{safe_name}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    return None

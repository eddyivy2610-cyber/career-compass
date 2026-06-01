def evaluate_student(student_data, technical_skills_score=3):
    """
    student_data: dict with "student_id", "name", "records"
    records: nested dicts: {'JS1': {'Term1': {'Math': 80, 'English': 75}}}
    technical_skills_score: numerical (1-5) representing manual technical aptitude entry.
    """
    records = student_data.get('records', {})
    
    # Group subjects
    categories = {
        "Science": ["Math", "Mathematics", "Basic Science", "Basic Technology", "Computer Studies", "Physical and Health Education", "PHE", "Intro Tech"],
        "Arts": ["English", "English Language", "Literature", "Literature in English", "Social Studies", "Civic Education", "CRS", "IRS", "French", "History", "Cultural and Creative Arts", "CCA", "Hausa", "Igbo", "Yoruba"],
        "Commercial": ["Math", "Mathematics", "Business Studies", "Economics", "Commerce"],
        "Vocational": ["Basic Technology", "Intro Tech", "Home Economics", "Agricultural Science", "Agric Science", "Cultural and Creative Arts", "CCA", "Fine Art", "Music"]
    }
    
    # Aggregate scores per subject across all terms/classes
    subject_scores = {}
    for class_name, terms in records.items():
        for term_name, subjects in terms.items():
            for subj, score in subjects.items():
                # Normalize subject name for better matching
                subj_clean = str(subj).strip()
                if subj_clean not in subject_scores:
                    subject_scores[subj_clean] = []
                subject_scores[subj_clean].append(float(score))
        
    avg_subject_scores = {subj: sum(scores)/len(scores) for subj, scores in subject_scores.items()}
    
    # Completeness Check
    core_subjects = ["Mathematics", "Math", "English", "English Language", "Basic Science"]
    found_core = [subj for subj in core_subjects if subj in avg_subject_scores]
    
    if len(found_core) >= 3:
        confidence = "High"
        confidence_msg = "Complete core records available."
    elif len(found_core) > 0:
        confidence = "Medium"
        confidence_msg = "Some core subjects missing. Manual review recommended."
    else:
        confidence = "Low"
        confidence_msg = "Insufficient data. Core subjects missing."
        
    # Calculate category averages
    category_academic_scores = {}
    for category, subjects in categories.items():
        valid_scores = [avg_subject_scores[s] for s in subjects if s in avg_subject_scores]
        if valid_scores:
            category_academic_scores[category] = sum(valid_scores) / len(valid_scores)
        else:
            category_academic_scores[category] = 0
            
    # Combine scores. Suitability = (Weight * Academic) + (Weight * Technical Skill)
    tech_score_100 = float(technical_skills_score) * 20
    suitability_scores = {}
    
    for category in categories.keys():
        academic = category_academic_scores.get(category, 0)
        if category in ["Vocational", "Science"]:
            suitability_scores[category] = (0.6 * academic) + (0.4 * tech_score_100)
        else:
            suitability_scores[category] = (0.8 * academic) + (0.2 * tech_score_100)
            
    recommended_path = max(suitability_scores, key=suitability_scores.get)
    
    total_score = sum(suitability_scores.values())
    if total_score == 0: total_score = 1
    path_scores = {k: round((v / total_score) * 100) for k, v in suitability_scores.items()}
    
    sorted_subjects = sorted(avg_subject_scores.items(), key=lambda x: x[1], reverse=True)
    top_subjects = [subj for subj, score in sorted_subjects[:3]]
    
    # Basic Trend Analysis
    class_averages = {}
    for class_name, terms in records.items():
        cls = str(class_name).upper().strip()
        if cls not in class_averages:
            class_averages[cls] = []
        for term_name, subjects in terms.items():
            class_averages[cls].extend(subjects.values())
    
    trend_msg = "Stable performance."
    if 'JS1' in class_averages and 'JS3' in class_averages:
        js1_avg = sum(class_averages['JS1'])/len(class_averages['JS1'])
        js3_avg = sum(class_averages['JS3'])/len(class_averages['JS3'])
        if js3_avg > js1_avg + 5:
            trend_msg = "Strong upward progression detected from JS1 to JS3."
        elif js3_avg < js1_avg - 5:
            trend_msg = "Downward performance trend detected. Needs attention."
            
    reason = [
        f"Strongest performance in {recommended_path} related subjects.",
        trend_msg,
        confidence_msg
    ]
    
    careers = {
        "Science": ["Engineering", "Medicine", "Computer Science"],
        "Arts": ["Law", "Mass Communication", "Linguistics"],
        "Commercial": ["Accounting", "Banking", "Business Administration"],
        "Vocational": ["Fashion Design", "Catering", "Automobile Engineering", "Technical Crafts"]
    }
    
    return {
        "recommended_path": recommended_path,
        "score": round(suitability_scores[recommended_path], 2),
        "confidence": confidence,
        "reason": reason,
        "careers": careers.get(recommended_path, []),
        "academic_breakdown": {k: round(v, 2) for k, v in category_academic_scores.items()},
        "top_subjects": top_subjects,
        "path_scores": path_scores
    }

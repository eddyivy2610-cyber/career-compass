import os
from flask import Flask, request, jsonify, render_template
from core.file_processor import process_term_file, get_cached_student, CACHE_DIR
from core.recommendation_engine import evaluate_student
from core.database import save_recommendation, get_all_recommendations, get_report_sessions, get_recommendations_by_session, delete_session
from datetime import datetime
import json
import io
import csv
from flask import Response

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compass')
def compass():
    return render_template('compass_selection.html')

@app.route('/compass_batch')
def compass_batch():
    return render_template('compass.html')

@app.route('/compass_single')
def compass_single():
    return render_template('compass_single.html')

@app.route('/reports')
def reports():
    sessions = get_report_sessions()
    return render_template('reports.html', sessions=sessions)

@app.route('/api/report_details/<session_tag>')
def report_details_api(session_tag):
    recs = get_recommendations_by_session(session_tag)
    for r in recs:
        try:
            r['top_subjects'] = json.loads(r['top_subjects']) if r['top_subjects'] else []
            r['path_scores'] = json.loads(r['path_scores']) if r['path_scores'] else {}
        except:
            r['top_subjects'] = []
            r['path_scores'] = {}
    recs = sorted(recs, key=lambda x: x.get('student_name', '').lower())
    return jsonify(recs)

@app.route('/report/<session_tag>')
def report_page(session_tag):
    return render_template('report_details.html', session_tag=session_tag)

@app.route('/api/delete_report/<session_tag>', methods=['DELETE'])
def api_delete_report(session_tag):
    delete_session(session_tag)
    return jsonify({"message": "Deleted successfully"}), 200

@app.route('/export_reports/<session_tag>')
def export_reports(session_tag):
    recommendations = get_recommendations_by_session(session_tag)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Student Name', 'Recommended Path', 'Date'])
    for r in recommendations:
        writer.writerow([r['id'], r['student_name'], r['recommended_path'], r['date']])
    
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": f"attachment; filename=report_{session_tag}.csv"})

@app.route('/upload_term_file/<class_name>/<term>', methods=['POST'])
def upload_term_file(class_name, term):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    try:
        processed_count = process_term_file(filepath, class_name, term)
        return jsonify({"success": True, "processed": processed_count})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/check_exemptions')
def check_exemptions():
    exemptions = []
    if os.path.exists(CACHE_DIR):
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                student_id = filename[:-5]
                s_data = get_cached_student(student_id)
                if not s_data: continue
                
                records = s_data.get('records', {})
                missing = []
                for cls in ['JS1', 'JS2', 'JS3']:
                    if cls not in records:
                        missing.append(cls)
                    else:
                        for t in ['Term1', 'Term2', 'Term3']:
                            if t not in records[cls]:
                                missing.append(f"{cls}-{t}")
                                
                if missing:
                    exemptions.append({
                        "student_id": student_id,
                        "name": s_data.get('name', student_id),
                        "missing": ", ".join(missing)
                    })
    return jsonify(exemptions)

@app.route('/evaluate/<student_id>', methods=['POST'])
def evaluate(student_id):
    student_data = get_cached_student(student_id)
    if not student_data:
        return jsonify({"error": "Student data not found in cache"}), 404
        
    data = request.json or {}
    tech_skills = data.get('technical_skills_score', 3)
    
    try:
        result = evaluate_student(student_data, float(tech_skills))
        result['student_id'] = student_id
        result['name'] = student_data['name']
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/override', methods=['POST'])
def override():
    data = request.json
    student_name = data.get('student_name')
    recommended_path = data.get('recommended_path')
    notes = data.get('notes', '')
    
    if not student_name or not recommended_path:
        return jsonify({"error": "Missing data"}), 400
        
    final_path = f"{recommended_path} (Notes: {notes})" if notes else recommended_path
    save_recommendation(student_name, final_path)
    
    return jsonify({"message": "Override saved successfully"}), 200

@app.route('/upload_single_student', methods=['POST'])
def upload_single_student():
    data = request.json
    name = str(data.get('name', '')).strip()
    subjects_data = data.get('subjects', []) 
    
    if not name:
        return jsonify({"error": "Student Name is required"}), 400
        
    grade_map = {
        'A': 85,
        'B': 65,
        'C': 55,
        'D': 47,
        'E': 42,
        'F': 20
    }
    
    records = {
        'JS1': {'Term1': {}, 'Term2': {}, 'Term3': {}},
        'JS2': {'Term1': {}, 'Term2': {}, 'Term3': {}},
        'JS3': {'Term1': {}, 'Term2': {}, 'Term3': {}}
    }
    
    for row in subjects_data:
        subj = row.get('subject', '').strip()
        if not subj: continue
        
        for cls in ['JS1', 'JS2', 'JS3']:
            for t in ['T1', 'T2', 'T3']:
                term_key = f"Term{t[1]}"
                val = row.get(f"{cls}_{t}")
                if val and val in grade_map:
                    records[cls][term_key][subj] = grade_map[val]

    safe_name = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    student_data = {
        "student_id": safe_name,
        "name": name,
        "records": records
    }
    
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        
    cache_path = os.path.join(CACHE_DIR, f"{safe_name}.json")
    with open(cache_path, 'w') as f:
        json.dump(student_data, f)
        
    session_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    res = evaluate_student(student_data, 3)
    
    save_recommendation(
        student_data['name'], 
        res['recommended_path'], 
        session_tag, 
        json.dumps(res.get('top_subjects', [])), 
        json.dumps(res.get('path_scores', {}))
    )
    
    return jsonify({"success": True, "session_tag": session_tag})

@app.route('/run_engine', methods=['POST'])
def run_engine():
    session_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []
    
    if os.path.exists(CACHE_DIR):
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                s_id = filename[:-5]
                s_data = get_cached_student(s_id)
                if s_data:
                    res = evaluate_student(s_data, 3)
                    res['student_id'] = s_id
                    res['name'] = s_data['name']
                    save_recommendation(
                        s_data['name'], 
                        res['recommended_path'], 
                        session_tag, 
                        json.dumps(res.get('top_subjects', [])), 
                        json.dumps(res.get('path_scores', {}))
                    )
                    results.append(res)
                        
    return jsonify({
        "success": True, 
        "processed": len(results),
        "session_tag": session_tag
    })

if __name__ == '__main__':
    app.run(debug=True)

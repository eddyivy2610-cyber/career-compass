# CareerCompass

**CareerCompass** is a data-driven career recommendation platform designed for school counselors in Nigeria. The platform analyzes a student's academic performance from JS1 through JS3, factors in manual assessments of technical skills, and automatically recommends the most suitable career path (Science, Arts, Commercial, or Vocational) for Senior Secondary School.

## Features

- **Batch Upload**: Upload `.csv` or `.xlsx` files containing terminal examination results for entire classes using a simple 9-slot grid system.
- **Single Entry Form**: Manually input an individual student's records term-by-term using a dynamic, interactive form.
- **Smart Recommendation Engine**: Processes core subjects, generates suitability scores, checks for missing data/exemptions, and identifies academic trends (e.g., upward progression).
- **Counselor Dashboard**: View beautifully formatted, printable reports for all students processed within a session.
- **Data Export**: Export finalized recommendations and path assignments to CSV.
- **Manual Overrides**: Counselors can override system recommendations with custom notes if external factors (like student interest or parental request) need to be considered.

## Technology Stack

- **Backend**: Python, Flask, Pandas (for robust CSV/Excel processing)
- **Database**: SQLite (built-in, zero-configuration)
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (No heavy frameworks, fast load times)
- **Production Server**: Waitress (WSGI server for Windows)

## Directory Structure

```text
career-compass/
├── app.py                      # Main Flask application definitions & routes
├── run.py                      # Entry point for production/development running
├── core/                       # Business logic & database layer
│   ├── database.py             # SQLite DB operations
│   ├── file_processor.py       # CSV/Excel parsing logic
│   ├── questionnaire_processor.py # Interest questionnaire logic
│   └── recommendation_engine.py# Core algorithm for career path prediction
├── static/                     # CSS, JS, and Images
├── templates/                  # HTML templates (Jinja2)
├── tests/                      # Mock data and test scripts
├── docs/                       # Project documentation
├── .env                        # Environment variables
└── requirements.txt            # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.8+
- Pip (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/eddyivy2610-cyber/career-compass.git
   cd career-compass
   ```

2. **Create a virtual environment (Optional but recommended)**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Ensure the `.env` file exists in the root directory. For development, you can set `FLASK_ENV=development`. For production, set it to `production`.

### Running the Application

To start the application, use the provided `run.py` script. It automatically detects the environment and uses the Waitress WSGI server if in production mode.

```bash
python run.py
```

Open your browser and navigate to `http://localhost:5000` to view the application.

## Usage Guide
1. **Home/Landing Page**: Introduces the platform. Click "Get Started".
2. **Compass Selection**: Choose either **Batch Upload** (for uploading CSV/Excel sheets) or **Single Entry** (for typing in a single student's grades).
3. **Data Processing**: The system parses the data, alerts you of any missing term records, and runs the recommendation engine.
4. **Reports**: View the final recommendations. You can filter the results, edit individual recommendations, or export the entire session to a CSV file for printing or sharing with parents.



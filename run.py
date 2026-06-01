import os
from dotenv import load_dotenv

load_dotenv()

from app import app

if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    
    if env == 'production':
        print(f"Starting Waitress production server on port {port}...")
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        print(f"Starting Flask development server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=True)

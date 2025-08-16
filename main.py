"""
TaskWeave AI - Main Flask application entry point
"""
from simple_app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

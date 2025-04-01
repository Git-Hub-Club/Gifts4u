import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_testing")

# Load data from JSON file
def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty/invalid, return empty data structure
        return {
            "categories": [
                {"id": "movies", "name": "Movies"},
                {"id": "tv", "name": "TV Shows"},
                {"id": "games", "name": "Games"},
                {"id": "music", "name": "Music"},
                {"id": "applications", "name": "Applications"},
                {"id": "documentaries", "name": "Documentaries"},
                {"id": "other", "name": "Other"}
            ],
            "files": []
        }

# Routes
@app.route('/')
def index():
    data = load_data()
    latest_files = sorted(data['files'], key=lambda x: x.get('added_date', ''), reverse=True)[:20]
    popular_files = sorted(data['files'], key=lambda x: x.get('downloads', 0), reverse=True)[:20]
    return render_template('index.html', 
                          categories=data['categories'], 
                          latest_files=latest_files, 
                          popular_files=popular_files)

@app.route('/category/<category_id>')
def category(category_id):
    data = load_data()
    category_name = next((cat['name'] for cat in data['categories'] if cat['id'] == category_id), "Unknown Category")
    category_files = [file for file in data['files'] if file.get('category_id') == category_id]
    
    # Sort files by added date (descending)
    category_files = sorted(category_files, key=lambda x: x.get('added_date', ''), reverse=True)
    
    return render_template('category.html', 
                          categories=data['categories'], 
                          category_id=category_id,
                          category_name=category_name,
                          files=category_files)

@app.route('/file/<file_id>')
def file_details(file_id):
    data = load_data()
    file = next((f for f in data['files'] if f.get('id') == file_id), None)
    
    if not file:
        flash('File not found')
        return redirect(url_for('index'))
    
    category_name = next((cat['name'] for cat in data['categories'] if cat['id'] == file.get('category_id')), "Unknown")
    
    return render_template('file.html', 
                          categories=data['categories'], 
                          file=file,
                          category_name=category_name)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return redirect(url_for('index'))
    
    data = load_data()
    results = [
        file for file in data['files'] 
        if query in file.get('name', '').lower() or 
           query in file.get('description', '').lower()
    ]
    
    # Sort results by relevance (name matches first, then description matches)
    results.sort(key=lambda x: (
        0 if query in x.get('name', '').lower() else 1,
        x.get('downloads', 0)
    ), reverse=True)
    
    return render_template('search.html', 
                          categories=data['categories'], 
                          query=query,
                          results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

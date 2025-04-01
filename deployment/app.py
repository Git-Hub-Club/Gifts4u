import os
import json
import uuid
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_testing")

# Admin credentials
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "omdas6633")  # Custom password

# Load data from JSON file
def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty/invalid, return empty data structure
        return {
            "categories": [
                {"id": "fiction", "name": "Fiction"},
                {"id": "nonfiction", "name": "Non-Fiction"},
                {"id": "academic", "name": "Academic & Textbooks"},
                {"id": "scifi-fantasy", "name": "Sci-Fi & Fantasy"},
                {"id": "biography", "name": "Biography & Memoir"},
                {"id": "self-help", "name": "Self-Help & Personal Development"},
                {"id": "other", "name": "Other eBooks"}
            ],
            "files": []
        }

# Save data to JSON file
def save_data(data):
    try:
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        return False

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

# Admin helper function
def is_admin():
    return session.get('admin_logged_in', False)

# Admin auth routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin():
        return redirect(url_for('admin_dashboard'))
        
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('You have been logged in as admin')
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid password'
    
    return render_template('admin_login.html', categories=load_data()['categories'], error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out')
    return redirect(url_for('index'))

# Admin dashboard
@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    search_query = request.args.get('search', '').lower()
    
    files = data['files']
    if search_query:
        files = [
            file for file in files
            if search_query in file.get('name', '').lower() or
               search_query in file.get('description', '').lower()
        ]
    
    # Sort files by added date (newest first)
    files = sorted(files, key=lambda x: x.get('added_date', ''), reverse=True)
    
    # Add category name to each file
    for file in files:
        file['category_name'] = next(
            (cat['name'] for cat in data['categories'] if cat['id'] == file.get('category_id')),
            "Unknown"
        )
    
    return render_template('admin_dashboard.html', categories=data['categories'], files=files)

# Add new file
@app.route('/admin/files/add', methods=['GET', 'POST'])
def admin_add_file():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    
    if request.method == 'POST':
        # Get form data
        file_id = request.form.get('id')
        
        # Check if ID already exists
        if any(f['id'] == file_id for f in data['files']):
            flash(f'A file with ID "{file_id}" already exists')
            return render_template('admin_file_form.html', categories=data['categories'], file=None)
        
        # Build links array
        external_links = []
        link_titles = request.form.getlist('link_titles[]')
        link_urls = request.form.getlist('link_urls[]')
        
        for i in range(len(link_titles)):
            if i < len(link_urls):
                external_links.append({
                    "title": link_titles[i],
                    "url": link_urls[i]
                })
        
        # Build file info object
        file_info = {}
        info_keys = request.form.getlist('info_keys[]')
        info_values = request.form.getlist('info_values[]')
        
        for i in range(len(info_keys)):
            if i < len(info_values) and info_keys[i]:
                file_info[info_keys[i]] = info_values[i]
        
        # Create new file object
        new_file = {
            "id": file_id,
            "name": request.form.get('name'),
            "category_id": request.form.get('category_id'),
            "description": request.form.get('description'),
            "size": request.form.get('size'),
            "added_date": request.form.get('added_date'),
            "downloads": int(request.form.get('downloads', 0)),
            "external_links": external_links,
            "file_info": file_info
        }
        
        # Add file to data
        data['files'].append(new_file)
        
        # Save data
        if save_data(data):
            flash(f'File "{new_file["name"]}" added successfully')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Error saving file data')
    
    return render_template('admin_file_form.html', categories=data['categories'], file=None)

# Edit file
@app.route('/admin/files/edit/<file_id>', methods=['GET', 'POST'])
def admin_edit_file(file_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    file = next((f for f in data['files'] if f.get('id') == file_id), None)
    
    if not file:
        flash('File not found')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # Build links array
        external_links = []
        link_titles = request.form.getlist('link_titles[]')
        link_urls = request.form.getlist('link_urls[]')
        
        for i in range(len(link_titles)):
            if i < len(link_urls):
                external_links.append({
                    "title": link_titles[i],
                    "url": link_urls[i]
                })
        
        # Build file info object
        file_info = {}
        info_keys = request.form.getlist('info_keys[]')
        info_values = request.form.getlist('info_values[]')
        
        for i in range(len(info_keys)):
            if i < len(info_values) and info_keys[i]:
                file_info[info_keys[i]] = info_values[i]
        
        # Update file
        file_index = next((i for i, f in enumerate(data['files']) if f.get('id') == file_id), None)
        if file_index is not None:
            data['files'][file_index] = {
                "id": file_id,  # ID cannot be changed
                "name": request.form.get('name'),
                "category_id": request.form.get('category_id'),
                "description": request.form.get('description'),
                "size": request.form.get('size'),
                "added_date": request.form.get('added_date'),
                "downloads": int(request.form.get('downloads', 0)),
                "external_links": external_links,
                "file_info": file_info
            }
            
            # Save data
            if save_data(data):
                flash(f'File "{data["files"][file_index]["name"]}" updated successfully')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Error saving file data')
    
    return render_template('admin_file_form.html', categories=data['categories'], file=file)

# Delete file
@app.route('/admin/files/delete/<file_id>')
def admin_delete_file(file_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    file_index = next((i for i, f in enumerate(data['files']) if f.get('id') == file_id), None)
    
    if file_index is not None:
        file_name = data['files'][file_index]['name']
        data['files'].pop(file_index)
        
        if save_data(data):
            flash(f'File "{file_name}" deleted successfully')
        else:
            flash('Error deleting file')
    else:
        flash('File not found')
    
    return redirect(url_for('admin_dashboard'))

# Manage categories
@app.route('/admin/categories')
def admin_manage_categories():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    
    # Count files in each category and calculate total downloads
    categories_with_stats = []
    for category in data['categories']:
        category_files = [f for f in data['files'] if f.get('category_id') == category['id']]
        file_count = len(category_files)
        total_downloads = sum(f.get('downloads', 0) for f in category_files)
        
        categories_with_stats.append({
            'id': category['id'],
            'name': category['name'],
            'file_count': file_count,
            'total_downloads': total_downloads
        })
    
    return render_template('admin_categories.html', 
                          categories=data['categories'],
                          categories_with_count=categories_with_stats)

@app.route('/admin/categories/reorder', methods=['POST'])
def admin_reorder_categories():
    if not is_admin():
        return {'success': False, 'message': 'Unauthorized'}, 401
    
    data = load_data()
    category_ids = request.json.get('category_ids', [])
    
    if not category_ids:
        return {'success': False, 'message': 'No category IDs provided'}, 400
    
    # Create a new ordered categories list
    new_categories = []
    for category_id in category_ids:
        # Find the category in the original list
        category = next((c for c in data['categories'] if c['id'] == category_id), None)
        if category:
            new_categories.append(category)
    
    # Add any categories that weren't in the ordered list (should not happen, but just in case)
    for category in data['categories']:
        if category['id'] not in category_ids:
            new_categories.append(category)
    
    # Replace categories with the new ordered list
    data['categories'] = new_categories
    
    # Save data
    if save_data(data):
        return {'success': True, 'message': 'Categories reordered successfully'}
    else:
        return {'success': False, 'message': 'Error saving category order'}, 500

# Add category
@app.route('/admin/categories/add', methods=['POST'])
def admin_add_category():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    category_id = request.form.get('category_id', '').strip()
    category_name = request.form.get('category_name', '').strip()
    
    # Validate inputs
    if not category_id or not category_name:
        flash('Category ID and name are required')
        return redirect(url_for('admin_manage_categories'))
    
    # Validate format
    import re
    if not re.match(r'^[a-z0-9-]+$', category_id):
        flash('Category ID must contain only lowercase letters, numbers, and hyphens')
        return redirect(url_for('admin_manage_categories'))
    
    # Check if category ID already exists
    if any(c['id'] == category_id for c in data['categories']):
        flash(f'A category with ID "{category_id}" already exists')
        return redirect(url_for('admin_manage_categories'))
    
    # Add category
    data['categories'].append({
        'id': category_id,
        'name': category_name
    })
    
    # Save data
    if save_data(data):
        flash(f'Category "{category_name}" added successfully')
    else:
        flash('Error adding category')
    
    return redirect(url_for('admin_manage_categories'))

# Edit category
@app.route('/admin/categories/edit/<category_id>', methods=['POST'])
def admin_edit_category(category_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    category_name = request.form.get('category_name', '').strip()
    
    # Validate input
    if not category_name:
        flash('Category name is required')
        return redirect(url_for('admin_manage_categories'))
    
    category_index = next((i for i, c in enumerate(data['categories']) if c.get('id') == category_id), None)
    
    if category_index is not None:
        data['categories'][category_index]['name'] = category_name
        
        if save_data(data):
            flash(f'Category updated successfully')
        else:
            flash('Error updating category')
    else:
        flash('Category not found')
    
    return redirect(url_for('admin_manage_categories'))

# Delete category
@app.route('/admin/categories/delete/<category_id>')
def admin_delete_category(category_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    data = load_data()
    
    # Check if category has files
    if any(f.get('category_id') == category_id for f in data['files']):
        flash('Cannot delete category that contains files')
        return redirect(url_for('admin_manage_categories'))
    
    category_index = next((i for i, c in enumerate(data['categories']) if c.get('id') == category_id), None)
    
    if category_index is not None:
        category_name = data['categories'][category_index]['name']
        data['categories'].pop(category_index)
        
        if save_data(data):
            flash(f'Category "{category_name}" deleted successfully')
        else:
            flash('Error deleting category')
    else:
        flash('Category not found')
    
    return redirect(url_for('admin_manage_categories'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

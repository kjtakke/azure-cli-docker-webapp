import os
from flask import Flask, send_from_directory, abort, current_app, redirect, url_for, request, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import json
port = os.environ.get('PORT', 80)
app = Flask(__name__)
auth = HTTPBasicAuth()
home = "index.html"

# Replace these with your desired username and password
users = {
    "admin": generate_password_hash("user"),
    "va": generate_password_hash("password")
}

# Load search index
with open('templates/search/search_index.json', 'r', encoding='utf-8') as f:
    search_index = json.load(f)

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

@app.route('/')
@auth.login_required
def index():
    return redirect(url_for('documentation', filename=home))

@app.route('/search', methods=['GET'])
@auth.login_required
def search():
    query = request.args.get('q', '').lower()
    results = []
    if query:
        for entry in search_index:
            if query in entry['title'].lower() or query in entry['body'].lower():
                results.append(entry)
    return render_template('search/search_index.html', query=query, results=results)

@app.route('/docs/<path:filename>')
@auth.login_required
def documentation(filename):
    full_path = os.path.join(current_app.root_path, 'static/docs', filename)

    if os.path.isfile(full_path):
        return send_from_directory('static/docs', filename)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

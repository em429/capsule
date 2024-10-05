#!/usr/bin/env python3
# A tiny webapp to display highlights by querying Calibre's metadata.db

import os
import sqlite3
import json
from flask import Flask, jsonify, render_template_string, request, abort

# Set default DB path and allow overwriting with an environment variable
DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), "R", "books", "metadata.db")
DB_PATH = os.getenv("BOOKS_DB_PATH", DEFAULT_DB_PATH)

# Initialize Flask app
app = Flask(__name__)

# File to store favorites
FAVORITES_FILE = 'favorites.json'

# Load favorites from file
def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save favorites to file
def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w') as f:
        json.dump(favorites, f)

# Query function to get 3 random results
def get_random_annotations():
    query = """
    SELECT a.id, a.searchable_text, b.title, b.id as book_id
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.searchable_text != ''
    ORDER BY RANDOM()
    LIMIT 3;
    """
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    favorites = load_favorites()
    return [{
        "id": row["id"],
        "searchable_text": row["searchable_text"], 
        "title": row["title"], 
        "book_id": row["book_id"],
        "is_favorite": str(row["id"]) in favorites
    } for row in rows]

# Query function to get all books with annotations
def get_books_with_annotations():
    query = """
    SELECT DISTINCT b.id, b.title
    FROM books b
    JOIN annotations a ON a.book = b.id
    WHERE a.searchable_text != ''
    ORDER BY b.title;
    """
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    return [{"id": row["id"], "title": row["title"]} for row in rows]

# Query function to get all annotations for a specific book
def get_book_annotations(book_id):
    query = """
    SELECT a.id, a.searchable_text, b.title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.book = ? AND a.searchable_text != ''
    ORDER BY a.timestamp;
    """
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, (book_id,))
        rows = cur.fetchall()
    
    if not rows:
        return None
    
    favorites = load_favorites()
    return {
        "title": rows[0]["title"],
        "annotations": [{
            "id": row["id"],
            "text": row["searchable_text"],
            "is_favorite": str(row["id"]) in favorites
        } for row in rows]
    }

@app.route('/annotations', methods=['GET'])
def get_annotations():
    try:
        annotations = get_random_annotations()
        return jsonify({"results": annotations}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    try:
        annotations = get_random_annotations()
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Random Annotations</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 0;
                    line-height: 1.6;
                    max-width: 600px;
                }
                .annotation-block {
                    border-bottom: 1px solid #ddd;
                    padding: 10px 0;
                }
                h2 {
                    font-size: 1.2em;
                    margin: 0 0 10px 0;
                }
                p {
                    margin: 0;
                    color: #555;
                }
                .books-link {
                    display: block;
                    margin-top: 20px;
                    font-weight: bold;
                }
                .star-btn {
                    background: none;
                    color: #9d9d9d;
                    border: none;
                    font-size: 1.5em;
                    cursor: pointer;
                }
                .star-btn.favorited {
                    color: gold;
                }
            </style>
        </head>
        <body>
            <a href="/books" class="books-link">Back to book list</a>
            <h1>Random Annotations</h1>
            <div id="annotations-list">
                {% for annotation in annotations %}
                <div class="annotation-block">
                    <a href="/book/{{ annotation.book_id }}">
                      <h2>{{ annotation.title }}</h2>
                    </a>
                    <p>{{ annotation.searchable_text }}</p>
                    <button class="star-btn {% if annotation.is_favorite %}favorited{% endif %}" 
                            onclick="toggleFavorite({{ annotation.id }}, this)">
                        &#9733;
                    </button>
                </div>
                {% endfor %}
            </div>
            <script>
                function toggleFavorite(annotationId, button) {
                    fetch('/toggle_favorite/' + annotationId, {method: 'POST'})
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                button.classList.toggle('favorited');
                            }
                        });
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(html_template, annotations=annotations)
    except Exception as e:
        return f"<p>Error: {str(e)}</p>", 500

@app.route('/books', methods=['GET'])
def books_list():
    try:
        books = get_books_with_annotations()
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Books with Annotations</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 0;
                    line-height: 1.6;
                    max-width: 600px;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin-bottom: 10px;
                }
                a {
                    color: #0066cc;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <a href="/">Back to random annotations</a>
            <h1>Books with Annotations</h1>
            <ul>
                {% for book in books %}
                <li><a href="/book/{{ book.id }}">{{ book.title }}</a></li>
                {% endfor %}
            </ul>
        </body>
        </html>
        """
        return render_template_string(html_template, books=books)
    except Exception as e:
        return f"<p>Error: {str(e)}</p>", 500

@app.route('/book/<int:book_id>', methods=['GET'])
def book_annotations(book_id):
    try:
        book_data = get_book_annotations(book_id)
        if book_data is None:
            abort(404)
        
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ book_data.title }} - Annotations</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 0;
                    line-height: 1.6;
                    max-width: 600px;
                }
                .annotation {
                    border-bottom: 1px solid #ddd;
                    padding: 10px 0;
                }
                h1 {
                    font-size: 1.5em;
                    margin-bottom: 20px;
                }
                p {
                    margin: 0;
                    color: #333;
                }
                .star-btn {
                    background: none;
                    border: none;
                    font-size: 1.5em;
                    cursor: pointer;
                }
                .star-btn.favorited {
                    color: gold;
                }
            </style>
        </head>
        <body>
            <h1>{{ book_data.title }}</h1>
            <div id="annotations-list">
                {% for annotation in book_data.annotations %}
                <div class="annotation">
                    <p>{{ annotation.text }}</p>
                    <button class="star-btn {% if annotation.is_favorite %}favorited{% endif %}" 
                            onclick="toggleFavorite({{ annotation.id }}, this)">
                        &#9733;
                    </button>
                </div>
                {% endfor %}
            </div>
            <a href="/books">Back to books list</a>
            <script>
                function toggleFavorite(annotationId, button) {
                    fetch('/toggle_favorite/' + annotationId, {method: 'POST'})
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                button.classList.toggle('favorited');
                            }
                        });
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(html_template, book_data=book_data)
    except Exception as e:
        return f"<p>Error: {str(e)}</p>", 500

@app.route('/toggle_favorite/<int:annotation_id>', methods=['POST'])
def toggle_favorite(annotation_id):
    favorites = load_favorites()
    annotation_id_str = str(annotation_id)
    
    if annotation_id_str in favorites:
        del favorites[annotation_id_str]
    else:
        favorites[annotation_id_str] = True
    
    save_favorites(favorites)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

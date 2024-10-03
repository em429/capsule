import os
import sqlite3
import json
from flask import Flask, jsonify, render_template_string

# Set default DB path and allow overwriting with an environment variable
DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), "R", "books", "metadata.db")
DB_PATH = os.getenv("BOOKS_DB_PATH", DEFAULT_DB_PATH)

# Initialize Flask app
app = Flask(__name__)

# Query function to get 3 random results
def get_random_annotations():
    query = """
    SELECT a.searchable_text, b.title
    FROM annotations a
    JOIN books b ON a.book = b.id
    WHERE a.searchable_text != ''
    ORDER BY RANDOM()
    LIMIT 3;
    """
    
    # Connect to the SQLite database
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # This allows us to return the result as a dictionary
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    
    # Convert the rows to a list of dictionaries
    results = [{"searchable_text": row["searchable_text"], "title": row["title"]} for row in rows]
    return results

# Flask route to serve the data as JSON
@app.route('/annotations', methods=['GET'])
def get_annotations():
    try:
        annotations = get_random_annotations()
        return jsonify({"results": annotations}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Root route to display the data as HTML in a mobile-friendly format
@app.route('/', methods=['GET'])
def index():
    try:
        annotations = get_random_annotations()

        # Minimal HTML template for mobile-friendly display
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Annotations</title>
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
            </style>
        </head>
        <body>
            <h1>Random Annotations</h1>
            <div id="annotations-list">
                {% for annotation in annotations %}
                <div class="annotation-block">
                    <h2>{{ annotation.title }}</h2>
                    <p>{{ annotation.searchable_text }}</p>
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
        """

        # Render the HTML with the annotations data
        return render_template_string(html_template, annotations=annotations)
    except Exception as e:
        return f"<p>Error: {str(e)}</p>", 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

